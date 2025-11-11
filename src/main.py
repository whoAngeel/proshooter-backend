import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infraestructure.config.settings import settings
from src.presentation.api.v1.routers import router as router_v1

LOG_LEVEL = settings.LOG_LEVEL if hasattr(settings, "LOG_LEVEL") else "INFO"
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "default",
        }
    },
    "root": {
        "handlers": ["stdout"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "uvicorn": {"handlers": ["stdout"], "level": LOG_LEVEL, "propagate": False},
        "uvicorn.error": {
            "handlers": ["stdout"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["stdout"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}
logging.config.dictConfig(logging_config)

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
