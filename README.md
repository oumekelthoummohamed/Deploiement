# Bank Churn MLOps

Projet MLOps complet pour la prediction de churn bancaire avec entrainement du modele, API FastAPI, Docker, deploiement Azure Container Apps, CI/CD GitHub Actions, detection de drift et application Streamlit.

## Contenu
- Entrainement du modele avec MLflow
- API FastAPI (health + predict)
- Dockerisation et tests locaux
- Deploiement sur Azure Container Apps via ACR
- CI/CD GitHub Actions
- Detection et simulation de drift (Evidently)
- App Streamlit pour tester l'API

## Structure
- app/ : code API FastAPI
- model/ : modele entraine (churn_model.pkl)
- Data/ : dataset
- train_model.py : entrainement + MLflow
- drift_detection.py : rapport de drift (reports/drift_report.html)
- streamlit_app.py : app Streamlit
- Dockerfile, .dockerignore
- .github/workflows/ci-cd.yml : pipeline CI/CD

## Prerequis
- Python 3.9+
- Docker Desktop
- Azure CLI (az login)
- Git

## Installation
```powershell
pip install -r requirements.txt
```

## Entrainement + MLflow
```powershell
python train_model.py
mlflow ui --port 5000
```
Ouvrir http://localhost:5000

## API locale
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Test:
```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Docker
Build:
```powershell
docker build -t bank-churn-api:v1 .
```
Run:
```powershell
docker run -d -p 8000:8000 --name churn-api bank-churn-api:v1
```
Test:
```powershell
Invoke-RestMethod http://localhost:8000/health
```
Stop:
```powershell
docker stop churn-api
docker rm churn-api
```

## Deploiement Azure
Variables recommandees:
- RESOURCE_GROUP=rg-mlops
- ACR_NAME=acrmlopskelthoummohamed
- CONTAINER_APP_NAME=acrmlopskelthoummohamed

URL publique:
- https://acrmlopskelthoummohamed.bluedesert-fa439975.swedencentral.azurecontainerapps.io

Test:
```powershell
$base = "https://acrmlopskelthoummohamed.bluedesert-fa439975.swedencentral.azurecontainerapps.io"
Invoke-RestMethod "$base/health"
```

## Drift (Evidently)
```powershell
python drift_detection.py
```
Rapport: reports/drift_report.html

## Streamlit
```powershell
streamlit run streamlit_app.py
```
Ouvrir http://localhost:8501

## CI/CD GitHub Actions
Le workflow est dans .github/workflows/ci-cd.yml.
Configurer les secrets GitHub Actions:
- AZURE_CREDENTIALS (JSON du service principal)
- ACR_NAME
- RESOURCE_GROUP
- CONTAINER_APP_NAME

Creation du service principal:
```powershell
az ad sp create-for-rbac --name "sp-bank-churn" --role contributor --scopes /subscriptions/39b7321b-cc7a-4f24-8a56-6634cb8c11c0 --sdk-auth
```

Role ACR Push:
```powershell
az role assignment create --assignee <APP_ID> --role AcrPush --scope /subscriptions/39b7321b-cc7a-4f24-8a56-6634cb8c11c0/resourceGroups/rg-mlops/providers/Microsoft.ContainerRegistry/registries/acrmlopskelthoummohamed
```

## Notes
- Respect strict du workshop valide.
- Docker image peut etre volumineuse a cause de MLflow et dependances ML.
