from fastapi import FastAPI
from app.database import engine, Base
from app import models
from app.api import auth, files
app = FastAPI()

@app.get("/")
def health_check():
    return {"message": "Secure File Storage API is running"}

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(files.router)