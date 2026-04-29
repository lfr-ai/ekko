import requests  # type: ignore[import-untyped]


def test_backend_health():
    resp = requests.get("http://localhost:8000/health", timeout=10)
    assert resp.status_code == 200
