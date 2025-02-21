from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infraestructure.database.session import get_db



app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/users")
async def get_users(db:AsyncSession = Depends(get_db)):
    return {"message": "Database connected"}
