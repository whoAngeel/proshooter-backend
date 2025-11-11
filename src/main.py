import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infraestructure.config.settings import settings
from src.presentation.api.v1.routers import router as router_v1

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(
            sys.stdout
        ),  # Asegurar que sale a stdout (Docker lo captura)
    ],
)

logger = logging.getLogger(__name__)

# logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
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
    return {"status": "OK!!!!", "host": settings.HOST, "port": settings.PORT}


app.include_router(router_v1)
