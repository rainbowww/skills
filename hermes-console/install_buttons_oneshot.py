#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HERMES 콘솔 복사/붙여넣기 버튼 - 한 번 붙여넣기(self-contained) 설치기.

이 파일은 node40에서 "파일이 미리 존재하지 않아도" 동작하도록 설계되었다.
사용법(node40, Linux bash):
    python3 - <<'PYEOF'
    ...(이 파일 전체 내용을 붙여넣음)...
    PYEOF

동작:
  1) 18091 포트를 듣는 node 프로세스를 /proc 로 찾는다.
  2) 그 프로세스의 인자/cwd 에서 server.js 실경로를 알아낸다.
     (알려진 경로 /home/mann/fleet-status-board/server.js 를 우선 후보로 둔다)
  3) 이미 버튼(ysc-paste)이 있으면 건드리지 않고 "이미 설치됨" 보고 후 종료.
  4) 백업(server.js.bak) 생성 -> </body> 직전에 버튼 코드 삽입.
  5) 프로세스 재시작 -> HTTP 200 검증.
  6) 검증 실패 시 백업 자동 복구(원상복귀).
표준: 단일 언어(Python 표준 라이브러리만 사용). 외부 다운로드/의존 없음.
"""

import os
import re
import sys
import time
import glob
import signal
import subprocess
import urllib.request

PORT = 18091
KNOWN_SERVER_JS = "/home/mann/fleet-status-board/server.js"

BTN = r"""<script>
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
        var t = box.innerText.replace(/^\s*응답\s*/, '');
        try { await navigator.clipboard.writeText(t); cb.textContent = '✓ 복사됨'; setTimeout(function () { cb.textContent = '📋 복사'; }, 1500); }
        catch (e) { alert('마우스로 긁어 Ctrl+C 하세요'); }
      };
      box.appendChild(cb);
    }
  }
  add(); setInterval(add, 1500);
})();
</script>"""

MARK = "ysc-paste"


def find_pid_on_port(port):
    """/proc 만으로 특정 포트를 LISTEN 하는 PID 를 찾는다(ss/lsof 불필요)."""
    want_hex = "%04X" % port
    inodes = set()
    for path in ("/proc/net/tcp", "/proc/net/tcp6"):
        try:
            with open(path) as f:
                next(f, None)
                for line in f:
                    parts = line.split()
                    if len(parts) < 10:
                        continue
                    local = parts[1]
                    state = parts[3]
                    if state != "0A":  # 0A = LISTEN
                        continue
                    if local.split(":")[-1].upper() == want_hex:
                        inodes.add(parts[9])
        except OSError:
            pass
    if not inodes:
        return None
    for pid_dir in glob.glob("/proc/[0-9]*"):
        pid = os.path.basename(pid_dir)
        fd_dir = os.path.join(pid_dir, "fd")
        try:
            for fd in os.listdir(fd_dir):
                try:
                    target = os.readlink(os.path.join(fd_dir, fd))
                except OSError:
                    continue
                m = re.match(r"socket:\[(\d+)\]", target)
                if m and m.group(1) in inodes:
                    return int(pid)
        except OSError:
            continue
    return None


def server_js_from_pid(pid):
    """프로세스의 cmdline/cwd 에서 server.js 실경로를 추출."""
    if pid is None:
        return None, None
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as f:
            args = f.read().split(b"\x00")
        args = [a.decode("utf-8", "replace") for a in args if a]
    except OSError:
        args = []
    try:
        cwd = os.readlink("/proc/%d/cwd" % pid)
    except OSError:
        cwd = None
    node_bin = args[0] if args else "/usr/bin/node"
    for a in args[1:]:
        if a.endswith(".js"):
            cand = a if os.path.isabs(a) else (os.path.join(cwd, a) if cwd else a)
            if os.path.isfile(cand):
                return cand, node_bin
    if cwd:
        for name in ("server.js", "app.js", "index.js"):
            cand = os.path.join(cwd, name)
            if os.path.isfile(cand):
                return cand, node_bin
    return None, node_bin


def locate_server_js():
    pid = find_pid_on_port(PORT)
    path, node_bin = server_js_from_pid(pid)
    if path:
        return path, node_bin, pid
    if os.path.isfile(KNOWN_SERVER_JS):
        return KNOWN_SERVER_JS, (node_bin or "node"), pid
    for base in ("/home/mann", "/home", "/opt", "/srv", "/root"):
        for cand in glob.glob(base + "/**/server.js", recursive=True):
            try:
                with open(cand, "r", errors="ignore") as f:
                    head = f.read(4000)
                if str(PORT) in head:
                    return cand, (node_bin or "node"), pid
            except OSError:
                continue
    return None, (node_bin or "node"), pid


def restart(node_bin, server_js, pid):
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1.0)
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
        time.sleep(0.5)
    logf = "/tmp/ysc_console.log"
    subprocess.Popen(
        ["setsid", "nohup", node_bin, server_js, str(PORT)],
        stdout=open(logf, "ab"), stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL, close_fds=True,
    )
    time.sleep(1.5)


def http_ok():
    for _ in range(6):
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/" % PORT, timeout=3) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(1.0)
    return False


def main():
    server_js, node_bin, pid = locate_server_js()
    print("PID=%s  node=%s" % (pid, node_bin))
    if not server_js:
        print("server.js: (찾지 못함)")
        print("결과=콘솔서버(server.js %d) 없음 — node40에서 실행했는지 확인" % PORT)
        return 2
    print("server.js: %s" % server_js)

    with open(server_js, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    if MARK in html:
        print("결과=이미 설치됨(중복 없음)")
        return 0

    if "</body>" not in html:
        print("결과=</body> 태그가 없어 삽입 위치를 찾을 수 없음")
        return 3

    bak = server_js + ".bak"
    with open(bak, "w", encoding="utf-8") as f:
        f.write(html)

    new_html = html.replace("</body>", BTN + "\n</body>", 1)
    with open(server_js, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("삽입 완료 (백업: %s)" % bak)

    restart(node_bin, server_js, pid)
    if http_ok():
        print("결과=완료! 콘솔 정상 → 브라우저 새로고침하면 버튼 보임")
        return 0
    with open(bak, "r", encoding="utf-8") as f:
        orig = f.read()
    with open(server_js, "w", encoding="utf-8") as f:
        f.write(orig)
    restart(node_bin, server_js, find_pid_on_port(PORT))
    print("결과=삽입 후 콘솔이 안 떠서 '자동 원상복구'함. 콘솔 안전(원래대로)")
    return 4


if __name__ == "__main__":
    sys.exit(main())
