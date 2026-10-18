import json
import socket
import ssl
import time
import urllib.request
import urllib.error

HOST = "formelec.sunarp.gob.pe"
IP = "191.98.163.166"
BASE = "https://" + HOST + "/SunarpRestWebservices/v2/SnrpRest.svc"

def run(name, function):
    start = time.monotonic()
    try:
        value = function()
        ok = True
    except Exception as e:
        value = type(e).__name__ + ": " + str(e)[:160]
        ok = False

    return {
        "test": name,
        "ok": ok,
        "ms": round((time.monotonic() - start) * 1000),
        "result": value
    }

def dns():
    return sorted(set(
        x[4][0]
        for x in socket.getaddrinfo(
            HOST, 443,
            type=socket.SOCK_STREAM
        )
    ))

def tcp(host, port):
    with socket.create_connection(
        (host, port),
        timeout=7
    ) as s:
        return {
            "connected": True,
            "localPort": s.getsockname()[1]
        }

def tls():
    context = ssl.create_default_context()

    with socket.create_connection(
        (IP, 443), timeout=7
    ) as raw:

        raw.settimeout(7)

        with context.wrap_socket(
            raw,
            server_hostname=HOST
        ) as conn:
            return {
                "version": conn.version(),
                "cipher": conn.cipher()[0],
                "certificateVerified": True
            }

def http(url, method="GET", body=None):
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({})
    )

    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "text/plain"
        } if body is not None else {},
        method=method
    )

    try:
        with opener.open(
            request, timeout=10
        ) as response:

            response.read(1024)

            return {
                "status": response.status,
                "contentType": response.headers.get(
                    "Content-Type", ""
                )
            }

    except urllib.error.HTTPError as e:
        return {
            "status": e.code,
            "note": "HTTP_RESPONSE_RECEIVED"
        }

def public_ip():
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({})
    )

    with opener.open(
        "https://api.ipify.org?format=json",
        timeout=10
    ) as response:
        return json.load(response)

tests = [
    run("01_DNS_SUNARP", dns),
    run("02_TCP_SUNARP_IP", lambda: tcp(IP, 443)),
    run("03_TCP_SUNARP_DNS", lambda: tcp(HOST, 443)),
    run("04_TCP_GOOGLE", lambda: tcp("www.google.com", 443)),
    run("05_TLS_SUNARP", tls),
    run("06_GET_WSDL", lambda: http(BASE + "?singleWsdl")),
    run("07_POST_ANONIMO", lambda: http(
        BASE + "/getVehiculoPImage",
        "POST", b"{}"
    )),
    run("08_IP_SALIDA", public_ip)
]

data = {
    "platform": __import__("platform").platform(),
    "destination": HOST,
    "credentialsUsed": False,
    "tests": tests
}

print("SUNARP_RESULT=" + json.dumps(
    data, separators=(",", ":")
), flush=True)