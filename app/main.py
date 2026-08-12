from fastapi import FastAPI
from app.database import engine, Base
from app import models

app = FastAPI()

@app.get("/")
def health_check():
    return {"message": "Secure File Storage API is running"}


Base.metadata.create_all(bind=engine)
