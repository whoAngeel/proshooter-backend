from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.infraestructure.database.session import get_db
from src.infraestructure.config.settings import settings

from src.presentation.api.v1.routers import router as router_v1

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, description="API para la gestion de practicas de tiro")

@app.get("/health")
def health_check():
    return {"status": "ok"}

# print("Estoy corriendo")

app.include_router(router_v1)
