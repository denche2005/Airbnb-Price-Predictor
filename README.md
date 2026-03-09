# Airbnb Price Predictor (Worldwide)

ML‑powered web app that predicts the **fair nightly price** of any Airbnb listing worldwide.  
Paste an Airbnb URL or fill a short form and the app estimates a price in the **local currency**, plus a confidence range and feature importance.

> Built by **Denys Cherednychenko** — [LinkedIn](https://www.linkedin.com/in/denys-cherednychenko2005/) · [GitHub](https://github.com/denche2005)

---

## ✨ What this project shows

- **End‑to‑end ML system**: from raw Airbnb data → feature engineering → model training → API → React UI.
- **Modern stack**: FastAPI backend, React + Vite + Tailwind frontend, Playwright scraping, Optuna hyperparameter tuning.
- **Product feel**: Airbnb‑inspired UI, URL‑based predictions, confidence intervals, feature importance chart.

This is designed as a **portfolio project** that recruiters can both read and _use_.

---

## 🧠 Model & Data

- **Data source**: [Inside Airbnb](http://insideairbnb.com/get-the-data)
  - ~24 major cities across **6 continents** (New York, London, Paris, Tokyo, Barcelona, Sydney, etc.)
  - ~500K listings combined.
- **Features (~45+)**:
  - Location: city, country, latitude/longitude.
  - Property: accommodates, bedrooms, beds, bathrooms, minimum nights, availability.
  - Host: superhost flag, response rate, acceptance rate, listings count.
  - Reviews: number of reviews, reviews/month, overall rating + detailed sub‑scores.
  - Amenities: total count + key binary flags (elevator, pool, A/C, wifi, etc.).
- **Target**: log‑price of nightly rate (per city’s local currency).
- **Models compared**:
  - Linear, Ridge, Lasso, ElasticNet
  - RandomForest, GradientBoosting
  - **XGBoost, LightGBM, CatBoost**
- **Final model**: `XGBoost_tuned` with Optuna
  - R² (test) ≈ **0.97**
  - RMSE ≈ **0.36** (log‑space)
  - 5‑fold CV R² ≈ **0.97**

The app also returns the **top features by importance** so users can see what drives pricing.

---

## 🏗️ Architecture

**Backend (Python / FastAPI)**

- `backend/download_data.py`: downloads `listings.csv.gz` for 24+ cities from Inside Airbnb.
- `app/ml/data_ingestion.py`: merges datasets, cleans & parses price, reviews, amenities, etc.
- `app/ml/data_transformation.py`: feature engineering + `ColumnTransformer` preprocessing.
- `app/ml/model_trainer.py`: trains 9 baseline models + Optuna tuning on top 3.
- `app/ml/prediction_pipeline.py`: loads artifacts and runs predictions.
- `app/api/predict.py`: `/api/predict` endpoint (JSON payload).
- `app/api/scrape.py`: `/api/scrape` endpoint — scrapes an Airbnb URL and then predicts.
- `app/scraper/airbnb_scraper.py`: Playwright‑based scraper with Windows‑friendly async handling.

**Frontend (React / Vite / Tailwind)**

- `pages/Home`: marketing‑style landing (worldwide stats, how it works).
- `pages/Predictor`: main tool — tabs for **Paste URL** and **Manual input**.
- `components/PredictionForm`: rich form with amenity toggles and city selector.
- `components/PriceResult`: predicted price + confidence interval in local currency.
- `components/FeatureImportanceChart`: Recharts bar chart of top features.
- UI inspired by Airbnb (colors, layout, typography).

**Deployment**

- `docker-compose.yml` orchestrates:
  - FastAPI backend
  - React frontend served by Nginx
- Separate `Dockerfile` for backend and frontend.

---

## 🚀 Quickstart (local)

Requirements:

- Python 3.10+  
- Node.js 18+  
- (Optional) Docker & Docker Compose

### 1. Clone & install

```bash
git clone https://github.com/denche2005/Airbnb-Price-Predictor.git
cd Airbnb-Price-Predictor

# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # en Windows
pip install -r requirements.txt
```

### 2. Download data & train model

```bash
# Descargar datos de Inside Airbnb (24 ciudades)
python download_data.py

# Entrenar el modelo mundial (puede tardar)
python train.py
```

Esto genera los artefactos en `backend/artifacts/` (`model.pkl`, `preprocessor.pkl`, `metrics.json`, etc.).

### 3. Run backend

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API docs: `http://127.0.0.1:8000/docs`

### 4. Run frontend

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

- UI: `http://127.0.0.1:5173/`

---

## 🧑‍💻 How to use

1. Open the app in your browser.
2. Go to the **Predictor** page.
3. Choose:
   - **Paste URL**: pega un link de Airbnb (por ejemplo, `.com`, `.es`, etc.) y el sistema:
     - Usa Playwright para scrapear detalles básicos.
     - Predice el precio nocturno en la **moneda local**.
   - **Manual input**: rellena ciudad, habitaciones, reviews, amenities, etc.
4. Revisa:
   - Precio estimado
   - Rango de confianza
   - Variables más importantes para ese caso.

---

## 🧩 Why this project

I built this to demonstrate:

- Ability to **own an ML project end‑to‑end** (data, modeling, infra, UX).
- Comfort with **modern Python ML stack** (pandas, scikit‑learn, XGBoost/LightGBM/CatBoost, Optuna).
- Experience building **production‑style APIs** (FastAPI) and **frontends** (React + Tailwind).
- Practical understanding of **real‑world data issues** (different currencies, messy amenities, missing values, etc.).

If you’d like a quick walkthrough or want to discuss the design/trade‑offs, feel free to reach out on [LinkedIn](https://www.linkedin.com/in/denys-cherednychenko2005/).

