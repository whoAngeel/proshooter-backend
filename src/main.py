from fastapi import FastAPI
from src.infraestructure.config.settings import settings
from fastapi.middleware.cors import CORSMiddleware

from src.presentation.api.v1.routers import router as router_v1

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API para la gestion de practicas de tiro",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "OK lesgo!!!!", "host": settings.HOST, "port": settings.PORT}


app.include_router(router_v1)
