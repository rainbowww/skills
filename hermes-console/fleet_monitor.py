#!/usr/bin/env python3
# 함대 상태판 - PocketBase(bus)의 heartbeat를 읽어 각 노드의 생존/사망을 보여준다.
# 읽기전용, 안전(명령 실행 없음). 노드에서 박동이 끊기면 즉시 빨강으로 표시.
# 실행: HERMES_HOST=0.0.0.0 python3 fleet_monitor.py  → http://<서버>:8791/
import calendar
import json
import os
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = os.environ.get("HERMES_HOST", "127.0.0.1")
PORT = int(os.environ.get("HERMES_PORT", "8791"))
BUS = os.environ.get("HERMES_BUS", "http://127.0.0.1:6609")
DEAD_SEC = int(os.environ.get("DEAD_SEC", "60"))  # 이 초 넘게 소식 없으면 '사망'


def _age(created, now):
    """PocketBase created(UTC)를 epoch로 바꿔 경과초를 구한다."""
    try:
        s = created.replace("T", " ").replace("Z", "").split(".")[0]
        t = calendar.timegm(time.strptime(s, "%Y-%m-%d %H:%M:%S"))
        return max(0.0, now - t)
    except Exception:
        return None


def fleet():
    url = BUS + "/api/collections/status/records?perPage=200&sort=-created"
    try:
        data = json.loads(urllib.request.urlopen(url, timeout=10).read().decode())
    except Exception as e:
        return {"error": "PocketBase(bus) 접속 실패: %s" % e, "bus": BUS, "nodes": []}
    now = time.time()
    latest = {}
    for it in data.get("items", []):
        node = it.get("node", "")
        if not node.startswith("node"):      # CMD:/RES: 제외 — heartbeat만
            continue
        if node in latest:                   # -created 정렬이라 첫 등장이 최신
            continue
        latest[node] = it
    nodes = []
    for node, it in sorted(latest.items()):
        age = _age(it.get("created", ""), now)
        nodes.append({
            "node": node,
            "ip": it.get("ip", ""),
            "load": it.get("load", ""),
            "age": round(age) if age is not None else None,
            "alive": (age is not None and age < DEAD_SEC),
        })
    dead = [n["node"] for n in nodes if not n["alive"]]
    return {"error": None, "bus": BUS, "dead_sec": DEAD_SEC,
            "alive_count": sum(1 for n in nodes if n["alive"]),
            "dead_count": len(dead), "dead": dead, "nodes": nodes}


PAGE = """<!doctype html><meta charset="utf-8"><title>함대 상태판</title>
<body style="font-family:system-ui;background:#0e1526;color:#e8edf9;padding:24px;margin:0">
<h1 style="margin:0 0 4px">함대 상태판</h1>
<div id="sum" style="color:#8a97b5;font-size:14px;margin-bottom:16px">불러오는 중...</div>
<div id="grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px"></div>
<script>
function fmtAge(s){if(s==null)return '기록없음';if(s<60)return s+'초 전';if(s<3600)return Math.floor(s/60)+'분 전';return Math.floor(s/3600)+'시간 전';}
async function p(){
 let d;try{d=await(await fetch('/fleet',{cache:'no-store'})).json();}catch(e){document.getElementById('sum').textContent='상태판 서버 연결 안됨';return;}
 let sum=document.getElementById('sum'),grid=document.getElementById('grid');
 if(d.error){sum.innerHTML='<span style=color:#ff5c5c>⚠ '+d.error+'</span>';grid.innerHTML='';return;}
 sum.innerHTML='<b style=color:#3ecf8e>정상 '+d.alive_count+'</b> · <b style=color:#ff5c5c>사망 '+d.dead_count+'</b>'+(d.dead.length?' → <b style=color:#ff5c5c>'+d.dead.join(', ')+'</b>':'')+' · '+d.dead_sec+'초 무응답=사망';
 grid.innerHTML=d.nodes.map(n=>{let c=n.alive?'#3ecf8e':'#ff5c5c';return '<div style="background:#16203a;border:1px solid '+(n.alive?'#26355c':'#ff5c5c')+';border-radius:12px;padding:14px"><div style="font-size:18px;font-weight:700;color:'+c+'">'+(n.alive?'🟢':'🔴')+' '+n.node+'</div><div style="color:#8a97b5;font-size:13px;margin-top:6px">'+n.ip+'</div><div style="color:#8a97b5;font-size:13px">부하 '+(n.load||'?')+'</div><div style="color:'+c+';font-size:13px;margin-top:4px">'+fmtAge(n.age)+'</div></div>';}).join('')||'<div style=color:#8a97b5>노드 기록이 없어요</div>';
}
p();setInterval(p,3000);
</script>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/fleet"):
            b = json.dumps(fleet(), ensure_ascii=False).encode()
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


print("함대 상태판 실행: http://%s:%d  (bus=%s)" % (HOST, PORT, BUS))
ThreadingHTTPServer((HOST, PORT), H).serve_forever()
