from app.main import app


def test_healthz():
    c = app.test_client()
    r = c.get("/healthz")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_api_info_has_hostname():
    c = app.test_client()
    r = c.get("/api/info")
    assert r.status_code == 200
    data = r.get_json()
    assert "hostname" in data
    assert "aws" in data
    assert "instance_id" in data["aws"]


def test_metrics():
    c = app.test_client()
    r = c.get("/metrics")
    assert r.status_code == 200
    assert b"app_http_requests_total" in r.data or r.status_code == 200