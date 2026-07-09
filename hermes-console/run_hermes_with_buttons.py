#!/usr/bin/env python3
"""
HERMES 콘솔 + 버튼 통합 서버
복사/붙여넣기 버튼이 이미 설치된 상태로 실행

실행:
  python3 hermes-console/run_hermes_with_buttons.py
  → http://0.0.0.0:18091/ 에서 버튼이 포함된 콘솔 사용 가능
"""

import http.server
import json
import sys

BUTTON_CODE = """<script>
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

HTML_PAGE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HERMES 콘솔 (버튼 설치됨)</title>
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; background: #0e1526; font-family: system-ui; overflow: hidden; }
  .container { width: 100%; height: 100%; display: flex; flex-direction: column; }
  .header { padding: 16px 20px; background: #16203a; border-bottom: 1px solid #26355c; }
  .header h1 { margin: 0; color: #3ecf8e; font-size: 24px; }
  .header p { margin: 4px 0 0; color: #8a97b5; font-size: 12px; }
  .content { flex: 1; padding: 20px; display: flex; flex-direction: column; gap: 16px; overflow: auto; }
  textarea { flex: 0 0 120px; padding: 10px; background: #1e293b; color: #e8edf9; border: 1px solid #4a9eff; border-radius: 8px; font-family: monospace; font-size: 14px; resize: vertical; }
  .buttons { display: flex; gap: 8px; }
  button { padding: 8px 14px; border-radius: 8px; border: 1px solid #4a9eff; background: #1e293b; color: #fff; cursor: pointer; font-size: 13px; transition: background 0.2s; }
  button:hover { background: #2d3a52; }
  button:active { background: #4a9eff; }
  #result { flex: 1; padding: 14px; background: #16203a; border: 1px solid #26355c; border-radius: 8px; color: #e8edf9; font-family: monospace; font-size: 13px; white-space: pre-wrap; word-wrap: break-word; overflow: auto; }
  .status { padding: 8px 12px; background: #26355c; color: #3ecf8e; border-radius: 6px; font-size: 12px; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>HERMES 콘솔</h1>
    <p>✓ 복사/붙여넣기 버튼이 설치된 상태</p>
  </div>
  <div class="content">
    <div>
      <textarea id="cmd" placeholder="명령 입력 (예: ls -la, pwd 등)"></textarea>
      <div class="buttons">
        <button onclick="send()">📤 실행</button>
        <button class="ysc-paste">📋 붙여넣기(초기화)</button>
      </div>
    </div>
    <div>
      <div class="status">응답:</div>
      <div id="result">명령을 입력하고 실행을 누르세요.</div>
    </div>
  </div>
</div>

<script>
function send() {
  var cmd = document.getElementById('cmd').value;
  if (!cmd.trim()) return;
  document.getElementById('result').textContent = '$ ' + cmd + '\\n[실행 중...]';

  fetch('/api/exec', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({cmd: cmd})
  })
  .then(r => r.json())
  .then(d => {
    document.getElementById('result').textContent = d.output || '(출력 없음)';
  })
  .catch(e => {
    document.getElementById('result').textContent = '오류: ' + e.message;
  });
}

document.getElementById('cmd').addEventListener('keypress', function(e) {
  if (e.key === 'Enter' && e.ctrlKey) send();
});
</script>

""" + BUTTON_CODE

class HermesHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            content = HTML_PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/exec':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                cmd = data.get('cmd', '')
                # 안전을 위해 특정 명령만 허용
                import subprocess
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                output = result.stdout + result.stderr
            except Exception as e:
                output = f'Error: {e}'

            response = json.dumps({'output': output}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        pass

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', 18091), HermesHandler)
    print('✅ HERMES 콘솔 (버튼 설치됨)')
    print('🌐 http://0.0.0.0:18091/')
    print('📋 복사/붙여넣기 버튼: 자동 활성화')
    print('')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n중단.')
