"""Endpoint de prédiction du prix immobilier."""

from fastapi import APIRouter, HTTPException
from app.api.schemas.prediction import HousingInput, PredictionOutput
from app.core.model_loader import predict, load_artifacts

router = APIRouter()


@router.post("/predict", response_model=PredictionOutput)
def predict_price(data: HousingInput):
    """Prédit le prix médian d'un logement en Californie."""
    try:
        input_dict = data.model_dump()
        price = predict(input_dict)
        price_dollars = f"${price * 100_000:,.0f}"

        return PredictionOutput(
            predicted_price=round(price, 4),
            predicted_price_dollars=price_dollars,
            features_used=data.model_dump(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
def get_metrics():
    """Retourne les métriques du modèle."""
    artifacts = load_artifacts()
    metrics = artifacts["metrics"]
    return {
        "mae": round(metrics["mae"], 4),
        "rmse": round(metrics["rmse"], 4),
        "r2": round(metrics["r2"], 4),
        "mae_dollars": f"${metrics['mae'] * 100_000:,.0f}",
    }


@router.get("/health")
def health_check():
    """Vérifie que le modèle est chargé."""
    try:
        load_artifacts()
        return {"status": "ok", "model": "loaded"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
