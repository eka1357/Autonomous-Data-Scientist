from fastapi import APIRouter
from app.api.v1.endpoints import assistant, auth, datasets, health, models, predictions, projects

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
api_router.include_router(models.router, tags=["Models"])
api_router.include_router(predictions.router, tags=["Predictions"])
api_router.include_router(assistant.router, tags=["AI Assistant"])


