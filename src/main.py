from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.infraestructure.database.session import get_db
from src.infraestructure.config.settings import settings


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/users")
async def get_users(db:Session = Depends(get_db)):
    return {"message": "Database connected"}
