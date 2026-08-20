
(function(){
  var mode = "signin";
  var btn = document.getElementById("btnLogin");
  var link = document.getElementById("linkMode");
  var msg = document.getElementById("loginMsg");
  function setMsg(t, bad){ msg.textContent = t || ""; msg.className = "msg" + (bad ? " bad" : ""); }
  function setMode(m){
    mode = m;
    if(m==="signup"){ btn.textContent="註冊並開始"; link.textContent="已有帳號？登入"; }
    else { btn.textContent="登入"; link.textContent="沒有帳號？註冊"; }
  }
  link.addEventListener("click", function(){ setMode(mode==="signup"?"signin":"signup"); setMsg(""); });

  function login(){
    var u = document.getElementById("inUser").value.trim();
    var p = document.getElementById("inPw").value;
    if(!u){ setMsg("請填寫用戶名", true); return; }
    if(p.length < 6){ setMsg("密碼至少 6 位", true); return; }
    setMsg("處理中…");
    var req = (mode==="signup") ? apiRegister(u,p) : apiLogin(u,p);
    req.then(function(res){
      if(!res.ok){ setMsg((res.j&&res.j.error)||"失敗", true); return; }
      API.token = res.j.token; API.user = u;
      try{ localStorage.setItem("sb_token", res.j.token); localStorage.setItem("sb_user", u); }catch(e){}
      S.uid = "api:" + u;
      S.user = u;
      setMsg("登入成功");
      afterLogin(u);
    }).catch(function(){ setMsg("無法連接伺服器：請檢查網路後重新整理頁面再試（若剛更新部署，請等 1 分鐘）", true); });
  }
  btn.addEventListener("click", login);

  // 自動登入：localStorage 有 token 就直接進 dashboard（autoRegenerate 會背景升級本地計畫）
  if(API.token && API.user){
    setMsg("自動登入中…");
    afterLogin(API.user).catch(function(){ setMsg("自動登入失敗，請重新登入", true); });
  }

  var out = document.getElementById("btnLogout");
  if(out){
    out.addEventListener("click", function(){
      try{ window.saveAll(); }catch(e){}
      apiLogout().catch(function(){});
      API.token = null;
      try{ localStorage.removeItem("sb_token"); localStorage.removeItem("sb_user"); }catch(e){}
      setMode("signin"); setMsg("");
      window.S = {}; window.go("login");
    });
  }
})();
