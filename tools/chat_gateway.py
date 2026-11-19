"""ServMod chat gateway - runs on the owner's PC next to Ollama. Only POST /api/chat, only with the shared key,
only the allowed model, limited output. Listens on 127.0.0.1:11500; a Cloudflare Tunnel points llm.servmod.com here.
Key: file chat_key.txt next to this script (made by chat_pc_setup.ps1, never in the repo)."""
import json, os, sys, hmac, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
HERE = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(HERE, "chat_key.txt"), encoding="utf-8").read().strip()
MODEL = os.environ.get("CHAT_MODEL", "qwen2.5:14b")
OLLAMA = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")

class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        b = json.dumps(obj).encode(); self.send_response(code)
        self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        self._send(200 if self.path == "/health" else 404, {"ok": True})
    def do_POST(self):
        if self.path != "/api/chat": return self._send(404, {"error": "not found"})
        if not hmac.compare_digest(self.headers.get("X-Chat-Key", ""), KEY): return self._send(403, {"error": "forbidden"})
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n <= 0 or n > 120000: return self._send(413, {"error": "size"})
            d = json.loads(self.rfile.read(n))
            d["model"] = MODEL; d["stream"] = False
            o = d.get("options") or {}
            d["options"] = {"temperature": min(float(o.get("temperature", 0.2)), 0.7), "num_ctx": min(int(o.get("num_ctx", 8192)), 12288), "num_predict": min(int(o.get("num_predict", 300)), 400)}
            req = urllib.request.Request(OLLAMA + "/api/chat", data=json.dumps(d).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r: self._send(200, json.loads(r.read()))
        except Exception as e:
            self._send(502, {"error": str(e)[:200]})
    def log_message(self, *a): pass

if __name__ == "__main__":
    print(f"chat gateway on 127.0.0.1:11500 -> {OLLAMA}, model {MODEL}"); ThreadingHTTPServer(("127.0.0.1", 11500), H).serve_forever()
