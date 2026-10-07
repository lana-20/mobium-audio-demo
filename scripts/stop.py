#!/usr/bin/env python3
"""Stops a capture and keeps both halves of Mobium's answer: prints the
message, as `mobium audio stop` would, and writes the structured result —
timeline, volumes, interruptions — as JSON. The CLI prints one or the other,
and a capture can be stopped once, so this asks through `mobium pipe`, the
channel every client uses.

    scripts/stop.py <device> <out.json> [path.wav]

MOBIUM names the binary (default: mobium on PATH). Without a path — on a
phone, which captures no sound — nothing is saved but the JSON.
"""
import json
import os
import subprocess
import sys


def main(device, out, wav):
    binary = os.environ.get("MOBIUM", "mobium").split()
    proc = subprocess.Popen(binary + ["pipe", "--device", device], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, text=True)

    def ask(n, method, params):
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": n, "method": method, "params": params}) + "\n")
        proc.stdin.flush()
        for line in proc.stdout:
            msg = json.loads(line)
            if msg.get("id") == n:
                return msg
        sys.exit("mobium pipe ended without answering")

    ask(1, "initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                          "clientInfo": {"name": "mobium-audio-demo", "version": "1"}})
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    args = {"action": "stop"}
    if wav:
        args["path"] = os.path.abspath(wav)
    res = ask(2, "tools/call", {"name": "app_audio", "arguments": args}).get("result", {})
    proc.stdin.close()
    proc.wait(timeout=30)
    text = "\n".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text").strip()
    print(text)
    with open(out, "w") as f:
        json.dump(res.get("structuredContent"), f, indent=2)
    return 1 if res.get("isError") else 0


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else ""))
