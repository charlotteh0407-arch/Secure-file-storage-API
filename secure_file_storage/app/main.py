from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Secure File Storage API is running"}

from app.database import engine, base
from app import models

base.metadata.create_all(bind=engine)
