/* 자막 변환기 프런트엔드 로직
   항목 3(변환 호출)·6(미리보기)·7(TXT 다운로드)·8(로딩)·9(검색+자동 스크롤) */
"use strict";

const $ = (id) => document.getElementById(id);
const urlInput = $("url-input");
const tsToggle = $("ts-toggle");
const convertBtn = $("convert-btn");
const errorBox = $("error-box");
const loading = $("loading");
const loadingStage = $("loading-stage");
const progressBar = $("progress-bar");
const progressPct = $("progress-pct");
const loadingDetail = $("loading-detail");
const loadingElapsed = $("loading-elapsed");
const cancelBtn = $("cancel-btn");
const result = $("result");
const videoTitle = $("video-title");
const preview = $("preview");
const searchInput = $("search-input");
const searchCount = $("search-count");
const downloadBtn = $("download-btn");

let rawText = "";   // 변환 원문 (다운로드용)
let title = "자막";
let pollTimer = null;   // 진행률 폴링 타이머
let cancelled = false;

/* ---------- 항목 3+8: 변환 요청 + 실시간 진행률 ---------- */
async function convert() {
  const url = urlInput.value.trim();
  errorBox.hidden = true;
  if (!url) { showError("유튜브 영상 주소를 입력해 주세요."); return; }

  cancelled = false;
  convertBtn.disabled = true;
  setProgress("변환을 시작합니다", 0, "잠시만요…", 0);
  loading.hidden = false;

  try {
    const res = await fetch("/api/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, timestamps: tsToggle.checked }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `변환 요청 실패 (HTTP ${res.status})`);
    if (!data.job_id) throw new Error("작업 시작에 실패했습니다.");
    pollProgress(data.job_id);   // 이제부터 단계·%·상세를 폴링으로 갱신
  } catch (e) {
    endLoading();
    showError(e.message);
  }
}

/* ---------- 진행률 폴링: 0.7초마다 서버 상태를 읽어 화면 갱신 ---------- */
function pollProgress(jobId) {
  const tick = async () => {
    if (cancelled) return;
    try {
      const res = await fetch(`/api/progress/${jobId}`);
      const p = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(p.error || "진행 상태를 읽지 못했습니다.");

      setProgress(p.stage, p.percent, p.detail, p.elapsed);

      if (p.done) {
        if (p.error) { endLoading(); showError(p.error); return; }
        const r = p.result || {};
        rawText = r.text || "";
        title = r.title || "자막";
        videoTitle.textContent = title;
        renderPreview(rawText);
        result.hidden = false;
        searchInput.value = "";
        searchCount.textContent = "";
        endLoading();
        result.scrollIntoView({ behavior: "smooth", block: "start" });
        return;
      }
      pollTimer = setTimeout(tick, 700);
    } catch (e) {
      // 네트워크 일시 오류면 몇 번은 계속 시도(끊지 않음)
      pollTimer = setTimeout(tick, 1200);
    }
  };
  tick();
}

function setProgress(stage, percent, detail, elapsed) {
  const pct = Math.max(0, Math.min(100, Math.round(percent || 0)));
  loadingStage.textContent = stage || "진행 중";
  progressBar.style.width = pct + "%";
  progressPct.textContent = pct + "%";
  loadingDetail.textContent = detail || "";
  const secs = Math.round(elapsed || 0);
  const mmss = secs >= 60 ? `${Math.floor(secs / 60)}분 ${secs % 60}초` : `${secs}초`;
  loadingElapsed.textContent = `경과 ${mmss} · 영상 길이에 따라 수 분 걸릴 수 있어요`;
}

function endLoading() {
  if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
  loading.hidden = true;
  convertBtn.disabled = false;
}

function cancelConvert() {
  cancelled = true;
  endLoading();
  showError("변환을 취소했습니다. 다시 시도할 수 있어요.");
}

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.hidden = false;
}

/* ---------- 항목 6: 미리보기 렌더 ---------- */
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}
function renderPreview(text, keyword = "") {
  let html = escapeHtml(text);
  if (keyword) {
    const safe = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    html = html.replace(new RegExp(safe, "gi"), (m) => `<mark>${m}</mark>`);
  }
  preview.innerHTML = html;
}

/* ---------- 항목 9: 실시간 검색 + 자동 스크롤 ---------- */
searchInput.addEventListener("input", () => {
  const kw = searchInput.value.trim();
  renderPreview(rawText, kw);
  if (!kw) { searchCount.textContent = ""; return; }
  const marks = preview.querySelectorAll("mark");
  searchCount.textContent = marks.length ? `${marks.length}건` : "결과 없음";
  if (marks.length) {
    marks[0].classList.add("current");
    marks[0].scrollIntoView({ behavior: "smooth", block: "center" });
  }
});

/* ---------- 항목 7: TXT 파일 다운로드 (Blob + <a download>) ---------- */
function downloadTxt() {
  const body = `# ${title}\n\n${rawText}\n`;
  const blob = new Blob([body], { type: "text/plain;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `${title.replace(/[\\/:*?"<>|]/g, "_").slice(0, 80)}.txt`;
  a.click();
  URL.revokeObjectURL(a.href);
}

/* ---------- 접근성: 글자 크기 조절 ---------- */
let fontRem = 1.0;
function setFont(delta) {
  fontRem = Math.min(1.6, Math.max(0.8, fontRem + delta));
  preview.style.setProperty("--preview-font", `${fontRem}rem`);
  preview.style.fontSize = `${fontRem}rem`;
}

/* ---------- 이벤트 바인딩 (키보드 조작 지원) ---------- */
convertBtn.addEventListener("click", convert);
urlInput.addEventListener("keydown", (e) => { if (e.key === "Enter") convert(); });
cancelBtn.addEventListener("click", cancelConvert);
downloadBtn.addEventListener("click", downloadTxt);
$("font-plus").addEventListener("click", () => setFont(+0.1));
$("font-minus").addEventListener("click", () => setFont(-0.1));
tsToggle.addEventListener("change", () =>
  tsToggle.setAttribute("aria-checked", String(tsToggle.checked)));

/* ---------- 📱 폰으로 열기: 폰 접속 모드면 QR 카드 표시 ---------- */
async function initPhoneCard() {
  try {
    const res = await fetch("/api/lan");
    const d = await res.json().catch(() => ({}));
    if (!d.enabled || !d.url) return;   // PC 전용 모드면 카드 숨김 유지
    const qrBox = $("qr-box");
    if (d.qr) qrBox.innerHTML = d.qr;    // 서버가 만든 신뢰된 SVG
    const link = $("phone-url-link");
    link.textContent = d.url;
    link.href = d.url;
    $("phone-card").hidden = false;
  } catch (e) { /* 실패해도 웹앱은 그대로 동작 */ }
}
initPhoneCard();
