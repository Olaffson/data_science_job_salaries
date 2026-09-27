from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from pydantic import BaseModel
import joblib
import pandas as pd
import logging
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not SECRET_KEY or not ADMIN_PASSWORD:
    raise RuntimeError(
        "Les variables d'environnement SECRET_KEY et ADMIN_PASSWORD doivent être définies")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Charger le modèle (chemin relatif à ce fichier, indépendant du répertoire courant)
MODEL_PATH = Path(__file__).resolve().parent / "best_xgboost_model.pkl"
model = joblib.load(MODEL_PATH)

app = FastAPI()

bearer_scheme = HTTPBearer(auto_error=False)


class ModelInput(BaseModel):
    experience_level: str
    employment_type: str
    job_title: str
    employee_residence: str
    remote_ratio: str
    company_location: str
    company_size: str


def clean_text(value: str) -> str:
    # Même nettoyage que dans analyse/analyse.ipynb (données d'entraînement)
    return value.strip().lower().replace(' ', '')


def generate_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def has_access(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise credentials_exception
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
    except JWTError:
        raise credentials_exception
    if username == "admin":
        return True
    else:
        raise credentials_exception


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    if username == "admin" and password == ADMIN_PASSWORD:
        token = generate_token(username)
        return {"access_token": token, "token_type": "bearer"}  # nosec B105
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/predict", dependencies=[Depends(has_access)])
def predict(input: ModelInput):
    try:
        # Nettoyer les entrées comme lors de l'entraînement, puis convertir en DataFrame
        cleaned = {key: clean_text(value) for key, value in input.model_dump().items()}
        data = pd.DataFrame([cleaned])

        # Journaliser les données reçues pour le débogage
        logger.info(f"Données reçues pour prédiction : {data}")

        # Prédire en utilisant le modèle
        prediction = model.predict(data)

        # Convertir la prédiction en type natif Python (float)
        prediction_float = float(prediction[0])

        return {"prediction": prediction_float}
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la prédiction")


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=8000, log_level="info")
