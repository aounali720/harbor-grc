"""Security and workflow integration tests against the real HTTP application."""
import copy
import secrets
import time

import pytest
from fastapi.testclient import TestClient

from harbor_grc import auth, db, domain, frameworks
from harbor_grc.app import create_app
from harbor_grc.config import Settings

ORIGIN = "http://testserver"


@pytest.fixture(scope="session")
def passphrase():
    return secrets.token_urlsafe(24)


@pytest.fixture(scope="session")
def password_hash(passphrase):
    return auth.hash_password(passphrase)


@pytest.fixture
def workspace(tmp_path, password_hash):
    settings = Settings(database=tmp_path / "test.db", origin=ORIGIN)
    app = create_app(settings)
    with db.transaction(settings.database, write=True) as conn:
        for username, role in [("admin", "admin"), ("analyst", "analyst"), ("auditor", "auditor")]:
            conn.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                         (username, password_hash, role))
    with TestClient(app) as client:
        yield client, settings


def sign_in(client, passphrase, username="admin"):
    response = client.post("/api/auth/login", json={"username": username, "password": passphrase},
                           headers={"Origin": ORIGIN})
    assert response.status_code == 200, response.text
    return {"Origin": ORIGIN, "X-CSRF-Token": response.json()["csrf_token"]}


def control():
    return {"title": "Access review", "owner": "Security", "domain": "identity",
            "test_procedure": "Inspect all privileged accounts and approvals."}


def test_no_anonymous_register_or_export(workspace):
    client, _ = workspace
    for path in ["/api/risks", "/api/report", "/api/audit", "/api/schema"]:
        assert client.get(path).status_code == 401
    assert client.get("/health/live").status_code == 200
    assert client.get("/").status_code == 200


def test_cookie_is_httponly_and_session_is_hashed(workspace, passphrase):
    client, settings = workspace
    sign_in(client, passphrase)
    cookie = client.cookies[settings.cookie_name]
    with db.transaction(settings.database) as conn:
        row = conn.execute("SELECT * FROM sessions").fetchone()
    assert row["token_hash"] != cookie
    assert row["token_hash"] == auth.token_hash(cookie)
    assert client.get("/api/auth/me").json()["user"]["role"] == "admin"


def test_csrf_origin_and_content_type(workspace, passphrase):
    client, _ = workspace
    headers = sign_in(client, passphrase)
    assert client.post("/api/controls", json=control()).status_code == 403
    assert client.post("/api/controls", json=control(), headers={"Origin": ORIGIN}).status_code == 403
    evil = {**headers, "Origin": "https://attacker.example"}
    assert client.post("/api/controls", json=control(), headers=evil).status_code == 403
    assert client.post("/api/controls", content="{}", headers=headers).status_code == 415
    assert client.post("/api/controls", json=control(), headers=headers).status_code == 201


def test_login_csrf_host_and_validation_redaction(workspace):
    client, _ = workspace
    assert client.post("/api/auth/login", json={"username": "admin", "password": "wrong"}).status_code == 403
    assert client.get("/", headers={"Host": "attacker.example"}).status_code == 400
    marker = "sensitive-value-" * 20
    response = client.post("/api/auth/login", json={"username": "admin", "password": marker},
                           headers={"Origin": ORIGIN})
    assert response.status_code == 422
    assert marker not in response.text


def test_auditor_cannot_write_but_can_export_and_logout(workspace, passphrase):
    client, _ = workspace
    headers = sign_in(client, passphrase, "auditor")
    assert client.get("/api/controls").status_code == 200
    assert client.post("/api/controls", json=control(), headers=headers).status_code == 403
    assert client.post("/api/import/cloud", json={"Findings": []}, headers=headers).status_code == 403
    report = client.get("/api/report")
    assert report.status_code == 200
    assert "password_hash" not in report.text and "csrf_token" not in report.text
    assert client.post("/api/auth/logout", json={}, headers=headers).status_code == 200
    assert client.get("/api/auth/me").status_code == 401


def test_optimistic_update_rejects_lost_changes(workspace, passphrase):
    client, _ = workspace
    headers = sign_in(client, passphrase)
    original = client.post("/api/controls", json=control(), headers=headers).json()
    payload = {"version": original["version"], "data": {**control(), "title": "Updated access review"}}
    url = "/api/controls/" + original["id"]
    assert client.put(url, json=payload, headers=headers).status_code == 200
    assert client.put(url, json=payload, headers=headers).status_code == 409
    assert client.get(url).json()["title"] == "Updated access review"


