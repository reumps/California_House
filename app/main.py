"""Point d'entrée FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.predict import router as predict_router

app = FastAPI(
    title="California Housing API",
    description="API de prédiction du prix immobilier en Californie",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router, prefix="/api/v1", tags=["Prediction"])


@app.get("/")
def root():
    return {
        "app": "California Housing Price Predictor",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
