import logging
import logging.config
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infraestructure.config.settings import settings
from src.presentation.api.v1.routers import router as router_v1

# Convertir LOG_LEVEL de string a nivel de logging
LOG_LEVEL_STR = settings.LOG_LEVEL if hasattr(settings, "LOG_LEVEL") else "INFO"
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR.upper(), logging.INFO)

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
        "level": LOG_LEVEL,  # Ahora es un entero, no un string
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
        "src.infraestructure.utils.s3_utils": {
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