def test_body_limit_security_headers(workspace, passphrase):
    client, _ = workspace
    headers = sign_in(client, passphrase)
    response = client.post("/api/controls", content=b"x" * 1_048_577,
                           headers={**headers, "Content-Type": "application/json"})
    assert response.status_code == 413
    for key in ["content-security-policy", "x-content-type-options", "cache-control", "x-request-id"]:
        assert key in response.headers
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_absolute_and_idle_session_expiry(workspace, passphrase):
    client, settings = workspace
    sign_in(client, passphrase)
    with db.transaction(settings.database, write=True) as conn:
        conn.execute("UPDATE sessions SET last_seen=?", (int(time.time())-1801,))
    assert client.get("/api/controls").status_code == 401
    sign_in(client, passphrase)
    with db.transaction(settings.database, write=True) as conn:
        conn.execute("UPDATE sessions SET expires_at=?", (int(time.time())-1,))
    assert client.get("/api/controls").status_code == 401


def test_login_failures_persist_and_throttle(workspace, passphrase):
    client, settings = workspace
    # Seed nine failures to exercise the boundary without ten expensive password calculations.
    with db.transaction(settings.database, write=True) as conn:
        for _ in range(9):
            auth.failed_login(conn, "admin", "testclient")
    response = client.post("/api/auth/login", json={"username": "admin", "password": "incorrect-value"},
                           headers={"Origin": ORIGIN})
    assert response.status_code == 401
    assert client.post("/api/auth/login", json={"username": "admin", "password": passphrase},
                       headers={"Origin": ORIGIN}).status_code == 429
    with db.transaction(settings.database) as conn:
        assert conn.execute("SELECT failures FROM login_limits WHERE key=?",
                            ("user:" + auth.token_hash("admin"),)).fetchone()[0] == 10


def test_reset_and_disable_revoke_sessions(workspace, passphrase):
    client, settings = workspace
    sign_in(client, passphrase, "analyst")
    with db.transaction(settings.database, write=True) as conn:
        auth.create_user(conn, "analyst", secrets.token_urlsafe(24), "analyst", reset=True)
    assert client.get("/api/auth/me").status_code == 401
    sign_in(client, passphrase)
    with db.transaction(settings.database, write=True) as conn:
        conn.execute("UPDATE users SET active=0 WHERE username='admin'")
    assert client.get("/api/auth/me").status_code == 401


def asff():
    return {"Findings": [{
        "Id": "synthetic-security-check-1",
        "UpdatedAt": "2026-01-01T00:00:00Z",
        "ProductArn": "arn:aws:securityhub:us-east-1:000000000000:product/example/check",
        "Title": "Public storage exposure",
        "Description": "Synthetic bucket policy requires review.",
        "Severity": {"Label": "HIGH"}, "Compliance": {"Status": "FAILED"},
        "Resources": [{"Id": "synthetic-bucket.example"}]
    }]}


def test_cloud_import_is_idempotent_and_maps_asset(workspace, passphrase):
    client, _ = workspace
    headers = sign_in(client, passphrase)
    asset = client.post("/api/assets", json={"title": "Demo storage", "owner": "Platform",
        "external_id": "synthetic-bucket.example"}, headers=headers).json()
    assert client.post("/api/import/cloud", json=asff(), headers=headers).json()["created"] == 1
    second = client.post("/api/import/cloud", json=asff(), headers=headers).json()
    assert second == {"created": 0, "updated": 0, "skipped": 1}
    finding = client.get("/api/findings").json()["items"][0]
    assert finding["asset_id"] == asset["id"]
    assert finding["status"] == "open"


def test_cloud_import_update_preserves_manual_assignment(workspace, passphrase):
    client, _ = workspace
    headers = sign_in(client, passphrase)
    client.post("/api/import/cloud", json=asff(), headers=headers)
    old = client.get("/api/findings").json()["items"][0]
    data = {key: old[key] for key in domain.SCHEMAS["findings"].model_fields}
    data["owner"] = "Assigned platform engineer"
    client.put("/api/findings/" + old["id"], json={"version": old["version"], "data": data}, headers=headers)
    incoming = asff()
    incoming["Findings"][0]["Severity"]["Label"] = "CRITICAL"
    incoming["Findings"][0]["UpdatedAt"] = "2026-01-02T00:00:00Z"
    assert client.post("/api/import/cloud", json=incoming, headers=headers).json()["updated"] == 1
    record = client.get("/api/findings/" + old["id"]).json()
    assert record["owner"] == "Assigned platform engineer" and record["severity"] == "critical"


def test_invalid_import_rolls_back_whole_batch(workspace, passphrase):
    client, _ = workspace
    headers = sign_in(client, passphrase)
    incoming = asff()
    incoming["Findings"].append({**copy.deepcopy(incoming["Findings"][0]), "Id": "second", "Title": ""})
    assert client.post("/api/import/cloud", json=incoming, headers=headers).status_code == 422
    assert client.get("/api/findings").json()["items"] == []


def test_passed_cloud_check_never_automatically_closes_findings(workspace, passphrase):
    client, _ = workspace
    headers = sign_in(client, passphrase)
    client.post("/api/import/cloud", json=asff(), headers=headers)
    passed = asff()
    passed["Findings"][0]["Compliance"]["Status"] = "PASSED"
    assert client.post("/api/import/cloud", json=passed, headers=headers).json()["skipped"] == 1
    assert client.get("/api/findings").json()["items"][0]["status"] == "open"


