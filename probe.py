import json
import os
import platform
import socket
import ssl
import time
import concurrent.futures

TARGETS = [
    {"name": "FORMELEC", "ip": "191.98.163.166", "host": "formelec.sunarp.gob.pe"},
    {"name": "PORTAL",   "ip": "191.98.163.146", "host": "www.sunarp.gob.pe"},
    {"name": "ENLINEA",  "ip": "191.98.163.145", "host": "enlinea.sunarp.gob.pe"},
    {"name": "SPRL",     "ip": "191.98.163.237", "host": "sprl.sunarp.gob.pe"}
]

def probe(target):
    start = time.monotonic()
    result = {
        "name": target["name"],
        "ip": target["ip"],
        "host": target["host"],
        "tcp": False,
        "tls": False,
        "tlsVersion": None,
        "error": None
    }

    try:
        with socket.create_connection(
            (target["ip"], 443),
            timeout=6
        ) as sock:
            result["tcp"] = True
            result["tcpMs"] = round(
                (time.monotonic() - start) * 1000
            )

            sock.settimeout(6)
            context = ssl.create_default_context()

            with context.wrap_socket(
                sock,
                server_hostname=target["host"]
            ) as secure:
                result["tls"] = True
                result["tlsVersion"] = secure.version()

    except Exception as e:
        result["error"] = (
            type(e).__name__ + ": " + str(e)[:120]
        )

    result["totalMs"] = round(
        (time.monotonic() - start) * 1000
    )

    return result

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(probe, TARGETS))

data = {
    "runner": os.environ.get("RUNNER_NAME", "unknown"),
    "runnerOS": os.environ.get("RUNNER_OS", platform.system()),
    "platform": platform.platform(),
    "tests": results
}

print("SUNARP_RESULT=" + json.dumps(
    data, separators=(",", ":")
), flush=True)