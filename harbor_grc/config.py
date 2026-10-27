"""Small, explicit configuration surface. No default credentials."""
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

@dataclass(frozen=True)
class Settings:
    database: Path = Path("data/harbor.db")
    origin: str = "http://127.0.0.1:8000"
    production: bool = False
    session_hours: int = 8
    idle_minutes: int = 30
    max_body_bytes: int = 1_048_576

    def __post_init__(self):
        parsed = urlsplit(self.origin)
        if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                or parsed.path or parsed.query or parsed.fragment or parsed.username):
            raise ValueError("GRC_ORIGIN must be one origin, without a path or credentials")
        if self.production and parsed.scheme != "https":
            raise ValueError("Production requires an HTTPS GRC_ORIGIN")
        if not self.production and parsed.hostname not in {"127.0.0.1", "localhost", "::1", "testserver"}:
            raise ValueError("Non-loopback deployment requires GRC_ENV=production and HTTPS")

    @property
    def cookie_name(self):
        return "__Host-harbor_session" if self.production else "harbor_session"

    @property
    def allowed_host(self):
        return urlsplit(self.origin).hostname

    @classmethod
    def from_env(cls):
        env = os.environ.get("GRC_ENV", "local")
        if env not in {"local", "production"}:
            raise ValueError("GRC_ENV must be local or production")
        return cls(database=Path(os.environ.get("GRC_DATABASE", "data/harbor.db")),
                   origin=os.environ.get("GRC_ORIGIN", "http://127.0.0.1:8000"),
                   production=env == "production")

