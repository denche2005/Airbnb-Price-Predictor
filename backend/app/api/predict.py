from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.ml.prediction_pipeline import predict, get_city_info

router = APIRouter()


class PredictionInput(BaseModel):
    property_type: str = Field(default="Entire rental unit")
    room_type: str = Field(default="Entire home/apt")
    city: str = Field(default="New York")
    country: Optional[str] = None
    accommodates: int = Field(default=2, ge=1)
    bedrooms: float = Field(default=1, ge=0)
    beds: float = Field(default=1, ge=0)
    bathrooms: float = Field(default=1.0, ge=0)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    amenities_count: int = Field(default=20, ge=0)
    host_response_rate: float = Field(default=90.0, ge=0, le=100)
    host_acceptance_rate: float = Field(default=85.0, ge=0, le=100)
    host_is_superhost: str = Field(default="f")
    instant_bookable: str = Field(default="f")
    number_of_reviews: int = Field(default=10, ge=0)
    reviews_per_month: float = Field(default=1.5, ge=0)
    review_scores_rating: float = Field(default=4.5, ge=0, le=5)
    review_scores_accuracy: float = Field(default=4.5, ge=0, le=5)
    review_scores_cleanliness: float = Field(default=4.5, ge=0, le=5)
    review_scores_checkin: float = Field(default=4.5, ge=0, le=5)
    review_scores_communication: float = Field(default=4.5, ge=0, le=5)
    review_scores_location: float = Field(default=4.5, ge=0, le=5)
    review_scores_value: float = Field(default=4.5, ge=0, le=5)
    minimum_nights: int = Field(default=2, ge=1)
    availability_365: int = Field(default=200, ge=0, le=365)
    calculated_host_listings_count: int = Field(default=1, ge=0)

    has_elevator: Optional[int] = 0
    has_pool: Optional[int] = 0
    has_hot_tub: Optional[int] = 0
    has_gym: Optional[int] = 0
    has_doorman: Optional[int] = 0
    has_air_conditioning: Optional[int] = 0
    has_heating: Optional[int] = 0
    has_washer: Optional[int] = 0
    has_dryer: Optional[int] = 0
    has_kitchen: Optional[int] = 0
    has_tv: Optional[int] = 0
    has_wifi: Optional[int] = 0
    has_free_parking_on_premises: Optional[int] = 0
    has_indoor_fireplace: Optional[int] = 0
    has_patio_or_balcony: Optional[int] = 0
    has_breakfast: Optional[int] = 0
    has_buzzer_wireless_intercom: Optional[int] = 0
    has_wheelchair_accessible: Optional[int] = 0


@router.post("/predict")
async def predict_price(data: PredictionInput):
    try:
        result = predict(data.model_dump())
        return result
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run the training pipeline first.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cities")
async def cities():
    return get_city_info()
