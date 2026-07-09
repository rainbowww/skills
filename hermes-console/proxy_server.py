#!/usr/bin/env python3
"""
HERMES 콘솔 프록시 서버 — 버튼 주입 버전
실행하면 http://127.0.0.1:18092/ 에서 버튼이 설치된 HERMES 콘솔을 볼 수 있습니다.

사용법:
  python3 proxy_server.py  # 로컬에서 테스트
  또는
  python3 proxy_server.py --upstream http://192.168.0.40:18091  # 실제 node40에 연결
"""

import argparse
import http.server
import re
import sys
import urllib.request
from urllib.parse import urlparse

BUTTON_INJECTION = """<script>
(function () {
  function add() {
    var ta = document.querySelector('textarea');
    if (ta && !(ta.parentNode && ta.parentNode.querySelector('.ysc-paste'))) {
      var pb = document.createElement('button');
      pb.className = 'ysc-paste'; pb.type = 'button';
      pb.textContent = '📋 붙여넣기(초기화)';
      pb.style.cssText = 'margin:6px 4px;padding:8px 14px;border-radius:8px;border:1px solid #4a9eff;background:#1e293b;color:#fff;cursor:pointer;font-size:13px';
      pb.onclick = async function () {
        ta.value = '';
        try {
          ta.value = await navigator.clipboard.readText();
          ta.dispatchEvent(new Event('input', { bubbles: true })); ta.focus();
        } catch (e) { ta.focus(); alert('비웠어요. Ctrl+V 로 붙여넣으세요.'); }
      };
      ta.parentNode.insertBefore(pb, ta.nextSibling);
    }
    var lab = [].slice.call(document.querySelectorAll('*')).filter(function (e) {
      return !e.children.length && e.textContent.trim() === '응답';
    }).pop();
    var box = lab ? lab.parentElement : null;
    if (box && !box.querySelector('.ysc-copy')) {
      if (getComputedStyle(box).position === 'static') box.style.position = 'relative';
      var cb = document.createElement('button');
      cb.className = 'ysc-copy'; cb.type = 'button'; cb.textContent = '📋 복사';
      cb.style.cssText = 'position:absolute;top:6px;right:6px;z-index:99999;padding:6px 12px;border-radius:8px;border:1px solid #4a9eff;background:#1e293b;color:#fff;cursor:pointer;font-size:13px';
      cb.onclick = async function () {
        var t = box.innerText.replace(/^\\s*응답\\s*/, '');
        try { await navigator.clipboard.writeText(t); cb.textContent = '✓ 복사됨'; setTimeout(function () { cb.textContent = '📋 복사'; }, 1500); }
        catch (e) { alert('마우스로 긁어 Ctrl+C 하세요'); }
      };
      box.appendChild(cb);
    }
  }
  add(); setInterval(add, 1500);
})();
</script>"""

DEMO_HTML = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HERMES 콘솔 (버튼 데모)</title>
<style>
  html, body { margin: 0; height: 100%; background: #0e1526; overflow: hidden; }
  .container { width: 100%; height: 100%; display: flex; flex-direction: column; }
  .header { padding: 20px; background: #16203a; border-bottom: 1px solid #26355c; }
  .header h1 { margin: 0; color: #3ecf8e; }
  .header p { margin: 5px 0 0; color: #8a97b5; font-size: 14px; }
  .content { flex: 1; padding: 20px; overflow: auto; }
  textarea { width: 100%; height: 100px; padding: 10px; background: #1e293b; color: #e8edf9; border: 1px solid #4a9eff; border-radius: 8px; font-family: monospace; }
  button { margin: 6px 4px; padding: 8px 14px; border-radius: 8px; border: 1px solid #4a9eff; background: #1e293b; color: #fff; cursor: pointer; font-size: 13px; }
  button:hover { background: #2d3a52; }
  #result { margin-top: 20px; padding: 15px; background: #16203a; border: 1px solid #26355c; border-radius: 8px; min-height: 100px; color: #e8edf9; font-family: monospace; white-space: pre-wrap; word-wrap: break-word; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>HERMES 콘솔</h1>
    <p>✓ 복사/붙여넣기 버튼이 설치된 데모 버전</p>
  </div>
  <div class="content">
    <textarea id="cmd" placeholder="명령 입력"></textarea>
    <button onclick="send()">실행</button>
    <div id="result">응답 대기 중...</div>
  </div>
</div>

<script>
function send() {
  var cmd = document.getElementById('cmd').value;
  document.getElementById('result').textContent = '(데모 모드 — 실제 명령 실행 안 함)\\n입력된 명령: ' + cmd;
}
</script>
""" + BUTTON_INJECTION

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    upstream_url = "http://127.0.0.1:18091"

    def do_GET(self):
        try:
            # 업스트림에서 콘텐츠 가져오기
            upstream_full = self.upstream_url + self.path
            print(f"  → {upstream_full}", file=sys.stderr)

            req = urllib.request.Request(upstream_full, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                content = resp.read().decode('utf-8', errors='replace')
        except Exception as e:
            # 업스트림 연결 불가 → 데모 HTML 제공
            print(f"  ! 업스트림 연결 실패: {e}", file=sys.stderr)
            content = DEMO_HTML

        # </body> 직전에 버튼 코드 주입
        if '</body>' in content:
            content = content.replace('</body>', BUTTON_INJECTION + '</body>')

        # 응답 전송
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def log_message(self, format, *args):
        # 요청 로깅
        print(f"[{self.log_date_time_string()}] {format % args}", file=sys.stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HERMES 콘솔 프록시 (버튼 주입)')
    parser.add_argument('--upstream', default='http://127.0.0.1:18091', help='업스트림 HERMES 콘솔 URL')
    parser.add_argument('--port', type=int, default=18092, help='프록시 포트 (기본: 18092)')
    parser.add_argument('--host', default='127.0.0.1', help='바인드 주소')
    args = parser.parse_args()

    ProxyHandler.upstream_url = args.upstream

    server = http.server.HTTPServer((args.host, args.port), ProxyHandler)
    print(f"HERMES 콘솔 프록시 실행: http://{args.host}:{args.port}/")
    print(f"  업스트림: {args.upstream}")
    print(f"  버튼: 자동 주입 활성화 ✓")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n중단.")
        server.shutdown()
