
import sys
import os
import asyncio
from unittest.mock import AsyncMock, patch

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Env Vars
os.environ["GOOGLE_CLIENT_ID"] = "dummy"
os.environ["GOOGLE_CLIENT_SECRET"] = "dummy"
os.environ["GEMINI_API_KEY"] = "dummy"
os.environ["OPENAI_API_KEY"] = "dummy"

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def verify_auth_dependency():
    print("Testing Auth Dependency...")
    
    # 1. Test missing token
    response = client.post("/api/emails/sync")
    print(f"Missing Token Response: {response.status_code}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
    print("✅ Auth rejected missing token")
    
    # 2. Test valid token using override
    from api.dependencies import get_current_user
    from models.user import User
    
    async def mock_get_current_user():
        return User(id="test-user", email="test@example.com")
        
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    with patch("api.routes.emails.IngestionService") as MockService:
        instance = MockService.return_value
        instance.sync_user_emails = AsyncMock()
        
        response = client.post("/api/emails/sync")
        print(f"Valid Token Response: {response.status_code}")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        
    app.dependency_overrides = {}
    print("✅ Auth accepted valid token (Mocked)")

if __name__ == "__main__":
    verify_auth_dependency()
