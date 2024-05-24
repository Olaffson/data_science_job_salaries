import os
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException, Depends, status
from httpx import AsyncClient
from jose import JWTError, jwt


# Charger les variables d'environnement
os.environ["SECRET_KEY"] = "test_secret_key"
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"

app = FastAPI()

client = TestClient(app)


def generate_token(username: str) -> str:
    to_encode = {"sub": username}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@pytest.fixture
def token():
    return generate_token("admin")


@pytest.mark.asyncio
async def test_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token", data={"username": "admin", "password": os.environ.get("ADMIN_PASSWORD")})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_invalid_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/token", data={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401


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
    assert response.status_code == 200
    assert "prediction" in response.json()


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
    assert response.status_code == 401
