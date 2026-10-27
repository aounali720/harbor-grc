"""HTTP boundary: role checks, sessions, CSRF, limits and domain transactions."""
import hmac
import logging
import secrets
import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import auth, db, domain, frameworks
from .cloud import import_findings
from .config import Settings

LOG = logging.getLogger(__name__)
STATIC = Path(__file__).parent / "static"


class Login(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class Update(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: int = Field(ge=1, strict=True)
    data: dict


class RequestBoundary:
    """Bound bodies before JSON parsing, reject cross-origin writes, set headers."""
    def __init__(self, app, settings):
        self.app, self.settings = app, settings

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        request_id = secrets.token_hex(8)

        async def secured_send(message):
            if message["type"] == "http.response.start":
                extra = [
                    (b"content-security-policy", b"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"),
                    (b"x-content-type-options", b"nosniff"), (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"no-referrer"), (b"cache-control", b"no-store"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                    (b"x-request-id", request_id.encode()),
                ]
                if self.settings.production:
                    extra.append((b"strict-transport-security", b"max-age=31536000"))
                message = {**message, "headers": list(message.get("headers", [])) + extra}
            await send(message)

        if scope["method"] in {"POST", "PUT", "PATCH", "DELETE"}:
            if headers.get(b"origin", b"").decode("latin-1") != self.settings.origin:
                response = JSONResponse({"detail": "Request origin does not match this workspace"}, 403)
                return await response(scope, receive, secured_send)
            content_type = headers.get(b"content-type", b"").decode("latin-1").split(";")[0].strip()
            if content_type != "application/json":
                return await JSONResponse({"detail": "Use application/json"}, 415)(scope, receive, secured_send)
            try:
                declared = int(headers.get(b"content-length", b"0"))
            except ValueError:
                return await JSONResponse({"detail": "Invalid content length"}, 400)(scope, receive, secured_send)
            if declared < 0 or declared > self.settings.max_body_bytes:
                return await JSONResponse({"detail": "Request exceeds the 1 MiB limit"}, 413)(scope, receive, secured_send)
            body = bytearray()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                body.extend(message.get("body", b""))
                if len(body) > self.settings.max_body_bytes:
                    return await JSONResponse({"detail": "Request exceeds the 1 MiB limit"}, 413)(scope, receive, secured_send)
                if not message.get("more_body", False):
                    break
            delivered = False

            async def buffered_receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()

            return await self.app(scope, buffered_receive, secured_send)
        return await self.app(scope, receive, secured_send)


def create_app(settings=None):
    settings = settings or Settings.from_env()
    db.initialize(settings.database)
    # A real scrypt calculation also runs for unknown users.
    dummy_hash = auth.hash_password(secrets.token_urlsafe(24))
    app = FastAPI(title="Harbor GRC", version="1.1.2", docs_url=None,
                  redoc_url=None, openapi_url=None)
    app.state.settings = settings
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[settings.allowed_host])
    app.add_middleware(RequestBoundary, settings=settings)

    def session_for(request, conn, *, write=False):
        session = auth.current_session(conn, request.cookies.get(settings.cookie_name), settings)
        if not session:
            raise HTTPException(401, "Sign in to continue")
        if write:
            csrf = request.headers.get("x-csrf-token", "")
            if not csrf or not hmac.compare_digest(csrf, session["csrf_token"]):
                raise HTTPException(403, "Invalid CSRF token; refresh and try again")
            if session["role"] not in {"admin", "analyst"}:
                raise HTTPException(403, "This account has read-only access")
        return session

    def workspace(conn):
        return {"name": "Harbor GRC", "demo": db.demo_enabled(conn)}

    def account_response(session, conn):
        return {"user": {"username": session["username"], "role": session["role"]},
                "csrf_token": session["csrf_token"], "workspace": workspace(conn)}

    @app.exception_handler(RequestValidationError)
    @app.exception_handler(ValidationError)
    async def domain_validation_error(request, exc):
        errors = "; ".join(".".join(map(str, e["loc"])) + ": " + e["msg"]
                           for e in exc.errors())
        return JSONResponse({"detail": errors}, 422)

    @app.exception_handler(domain.ConflictError)
    async def conflict_error(request, exc):
        return JSONResponse({"detail": str(exc)}, 409)

    @app.exception_handler(KeyError)
    async def missing_record(request, exc):
        return JSONResponse({"detail": "Record not found"}, 404)

    @app.exception_handler(ValueError)
    async def workflow_error(request, exc):
        return JSONResponse({"detail": str(exc)}, 400)

    @app.exception_handler(sqlite3.OperationalError)
    async def database_busy(request, exc):
        LOG.error("Database operation failed: %s", type(exc).__name__)
        return JSONResponse({"detail": "Database unavailable; try again shortly"}, 503,
                            headers={"Retry-After": "1"})

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/health/live")
    def live():
        return {"status": "ok"}

    @app.get("/health/ready")
    def ready():
        try:
            with db.transaction(settings.database) as conn:
                version = conn.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
                if version is None or version[0] != "1":
                    return JSONResponse({"status": "unavailable"}, 503)
                for query in (
                    "SELECT id,kind,version,data FROM records LIMIT 0",
                    "SELECT seq,hash,previous_hash FROM audit LIMIT 0",
                    "SELECT username,password_hash,role,active FROM users LIMIT 0",
                    "SELECT token_hash,username,csrf_token,expires_at,last_seen FROM sessions LIMIT 0",
                    "SELECT key,window_start,failures FROM login_limits LIMIT 0",
                ):
                    conn.execute(query)
            return {"status": "ready"}
        except sqlite3.Error:
            return JSONResponse({"status": "unavailable"}, 503)

    @app.post("/api/auth/login")
    def login(payload: Login, request: Request):
        username = payload.username.strip().lower()
        ip = request.client.host if request.client else "unknown"
        error = None
        with db.transaction(settings.database, write=True) as conn:
            if auth.rate_limited(conn, username, ip):
                error = 429
            else:
                user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
                valid = auth.check_password(payload.password, user["password_hash"] if user else dummy_hash)
                if not valid or not user or not user["active"]:
                    auth.failed_login(conn, username, ip)
                    domain.record_event(conn, "anonymous", "auth.failed", "authentication",
                                        {"principal_hash": auth.token_hash(username)})
                    error = 401
                else:
                    previous = request.cookies.get(settings.cookie_name)
                    if previous:
                        conn.execute("DELETE FROM sessions WHERE token_hash=?", (auth.token_hash(previous),))
                    token, csrf = auth.start_session(conn, username, settings)
                    domain.record_event(conn, username, "auth.login", "authentication", {})
                    data = {"user": {"username": username, "role": user["role"]},
                            "csrf_token": csrf, "workspace": workspace(conn)}
        if error:
            raise HTTPException(error, "Too many attempts; retry in 15 minutes" if error == 429
                                else "Invalid username or password",
                                headers={"Retry-After": "900"} if error == 429 else None)
        response = JSONResponse(data)
        response.set_cookie(settings.cookie_name, token, max_age=settings.session_hours*3600,
                            httponly=True, secure=settings.production, samesite="strict", path="/")
        return response

    @app.get("/api/auth/me")
    def me(request: Request):
        with db.transaction(settings.database, write=True) as conn:
            return account_response(session_for(request, conn), conn)

    @app.post("/api/auth/logout")
    def logout(request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session = session_for(request, conn)
            if not hmac.compare_digest(request.headers.get("x-csrf-token", ""), session["csrf_token"]):
                raise HTTPException(403, "Invalid CSRF token")
            conn.execute("DELETE FROM sessions WHERE token_hash=?", (session["token_hash"],))
            domain.record_event(conn, session["username"], "auth.logout", "authentication", {})
        response = JSONResponse({"status": "signed_out"})
        response.delete_cookie(settings.cookie_name, path="/", secure=settings.production,
                               httponly=True, samesite="strict")
        return response

    @app.get("/api/schema")
    def schemas(request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session_for(request, conn)
        return {"kinds": {kind: model.model_json_schema() for kind, model in domain.SCHEMAS.items()}}

    @app.get("/api/dashboard")
    def dashboard(request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session_for(request, conn)
            return domain.dashboard(conn)

    @app.get("/api/audit")
    def audit(request: Request, limit: int = 200):
        with db.transaction(settings.database, write=True) as conn:
            session_for(request, conn)
            return {"items": domain.list_audit(conn, limit), "verification": domain.verify_audit(conn)}

    @app.get("/api/report")
    def report(request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session = session_for(request, conn)
            domain.record_event(conn, session["username"], "report.exported", "workspace", {})
            data = domain.report(conn)
            data["workspace"] = workspace(conn)
        return JSONResponse(data, headers={"Content-Disposition": 'attachment; filename="harbor-grc-report.json"'})

    @app.post("/api/import/cloud")
    def cloud_import(payload: dict, request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session = session_for(request, conn, write=True)
            return import_findings(conn, payload, session["username"])

    @app.get("/api/frameworks")
    def framework_catalog(request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session_for(request, conn)
        return frameworks.catalog()

    @app.get("/api/frameworks/mappings")
    def framework_mappings(request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session_for(request, conn)
        return frameworks.mappings()

    @app.get("/api/frameworks/coverage")
    def framework_coverage(request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session_for(request, conn)
            return frameworks.coverage(conn)

    @app.get("/api/{kind}")
    def records(kind: str, request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session_for(request, conn)
            return {"items": domain.list_records(conn, kind)}

    @app.get("/api/{kind}/{record_id}")
    def record(kind: str, record_id: str, request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session_for(request, conn)
            return domain.get_record(conn, kind, record_id)

    @app.post("/api/{kind}", status_code=201)
    def create_record(kind: str, payload: dict, request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session = session_for(request, conn, write=True)
            return domain.create_record(conn, kind, payload, session["username"])

    @app.put("/api/{kind}/{record_id}")
    def update_record(kind: str, record_id: str, payload: Update, request: Request):
        with db.transaction(settings.database, write=True) as conn:
            session = session_for(request, conn, write=True)
            return domain.update_record(conn, kind, record_id, payload.data, payload.version,
                                        session["username"])

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app

