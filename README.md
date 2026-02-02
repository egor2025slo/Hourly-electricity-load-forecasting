# Time-Series Load Forecasting (PJME) — FastAPI Service

This project forecasts hourly electricity load using historical PJME data. It is built to practice time-series ML and demonstrate an end-to-end ML-to-API workflow.

## What this project does
- **Goal:** predict PJME_MW (electric load) for a given datetime.
- **Approach:** feature engineering (calendar features + lag features) and XGBoost regression.
- **Serving:** FastAPI endpoint `/predict` that returns a numeric forecast.
- **Packaging:** Dockerized for reproducible deployment.

## Why it matters (business context)
Load forecasting supports:
- **Capacity planning:** anticipate peak hours and seasonal demand.
- **Operational efficiency:** optimize generation scheduling and purchases.
- **Grid stability:** better planning reduces overload risk and imbalance penalties.
- **Customer analytics:** demand patterns by time improve tariff and demand-response strategies.

## Dataset
- PJME hourly load data (`input/PJME_hourly.csv`)
- Target column: `PJME_MW`

## Model and features
The notebook builds features and trains an XGBoost model:
- **Calendar features:** hour, day of week, month, quarter, year, day of year, day of month, week of year
- **Lag features:** 7d, 28d, 1y (364d), 2y (728d), 3y (1092d)

The trained model is saved as `energy_model.json` and loaded by the API.

## Project structure
```
.
├── main.py                         # FastAPI app
├── tutorial-time-series-forecasting-with-ml.ipynb
├── energy_model.json               # Trained model
├── input/
│   └── PJME_hourly.csv             # Source data
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

## Run locally
```bash
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Open:
- `http://localhost:8000/docs`
- `http://localhost:8000/health`

Example:
```
http://localhost:8000/predict?date_str=2018-08-03 00:00:00
```

## Run with Docker
```bash
docker build -t you_tube_video_iskra:latest .
docker run -d --name you_tube_video_iskra_app -p 8000:8000 you_tube_video_iskra:latest
```

## API
### GET /predict
Query params:
- `date_str` (string, `YYYY-MM-DD HH:MM:SS`)

Response:
```json
{
  "datetime": "2018-08-03 00:00:00",
  "prediction_MW": 12345.67
}
```

### GET /health
Simple health check:
```json
{ "status": "ok" }
```

## Resume talking points
- **Business framing:** how demand forecasts reduce cost and improve grid reliability.
- **Feature design:** calendar + multi-horizon lag signals capture weekly and yearly seasonality.
- **Serving:** model wrapped as an API with validation and Dockerized deployment.
- **Next improvements:** model/versioning, monitoring, input data validation, and retraining pipeline.
