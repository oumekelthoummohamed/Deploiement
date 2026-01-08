from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np
from typing import List
import logging
import os
from pathlib import Path
from pydantic import BaseModel, Field

# Définir les modèles Pydantic directement ici
class CustomerFeatures(BaseModel):
    """Schema pour les features d'un client"""
    CreditScore: int = Field(..., ge=300, le=850, description="Score de credit")
    Age: int = Field(..., ge=18, le=100, description="Age du client")
    Tenure: int = Field(..., ge=0, le=10, description="Anciennete en annees")
    Balance: float = Field(..., ge=0, description="Solde du compte")
    NumOfProducts: int = Field(..., ge=1, le=4, description="Nombre de produits")
    HasCrCard: int = Field(..., ge=0, le=1, description="Possession carte credit")
    IsActiveMember: int = Field(..., ge=0, le=1, description="Membre actif")
    EstimatedSalary: float = Field(..., ge=0, description="Salaire estime")
    Geography_Germany: int = Field(..., ge=0, le=1, description="Client allemand")
    Geography_Spain: int = Field(..., ge=0, le=1, description="Client espagnol")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "CreditScore": 650,
                "Age": 35,
                "Tenure": 5,
                "Balance": 50000,
                "NumOfProducts": 2,
                "HasCrCard": 1,
                "IsActiveMember": 1,
                "EstimatedSalary": 75000,
                "Geography_Germany": 0,
                "Geography_Spain": 1
            }
        }
    }

class PredictionResponse(BaseModel):
    """Schema pour la reponse de prediction"""
    churn_probability: float = Field(..., description="Probabilite de churn (0-1)")
    prediction: int = Field(..., description="Prediction binaire (0=reste, 1=part)")
    risk_level: str = Field(..., description="Niveau de risque (Low/Medium/High)")

class HealthResponse(BaseModel):
    """Schema pour le health check"""
    status: str
    model_loaded: bool

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation FastAPI
app = FastAPI(
    title="Bank Churn Prediction API",
    description="API de prediction de defaillance client",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS pour permettre les requetes depuis un navigateur
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement du modele au demarrage
# Construire le chemin du modele de maniere robuste
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = os.getenv("MODEL_PATH", str(PROJECT_ROOT / "model" / "churn_model.pkl"))
model = None

def load_model_sync():
    """Charge le modele de facon synchrone"""
    global model
    try:
        # Essayer le chemin fourni d'abord
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            logger.info(f"Modele charge avec succes depuis {MODEL_PATH}")
        else:
            logger.warning(f"Modele non trouve a {MODEL_PATH}")
            model = None
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modele : {e}")
        model = None

@app.on_event("startup")
async def startup_event():
    """Charge le modele au demarrage de l'API"""
    load_model_sync()

@app.get("/", tags=["General"])
def root():
    """Endpoint racine"""
    return {
        "message": "Bank Churn Prediction API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """Verification de l'etat de l'API"""
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail="Modele non charge"
        )
    return {
        "status": "healthy",
        "model_loaded": True
    }

@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(features: CustomerFeatures):
    """
    Predit si un client va partir (churn)
    
    Retourne :
    - churn_probability : probabilite de churn (0 a 1)
    - prediction : 0 (reste) ou 1 (part)
    - risk_level : Low, Medium ou High
    """
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail="Modele non disponible"
        )
    
    try:
        # Preparation des features
        input_data = np.array([[
            features.CreditScore,
            features.Age,
            features.Tenure,
            features.Balance,
            features.NumOfProducts,
            features.HasCrCard,
            features.IsActiveMember,
            features.EstimatedSalary,
            features.Geography_Germany,
            features.Geography_Spain
        ]])
        
        # Prediction
        proba = model.predict_proba(input_data)[0, 1]
        prediction = int(proba > 0.5)
        
        # Classification du risque
        if proba < 0.3:
            risk = "Low"
        elif proba < 0.7:
            risk = "Medium"
        else:
            risk = "High"
        
        logger.info(
            f"Prediction effectuee : proba={proba:.4f}, "
            f"prediction={prediction}, risk={risk}"
        )
        
        return {
            "churn_probability": round(float(proba), 4),
            "prediction": prediction,
            "risk_level": risk
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la prediction : {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur de prediction : {str(e)}"
        )

@app.post("/predict/batch", tags=["Prediction"])
def predict_batch(features_list: List[CustomerFeatures]):
    """
    Predictions en batch pour plusieurs clients
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Modele non disponible")
    
    try:
        predictions = []
        
        for features in features_list:
            input_data = np.array([[
                features.CreditScore, features.Age, features.Tenure,
                features.Balance, features.NumOfProducts, features.HasCrCard,
                features.IsActiveMember, features.EstimatedSalary,
                features.Geography_Germany, features.Geography_Spain
            ]])
            
            proba = model.predict_proba(input_data)[0, 1]
            prediction = int(proba > 0.5)
            
            predictions.append({
                "churn_probability": round(float(proba), 4),
                "prediction": prediction
            })
        
        logger.info(f"Batch prediction : {len(predictions)} clients traites")
        
        return {"predictions": predictions, "count": len(predictions)}
    
    except Exception as e:
        logger.error(f"Erreur batch prediction : {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)