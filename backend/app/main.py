from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.predict import router as predict_router
from app.api.scrape import router as scrape_router
from app.utils import load_json

app = FastAPI(
    title="Airbnb Price Predictor API",
    description="ML-powered price prediction for Airbnb listings",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router, prefix="/api", tags=["Prediction"])
app.include_router(scrape_router, prefix="/api", tags=["Scraping"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/metrics")
async def get_metrics():
    try:
        metrics = load_json("artifacts/metrics.json")
        return metrics
    except FileNotFoundError:
        return {"error": "Model not trained yet. Run train.py first."}
