"""Schemas Pydantic pour l'endpoint de prédiction."""

from pydantic import BaseModel, Field


class HousingInput(BaseModel):
    """Entrée utilisateur : les 8 features du dataset California Housing."""
    MedInc: float = Field(..., description="Revenu médian (×$10k)", ge=0, le=20)
    HouseAge: float = Field(..., description="Âge médian du logement (années)", ge=0, le=60)
    AveRooms: float = Field(..., description="Nombre moyen de pièces", ge=0, le=50)
    AveBedrms: float = Field(..., description="Nombre moyen de chambres", ge=0, le=20)
    Population: float = Field(..., description="Population du district", ge=0, le=50000)
    AveOccup: float = Field(..., description="Occupation moyenne", ge=0, le=20)
    Latitude: float = Field(..., description="Latitude", ge=32, le=42)
    Longitude: float = Field(..., description="Longitude", ge=-125, le=-114)


class PredictionOutput(BaseModel):
    """Résultat de la prédiction."""
    predicted_price: float = Field(..., description="Prix prédit (×$100k)")
    predicted_price_dollars: str = Field(..., description="Prix en dollars formaté")
    features_used: dict = Field(..., description="Features utilisées pour la prédiction")
