# PricebnB — Airbnb Price Predictor

A full-stack ML-powered application that predicts Airbnb nightly prices using gradient boosting models trained on 74,000+ real listings across 6 major US cities.

## Features

- **ML Price Prediction** — LightGBM model tuned with Bayesian optimization (Optuna), achieving strong R² on the test set
- **Airbnb URL Scraper** — Paste any Airbnb listing URL to automatically extract features and predict the price
- **Manual Input Form** — Enter property details manually for instant estimates
- **Feature Importance** — See which factors influence pricing the most
- **Confidence Intervals** — Get low/high price range estimates
- **Modern UI** — Airbnb-inspired responsive design built with React + Tailwind CSS

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, Recharts, Lucide Icons |
| Backend | FastAPI, Uvicorn, Python 3.11+ |
| ML | LightGBM, XGBoost, CatBoost, Optuna, scikit-learn |
| Scraper | Playwright (headless Chromium) |
| Deployment | Docker Compose |

## Architecture

```
User → React Frontend → FastAPI Backend → ML Pipeline → Prediction
                                        → Playwright Scraper (for URL input)
```

**ML Pipeline:**
1. **Data Ingestion** — Load 74K Airbnb listings, clean and split 80/20
2. **Feature Engineering** — 19 base features + 3 derived (rooms_per_person, beds_per_room, bath_per_room)
3. **Preprocessing** — Imputation + Ordinal Encoding + Standard Scaling
4. **Model Training** — 9 baseline models → top 3 tuned with Optuna (20 trials each) → best model selected
5. **Prediction** — Load artifacts, transform input, predict log_price, convert to USD

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+

### Backend

```bash
cd backend
pip install -r requirements.txt
python train.py        # Train the model (~10-15 min)
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev            # Starts on http://localhost:5173
```

### Docker (Alternative)

```bash
docker-compose up --build
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000/docs
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/predict` | Predict price from manual input |
| POST | `/api/scrape` | Scrape Airbnb URL + predict |
| GET | `/api/metrics` | Get model training metrics |
| GET | `/api/health` | Health check |

## Dataset

The model is trained on [Airbnb listing data](https://www.kaggle.com/) covering 6 US cities:
- New York City, San Francisco, Los Angeles, Chicago, Boston, Washington D.C.

**Features used (22 total):**
- 10 numerical: amenities count, accommodates, bathrooms, lat/lng, host response rate, reviews, rating, bedrooms, beds
- 9 categorical: property type, room type, bed type, cancellation policy, cleaning fee, city, host verification, instant bookable, host profile pic
- 3 engineered: rooms per person, beds per room, bathrooms per room

## Models Compared

| Model | Description |
|-------|-------------|
| Linear Regression | Baseline |
| Ridge / Lasso / ElasticNet | Regularized linear models |
| Random Forest | Ensemble of decision trees |
| Gradient Boosting | Sequential boosting |
| XGBoost | Extreme gradient boosting |
| LightGBM | Light gradient boosting machine |
| CatBoost | Categorical boosting |

Top 3 models are hyperparameter-tuned with Optuna (Bayesian optimization).

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI endpoints
│   │   ├── ml/           # ML pipeline (ingestion, transformation, training, prediction)
│   │   └── scraper/      # Airbnb URL scraper
│   ├── artifacts/        # Trained model + preprocessor
│   ├── data/             # Raw dataset
│   └── train.py          # Training entry point
├── frontend/
│   ├── src/
│   │   ├── components/   # React UI components
│   │   ├── pages/        # Home, Predictor, About
│   │   └── services/     # API client
│   └── index.html
├── docker-compose.yml
└── README.md
```

## License

MIT
