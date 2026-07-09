/* 자막 변환기 서비스 워커 — PWA(안드로이드 설치형 앱) 껍데기 캐시.
   철학: 껍데기(HTML/CSS/JS/아이콘)는 한 번 캐시해 재사용, 실제 변환·진행률(API)은
   항상 실시간 네트워크. 내용만 바뀌면 CACHE 버전만 올리면 된다. */
const CACHE = "subtitle-converter-v1";
const SHELL = [
  "./",
  "./index.html",
  "./css/style.css",
  "./js/app.js",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // API(변환/진행률)는 캐시 금지 — 항상 실시간이어야 함
  if (url.pathname.startsWith("/api/")) return;
  // 같은 출처의 앱 껍데기만 캐시 우선(오프라인에서도 화면은 뜨게)
  if (url.origin !== self.location.origin) return;
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      // 새로 받은 껍데기 리소스는 캐시에 갱신(내용 개선 시 자동 반영)
      const copy = res.clone();
      caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
      return res;
    }).catch(() => hit))
  );
});
