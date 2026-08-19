// StudyBuddy 原型 Firebase 組態
// 以 classic script 形式掛載到 window.FIREBASE_CONFIG，供 prototype.html 的 auth 腳本直接讀取。
// （Firebase 網頁 apiKey 本就設計為公開、放置於客戶端；安全性由 Firebase Security Rules 與 API 金鑰限制保障，非靠保密。）
window.FIREBASE_CONFIG = {
  apiKey: "AIzaSyA0NRJ7gNDRJGlSi49WAL8paVK014hqCGI",
  authDomain: "studybuddy-cef0f.firebaseapp.com",
  projectId: "studybuddy-cef0f",
  storageBucket: "studybuddy-cef0f.firebasestorage.app",
  messagingSenderId: "749026404304",
  appId: "1:749026404304:web:5d048b02de9740bbd57bd5",
  measurementId: "G-TL576CFG8Z"
};
