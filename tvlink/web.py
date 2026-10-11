"""Tiny web remote (stdlib only). Open http://127.0.0.1:8765 on the laptop."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>TV Link</title>
<style>
body{font-family:system-ui,sans-serif;background:#111;color:#eee;max-width:360px;margin:24px auto;padding:0 16px}
h1{font-size:18px;margin:0 0 12px}select,button{font-size:16px;border-radius:10px;border:0;padding:14px;width:100%}
select{background:#222;color:#eee;margin-bottom:12px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
button{background:#2a2a2a;color:#eee;cursor:pointer}button:active{background:#3b82f6}
button.power{background:#b91c1c;grid-column:span 2}#s{margin-top:12px;font-size:13px;color:#9ca3af;min-height:18px}
</style></head><body><h1>TV Link</h1><select id="p"></select><div class="grid" id="g"></div><div id="s"></div>
<script>
const $=id=>document.getElementById(id);
async function load(){const r=await (await fetch('/api/state')).json();
$('p').innerHTML=r.profiles.map(p=>`<option ${p==r.active?'selected':''}>${p}</option>`).join('');
$('g').innerHTML=r.buttons.map(b=>`<button class="${b=='power'?'power':''}" data-b="${b}">${b.replace('_',' ')}</button>`).join('');}
$('g').onclick=async e=>{const b=e.target.dataset.b;if(!b)return;
const r=await fetch('/api/send',{method:'POST',body:JSON.stringify({button:b})});
$('s').textContent=r.ok?'sent '+b:'error: '+(await r.json()).error;};
$('p').onchange=async()=>{await fetch('/api/profile',{method:'POST',body:JSON.stringify({profile:$('p').value})});load();};
load();
</script></body></html>"""


def make_server(storage, device, host="127.0.0.1", port=8765):
    lock = threading.Lock()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _json(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/":
                body = PAGE.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif self.path == "/api/state":
                self._json(200, {"active": storage.active, "profiles": storage.profiles(),
                                 "buttons": storage.buttons()})
            else:
                self._json(404, {"error": "not found"})

        def do_POST(self):
            try:
                n = int(self.headers.get("Content-Length", 0))
                req = json.loads(self.rfile.read(n) or b"{}")
                with lock:
                    if self.path == "/api/send":
                        device.send(storage.get_code(req["button"]))
                    elif self.path == "/api/profile":
                        storage.set_active(req["profile"])
                    else:
                        return self._json(404, {"error": "not found"})
                self._json(200, {"ok": True})
            except Exception as e:  # report to the UI
                self._json(400, {"error": str(e)})

    return ThreadingHTTPServer((host, port), H)
