import os, sys
try:
    from webhooks import store
    print("store OK; DATABASE_URL =", repr(os.environ.get("DATABASE_URL")))
except Exception as e:
    print("IMPORT FAILED:", type(e).__name__, e)
