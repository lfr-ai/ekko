import os

import pytest

# These integration tests depend on optional packages and external services.
# Skip the entire module if psycopg2 is not installed in the test environment.
psycopg2 = pytest.importorskip("psycopg2")


@pytest.mark.integration
def test_postgres_and_redis_available():
    # Postgres default service provided by CI will be on localhost:5432
    # Read password from environment; if not provided, skip the test to avoid
    # embedding secrets in the repository.
    pg_password = os.environ.get("POSTGRES_PASSWORD")  # pragma: allowlist secret
    if not pg_password:
        pytest.skip("POSTGRES_PASSWORD not set; skipping integration check")

    conn = None
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=pg_password,
            host=os.environ.get("POSTGRES_HOST", "127.0.0.1"),
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            connect_timeout=2,
        )
        conn.close()
    except Exception as e:
        raise AssertionError(f"Postgres not available: {e}")

    try:
        import redis

        r = redis.Redis(host="127.0.0.1", port=6379, db=0)
        r.ping()
    except Exception as e:
        raise AssertionError(f"Redis not available: {e}")
