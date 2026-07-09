/* 자막 변환기 프런트엔드 로직
   항목 3(변환 호출)·6(미리보기)·7(TXT 다운로드)·8(로딩)·9(검색+자동 스크롤) */
"use strict";

const $ = (id) => document.getElementById(id);
const urlInput = $("url-input");
const tsToggle = $("ts-toggle");
const convertBtn = $("convert-btn");
const errorBox = $("error-box");
const loading = $("loading");
const result = $("result");
const videoTitle = $("video-title");
const preview = $("preview");
const searchInput = $("search-input");
const searchCount = $("search-count");
const downloadBtn = $("download-btn");

let rawText = "";   // 변환 원문 (다운로드용)
let title = "자막";

/* ---------- 항목 3+8: 변환 요청 + 로딩 ---------- */
async function convert() {
  const url = urlInput.value.trim();
  errorBox.hidden = true;
  if (!url) { showError("유튜브 영상 주소를 입력해 주세요."); return; }

  convertBtn.disabled = true;
  loading.hidden = false;
  try {
    const res = await fetch("/api/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, timestamps: tsToggle.checked }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `변환 실패 (HTTP ${res.status})`);

    rawText = data.text || "";
    title = data.title || "자막";
    videoTitle.textContent = title;
    renderPreview(rawText);
    result.hidden = false;
    searchInput.value = "";
    searchCount.textContent = "";
    result.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (e) {
    showError(e.message);
  } finally {
    loading.hidden = true;
    convertBtn.disabled = false;
  }
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
downloadBtn.addEventListener("click", downloadTxt);
$("font-plus").addEventListener("click", () => setFont(+0.1));
$("font-minus").addEventListener("click", () => setFont(-0.1));
tsToggle.addEventListener("change", () =>
  tsToggle.setAttribute("aria-checked", String(tsToggle.checked)));
