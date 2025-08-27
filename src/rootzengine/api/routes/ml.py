"""Machine learning API routes"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ...ml.training import train_model

router = APIRouter()

@router.post("/train")
async def train_ml_model(training_config: Dict[str, Any]) -> Dict[str, Any]:
    """Train a new ML model"""
    try:
        result = train_model(training_config.get('data'))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict/{file_id}")
async def predict(file_id: str) -> Dict[str, Any]:
    """Make predictions on audio file"""
    # TODO: Implement prediction
    return {
        "file_id": file_id,
        "predictions": {
            "genre": "reggae",
            "confidence": 0.85
        }
    }
