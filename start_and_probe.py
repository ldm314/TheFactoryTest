import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
import urllib.request

PORT = int(os.environ.get("PROBE_PORT", "8091"))


def sign(body_bytes):
    secret = os.environ.get("WEBHOOK_SECRET", "factory-webhook-secret")
    digest = hmac.new(secret.encode(), body_bytes, hashlib.sha256).hexdigest()
    return "sha256=" + digest


def call(path, headers=None, data=None):
    url = f"http://127.0.0.1:{PORT}{path}"
    req = urllib.request.Request(url, method="POST", data=data)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def main():
    # 1. valid signature -> expect 200
    body = json.dumps({"event": "signed"}).encode()
    status, _ = call("/webhooks", {"X-Signature": sign(body)}, body)
    print("VALID   POST /webhooks ->", status)

    # 2. missing signature -> expect 401
    status, _ = call("/webhooks", {}, body)
    print("NO-HEADER POST /webhooks ->", status)

    # 3. invalid signature -> expect 401
    bad = sign(body + b"tampered")
    status, _ = call("/webhooks", {"X-Signature": bad}, body)
    print("BAD     POST /webhooks ->", status)


if __name__ == "__main__":
    main()
