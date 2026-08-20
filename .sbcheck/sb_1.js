
/* ---- 多用戶 API（PostgreSQL 伺服器端；token 存 localStorage，可跨裝置同步） ---- */
var API={token:null,user:null};
try{ API.token=localStorage.getItem('sb_token')||null; API.user=localStorage.getItem('sb_user')||null; }catch(e){}
function apiFetch(method,path,body,signal){
  var opt={method:method,headers:{'Content-Type':'application/json'}};
  if(signal)opt.signal=(signal.signal||signal); // 相容 AbortController（舊呼叫）與 AbortSignal
  if(API.token)opt.headers['Authorization']='Bearer '+API.token;
  if(body!==undefined)opt.body=JSON.stringify(body);
  return fetch(path,opt).then(function(r){ return r.json().then(function(j){ return {ok:r.ok,status:r.status,j:j}; }); });
}
function apiRegister(u,p){ return apiFetch('POST','/api/register',{username:u,password:p}); }
function apiLogin(u,p){ return apiFetch('POST','/api/login',{username:u,password:p}); }
function apiLogout(){ return apiFetch('POST','/api/logout'); }
function apiState(){ return apiFetch('GET','/api/state'); }
function apiSaveAnswers(a){ return apiFetch('PUT','/api/answers',{answers:a}); }
function apiSaveSnapshot(s){ return apiFetch('PUT','/api/snapshot',{snapshot:s}); }
function apiSavePlan(p,s){ return apiFetch('PUT','/api/plan',{plan:p,schedule:s}); }

var INPUT_IDS=['inParent','inBaby','inBirth','inNote'];
var SELECT_IDS=['E1','E3','E4'];
var CHIP_KEYS=['tier','goal','freq','screen'];
function collectAnswers(){
  var pairs=[];
  INPUT_IDS.forEach(function(id){var e=document.getElementById(id);if(e)pairs.push([id,e.value]);});
  SELECT_IDS.forEach(function(id){var e=document.getElementById(id);if(e)pairs.push([id,e.value]);});
  CHIP_KEYS.forEach(function(k){if(S[k]!==undefined)pairs.push([k,typeof S[k]==='object'?JSON.stringify(S[k]):String(S[k])]);});
  (window.PATHWAYS||[]).forEach(function(p){p.questions.forEach(function(q){if(S[q[0]]!==undefined)pairs.push([q[0],String(S[q[0]])]);});});
  return pairs;
}
function answersObject(){ var o={}; collectAnswers().forEach(function(p){ o[p[0]]=p[1]; }); return o; }
function saveAnswers(){ if(!S.user)return; apiSaveAnswers(answersObject()).catch(function(){}); }
function saveSnapshot(){
  if(!S.user||!S.plan)return;
  var snap=JSON.stringify({plan:S.plan,phys:S.phys,level:S.level,mistakes:S.mistakes,progress:S.progress,script:S.script,months:S.months,tier:S.tier,freq:S.freq,screen:S.screen});
  apiSaveSnapshot(JSON.parse(snap)).catch(function(){});
}
function savePlan(){
  if(!S.user||!S.teachingPlan)return;
  var sched=S.schedule||{current_week:0,current_lesson:0,completed:[]};
  var p=JSON.parse(JSON.stringify(S.teachingPlan));
  if(S.plan_source)p._src=S.plan_source;   // 來源標記：deepseek｜local（重新整理後仍顯示正確狀態）
  apiSavePlan(p,sched).catch(function(){});
}
function saveAll(){ saveAnswers(); saveSnapshot(); savePlan(); }

/* ---- 載入：伺服器端 state → S（與 SQLite 版同邏輯，只是資料來源換成 API） ---- */
function applyAnswers(ans){
  if(!ans)return;
  Object.keys(ans).forEach(function(k){var v=ans[k];
    if(SELECT_IDS.indexOf(k)>=0){var e=document.getElementById(k);if(e)e.value=v;return;}
    if(INPUT_IDS.indexOf(k)>=0)return;
    try{S[k]= (v&&(v[0]==='['||v[0]==='{'))?JSON.parse(v):v;}catch(e){S[k]=v;}
  });
  document.querySelectorAll('.opt').forEach(function(o){
    var v=S[o.dataset.name]; if(v===undefined||v===null)return;
    if(o.dataset.multi){(v||[]).forEach(function(x){o.querySelectorAll('.chip').forEach(function(c){if(c.dataset.v===x)c.classList.add('on');});});}
    else{o.querySelectorAll('.chip').forEach(function(c){if(c.dataset.v===v)c.classList.add('on');});}
  });
}
function loadAnswers(ans){
  if(!ans)return;
  Object.keys(ans).forEach(function(k){var v=ans[k];
    if(INPUT_IDS.indexOf(k)>=0){var e=document.getElementById(k);if(e)e.value=v;return;}
  });
  var b=document.getElementById('inBirth');
  if(b&&b.value) renderAge(); // 依出生日期重建四維度題目（renderAge 會設 S.months）
  applyAnswers(ans);
}
function loadPlan(p){
  if(!p||!p.plan)return null;
  var plan=p.plan;
  if(plan._src){ S.plan_source=plan._src; delete plan._src; } // 來源標記；舊計畫（無標記）→ 不顯示警告
  if(plan.weeks) plan.weeks.forEach(function(w){ if(w.focus) w.focus=w.focus.replace(/^第\s*\d+\s*週：/,''); }); // 遷移舊格式：移除內嵌「第 N 週：」前綴
  return {plan:plan,schedule:p.schedule||{current_week:0,current_lesson:0,completed:[]}};
}
function afterLogin(user){
  S.user=user;
  return apiState().then(function(res){
    if(!res.ok){ go('login'); if(res.status===401){ API.token=null; try{localStorage.removeItem('sb_token');}catch(e){} } return; }
    var st=res.j||{};
    var ans=st.answers||{};
    if(Object.keys(ans).length){
      loadAnswers(ans);                       // 已填過：載入答案
      if(!computeAssessment()){ go('questionnaire'); return; } // 答案不完整（缺出生日期）
      var saved=loadPlan(st.plan);
      if(saved){
        S.teachingPlan=saved.plan;            // 計畫只生成一次：登入直接沿用
        S.schedule=saved.schedule||{current_week:0,current_lesson:0,completed:[]};
        renderPlan(); renderMistakes(); renderSched();
        go('dash'); tab('plan');
        return;
      }
      return generateTeachingPlan().then(function(){ // 舊帳號無計畫 → 生成並保存
        savePlan();
        renderPlan(); renderMistakes(); renderSched();
        go('dash'); tab('plan');
      });
    }
    go('questionnaire');                      // 新帳號：填問卷
  }).catch(function(err){ go('login'); });    // 伺服器連不上 → 回登入
}
