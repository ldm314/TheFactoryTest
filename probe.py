import hashlib
import hmac
import json
import os
import subprocess
import time
import urllib.request
import urllib.error


PORT = 8091
URL = f"http://127.0.0.1:{PORT}"

READY = False
for _ in range(50):
    try:
        with urllib.request.urlopen(f"{URL}/health", timeout=2) as r:
            if r.status == 200:
                READY = True
                break
    except Exception:
        time.sleep(0.3)

if not READY:
    print("server never came up"); sys.exit(1)


def sign(body_bytes):
    secret = os.environ.get("WEBHOOK_SECRET", "factory-webhook-secret")
    digest = hmac.new(secret.encode(), body_bytes, hashlib.sha256).hexdigest()
    return "sha256=" + digest


def call(path, headers=None, data=None):
    req = urllib.request.Request(f"{URL}{path}", method="POST", data=data)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


body = json.dumps({"event": "signed"}).encode()

status, _ = call("/webhooks", {"X-Signature": sign(body)}, body)
print("VALID   POST /webhooks ->", status)

status, _ = call("/webhooks", {}, body)
print("NO-HEADER POST /webhooks ->", status)

bad = sign(body + b"tampered")
status, _ = call("/webhooks", {"X-Signature": bad}, body)
print("BAD     POST /webhooks ->", status)
