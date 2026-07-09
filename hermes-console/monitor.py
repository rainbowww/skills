#!/usr/bin/env python3
# 관제탑 - 자원 모니터 (읽기전용, 안전). 표준 라이브러리만.
# CPU/메모리/부하/상태를 웹으로 보여준다. 명령 실행 없음(RCE 없음) = 안전.
# 실행: HERMES_HOST=0.0.0.0 python3 monitor.py  → http://<서버>:8790/
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = os.environ.get("HERMES_HOST", "127.0.0.1")
PORT = int(os.environ.get("HERMES_PORT", "8790"))
_last = {"i": 0, "t": 0}


def _cpu():
    def rd():
        n = [int(x) for x in open("/proc/stat").readline().split()[1:]]
        return n[3] + (n[4] if len(n) > 4 else 0), sum(n)
    i1, t1 = rd()
    if _last["t"] == 0:
        time.sleep(0.1)
        i2, t2 = rd()
    else:
        i2, t2 = i1, t1
        i1, t1 = _last["i"], _last["t"]
    _last["i"], _last["t"] = i2, t2
    d = t2 - t1
    return 0.0 if d <= 0 else max(0.0, min(100.0, (1 - (i2 - i1) / d) * 100))


def _mem():
    m = {}
    for line in open("/proc/meminfo"):
        k, _, v = line.partition(":")
        if v.strip():
            m[k.strip()] = int(v.split()[0])
    tot = m.get("MemTotal", 1)
    av = m.get("MemAvailable", m.get("MemFree", 0))
    return round((1 - av / tot) * 100, 1), round(tot / 1024), round(av / 1024)


def _info():
    c = round(_cpu(), 1)
    mp, mt, ma = _mem()
    st = "critical" if c >= 85 or mp >= 90 else "busy" if c >= 60 or mp >= 75 else "ok"
    try:
        ld = round(os.getloadavg()[0], 2)
    except Exception:
        ld = 0
    return {"cpu": c, "mem": mp, "mem_total_mb": mt, "mem_avail_mb": ma,
            "load": ld, "state": st, "ready": st == "ok"}


PAGE = """<!doctype html><meta charset="utf-8"><title>관제탑</title>
<body style="font-family:system-ui;background:#0e1526;color:#e8edf9;text-align:center;padding:30px">
<h1>관제탑 · 시스템 자원</h1><div id="b" style="font-size:20px">불러오는 중...</div>
<script>
async function p(){try{let d=await(await fetch('/sysinfo',{cache:'no-store'})).json();
let c=d.state=='ok'?'#3ecf8e':d.state=='busy'?'#f5b445':'#ff5c5c';
document.getElementById('b').innerHTML='<div style="font-size:64px;color:'+c+'">'+d.cpu+'%<span style="font-size:20px"> CPU</span></div>메모리 '+d.mem+'% ('+d.mem_avail_mb+' / '+d.mem_total_mb+' MB) · 부하 '+d.load+'<div style="margin-top:12px;color:'+c+'">상태: '+(d.ready?'정상 · 실행 가능':'대기 · 회복 중')+'</div>';
}catch(e){document.getElementById('b').textContent='연결 안됨';}}
p();setInterval(p,2000);
</script>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/sysinfo"):
            b = json.dumps(_info(), ensure_ascii=False).encode()
            ct = "application/json"
        else:
            b = PAGE.encode()
            ct = "text/html"
        self.send_response(200)
        self.send_header("Content-Type", ct + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass


print("관제탑 자원 모니터 실행: http://%s:%d" % (HOST, PORT))
ThreadingHTTPServer((HOST, PORT), H).serve_forever()
