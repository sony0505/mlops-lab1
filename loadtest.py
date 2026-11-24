"""Simple load generator (equivalent of `hey -z 60s -c 50 -m POST ...`).

Usage: python loadtest.py [--url URL] [--duration 60] [--concurrency 50]
"""
import argparse
import json
import threading
import time
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://localhost:8080/predict")
parser.add_argument("--duration", type=int, default=60, help="seconds")
parser.add_argument("--concurrency", type=int, default=50)
args = parser.parse_args()

body = json.dumps({"instances": [[5.1, 3.5, 1.4, 0.2]]}).encode()
stop_at = time.time() + args.duration
lock = threading.Lock()
stats = {"ok": 0, "err": 0}


def worker():
    while time.time() < stop_at:
        req = urllib.request.Request(
            args.url, data=body, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
            key = "ok"
        except Exception:
            key = "err"
        with lock:
            stats[key] += 1


threads = [threading.Thread(target=worker) for _ in range(args.concurrency)]
start = time.time()
for t in threads:
    t.start()
for t in threads:
    t.join()
elapsed = time.time() - start
total = stats["ok"] + stats["err"]
print(f"Requests: {total}  OK: {stats['ok']}  Errors: {stats['err']}")
print(f"Duration: {elapsed:.1f}s  Requests/sec: {total / elapsed:.1f}")
