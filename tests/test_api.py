from fastapi.testclient import TestClient
from src.api.routes import app
c=TestClient(app)
def test_health():
    assert c.get("/health").json()=={"ok": True}
