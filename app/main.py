import logging
import os
import socket
from itertools import count

from flask import Flask, jsonify, render_template, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from app.aws_meta import fetch_aws_metadata

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("devops-exam-app")

REQUESTS = Counter("app_http_requests_total", "Total HTTP requests", ["path"])
_counter = count(1)

app = Flask(__name__)


def server_info():
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "n/a"
    return {
        "hostname": hostname,
        "server_ip": ip,
        "pod_name": os.environ.get("HOSTNAME", hostname),
        "pod_ip": os.environ.get("POD_IP", ip),
        "node_name": os.environ.get("NODE_NAME", "n/a"),
        "node_ip": os.environ.get("NODE_IP", "n/a"),
        "request_id": next(_counter),
        "client_ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "aws": fetch_aws_metadata(),
    }


@app.after_request
def access_log(response):
    log.info(
        "method=%s path=%s status=%s pod=%s node=%s",
        request.method,
        request.path,
        response.status_code,
        os.environ.get("HOSTNAME", ""),
        os.environ.get("NODE_NAME", ""),
    )
    return response


@app.get("/")
def index():
    REQUESTS.labels(path="/").inc()
    return render_template("index.html", info=server_info())


@app.get("/api/info")
def api_info():
    REQUESTS.labels(path="/api/info").inc()
    return jsonify(server_info())


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))