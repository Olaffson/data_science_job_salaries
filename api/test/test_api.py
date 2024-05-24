import os
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Utilisez un chemin relatif pour l'import
from api.api import app, generate_token

# Charger les variables d'environnement
os.environ["SECRET_KEY"] = "test_secret_key"
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"

client = TestClient(app)

@pytest.fixture
def token():
    return generate_token("admin")

@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token", data={"username": "admin", "password": os.environ.get("ADMIN_PASSWORD")})
    pytest.assume(response.status_code == 200)
    pytest.assume("access_token" in response.json())

@pytest.mark.asyncio
async def test_invalid_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token", data={"username": "admin", "password": "wrongpassword"})
    pytest.assume(response.status_code == 401)

@pytest.mark.asyncio
async def test_predict(token):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "experience_level": "se",
        "employment_type": "ft",
        "job_title": "dataengineer",
        "employee_residence": "gb",
        "remote_ratio": "0",
        "company_location": "gb",
        "company_size": "m"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/predict", json=payload, headers=headers)
    pytest.assume(response.status_code == 200)
    pytest.assume("prediction" in response.json())

@pytest.mark.asyncio
async def test_predict_without_token():
    payload = {
        "experience_level": "se",
        "employment_type": "ft",
        "job_title": "dataengineer",
        "employee_residence": "gb",
        "remote_ratio": "0",
        "company_location": "gb",
        "company_size": "m"
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/predict", json=payload)
    pytest.assume(response.status_code == 401)