def test_audit_export_records_checkpoint(workspace, passphrase):
    client, settings = workspace
    headers = sign_in(client, passphrase)
    client.post("/api/controls", json=control(), headers=headers)
    report = client.get("/api/report").json()
    with db.transaction(settings.database) as conn:
        assert report["audit_verification"]["head_hash"] == domain.verify_audit(conn)["head_hash"]
        assert domain.list_audit(conn, 1)[0]["action"] == "report.exported"


def test_production_configuration_and_cookie(tmp_path, password_hash, passphrase):
    with pytest.raises(ValueError, match="HTTPS"):
        Settings(production=True)
    with pytest.raises(ValueError, match="Non-loopback"):
        Settings(origin="http://public.example")
    settings = Settings(database=tmp_path / "prod.db", origin="https://grc.example", production=True)
    app = create_app(settings)
    with db.transaction(settings.database, write=True) as conn:
        conn.execute("INSERT INTO users(username,password_hash,role) VALUES('admin',?,'admin')", (password_hash,))
    with TestClient(app, base_url="https://grc.example") as client:
        response = client.post("/api/auth/login", json={"username": "admin", "password": passphrase},
                               headers={"Origin": settings.origin})
        assert response.status_code == 200
        cookie = response.headers["set-cookie"]
        assert "__Host-harbor_session=" in cookie and "Secure" in cookie and "HttpOnly" in cookie
        assert "SameSite=strict" in cookie
        assert "strict-transport-security" in response.headers



def test_framework_endpoints_require_authentication_and_allow_auditors(workspace, passphrase):
    client, settings = workspace
    endpoints = ["/api/frameworks", "/api/frameworks/mappings", "/api/frameworks/coverage"]
    for endpoint in endpoints:
        assert client.get(endpoint).status_code == 401
    sign_in(client, passphrase, "auditor")
    catalog = client.get(endpoints[0])
    assert catalog.status_code == 200
    assert len(catalog.json()["items"]) == len(frameworks.catalog()["items"])
    assert client.get(endpoints[1]).status_code == 200
    coverage = client.get(endpoints[2]).json()
    assert coverage["local_control_count"] == 0
    assert len(coverage["items"]) == len(frameworks.catalog()["items"])
    assert all(item["mapped_controls"] == 0 for item in coverage["items"])
    with db.transaction(settings.database) as conn:
        assert conn.execute("SELECT COUNT(*) FROM records").fetchone()[0] == 0


def test_framework_snapshots_are_in_authenticated_report(workspace, passphrase):
    from harbor_grc.seed import seed_demo

    client, settings = workspace
    with db.transaction(settings.database, write=True) as conn:
        seed_demo(conn, "test-demo-operator")
    sign_in(client, passphrase, "auditor")
    report = client.get("/api/report").json()
    assert len(report["framework_catalog"]["items"]) == len(frameworks.catalog()["items"])
    assert len(report["framework_mappings"]["items"]) == 12
    assert report["framework_coverage"]["local_control_count"] == 12
    csf = next(item for item in report["framework_coverage"]["items"]
               if item["framework_id"] == "nist-csf-2.0")
    assert csf["mapped_controls"] == 12
    assert csf["evidence_backed_controls"] == 6
    assert "compliance_percent" not in csf



def test_generated_admin_can_sign_in_after_prior_failed_setup(tmp_path, monkeypatch, capsys):
    """Exercise the exact operator recovery path through the real HTTP boundary."""
    from harbor_grc.__main__ import main

    settings = Settings(database=tmp_path / "bootstrap.db", origin=ORIGIN)
    monkeypatch.setenv("GRC_DATABASE", str(settings.database))
    monkeypatch.setenv("GRC_ORIGIN", ORIGIN)
    monkeypatch.setenv("GRC_ENV", "local")
    app = create_app(settings)
    with db.transaction(settings.database, write=True) as conn:
        for _ in range(10):
            auth.failed_login(conn, "admin", "testclient")
        assert auth.rate_limited(conn, "admin", "testclient")
    assert main(["init", "--admin", "admin", "--generate-password"]) == 0
    output = capsys.readouterr().out
    generated = next(line.removeprefix("Generated passphrase: ") for line in output.splitlines()
                     if line.startswith("Generated passphrase: "))
    assert 14 <= len(generated) <= 128
    with TestClient(app) as client:
        response = client.post("/api/auth/login",
                               json={"username": "admin", "password": generated},
                               headers={"Origin": ORIGIN})
        assert response.status_code == 200
        assert response.json()["user"] == {"username": "admin", "role": "admin"}
        assert generated not in client.get("/api/report").text
    with db.transaction(settings.database) as conn:
        assert generated not in "\n".join(conn.iterdump())
        assert domain.verify_audit(conn)["valid"]

