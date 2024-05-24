from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
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

# Charger votre modèle
model = joblib.load("api/best_xgboost_model.pkl")

app = FastAPI()

# Charger les variables d'environnement
load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class ModelInput(BaseModel):
    experience_level: str
    employment_type: str
    job_title: str
    employee_residence: str
    remote_ratio: str
    company_location: str
    company_size: str

def generate_token(username: str) -> str:
    to_encode = {"sub": username}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def has_access(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/predict", dependencies=[Depends(has_access)])
def predict(input: ModelInput):
    try:
        # Convertir les données d'entrée en DataFrame
        data = pd.DataFrame([input.dict()])

        # Journaliser les données reçues pour le débogage
        logger.info(f"Données reçues pour prédiction : {data}")

        # Prédire en utilisant le modèle
        prediction = model.predict(data)

        # Convertir la prédiction en type natif Python (float)
        prediction_float = float(prediction[0])

        return {"prediction": prediction_float}
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=8000, log_level="info")