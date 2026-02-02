from fastapi import FastAPI, HTTPException
import xgboost as xgb
import pandas as pd
import numpy as np
from pathlib import Path

app = FastAPI()

# load model and history data
model = xgb.XGBRegressor()
ROOT = Path(__file__).resolve().parent

model_path = ROOT / "energy_model.json"
if not model_path.exists():
    raise FileNotFoundError(f"Model file not found: {model_path}")
model.load_model(str(model_path))

data_path = ROOT / "input" / "PJME_hourly.csv"
if not data_path.exists():
    raise FileNotFoundError(f"History data file not found: {data_path}")
history = pd.read_csv(str(data_path), index_col="Datetime", parse_dates=True)
if not isinstance(history.index, pd.DatetimeIndex):
    raise ValueError("History index is not datetime. Check the Datetime column in input data.")
history = history.sort_index()
if history.index.tz is not None:
    history.index = history.index.tz_convert(None)

# API endpoints
@app.get("/")
def root():
    return {"status": "ok", "message": "Use /predict?date_str=YYYY-MM-DD HH:MM:SS"}


@app.get("/health")
def health():
    return {"status": "ok"}

# Feature engineering
def build_features(target_date: pd.Timestamp) -> pd.DataFrame:
    if target_date.tz is not None:
        target_date = target_date.tz_convert(None)
    df = pd.DataFrame(index=[target_date])

    df["hour"] = df.index.hour
    df["dayofweek"] = df.index.dayofweek
    df["quarter"] = df.index.quarter
    df["month"] = df.index.month
    df["year"] = df.index.year
    df["dayofyear"] = df.index.dayofyear
    df["dayofmonth"] = df.index.day
    df["weekofyear"] = df.index.isocalendar().week.astype(int)

    def get_lag_value(lag_ts: pd.Timestamp) -> float:
        if lag_ts in history.index:
            return float(history.loc[lag_ts, "PJME_MW"])
        lag_idx = history.index[history.index <= lag_ts]
        if len(lag_idx) == 0:
            raise ValueError(f"No history data available on or before {lag_ts}")
        return float(history.loc[lag_idx[-1], "PJME_MW"])

    df["lag_7d"] = get_lag_value(target_date - pd.Timedelta("7 days"))
    df["lag_28d"] = get_lag_value(target_date - pd.Timedelta("28 days"))
    df["lag_1y"] = get_lag_value(target_date - pd.Timedelta("364 days"))
    df["lag_2y"] = get_lag_value(target_date - pd.Timedelta("728 days"))
    df["lag_3y"] = get_lag_value(target_date - pd.Timedelta("1092 days"))

    feature_order = [
        "hour",
        "dayofweek",
        "quarter",
        "month",
        "year",
        "dayofyear",
        "dayofmonth",
        "weekofyear",
        "lag_7d",
        "lag_28d",
        "lag_1y",
        "lag_2y",
        "lag_3y",
    ]
    df = df[feature_order]
    return df

@app.get("/predict")
def predict(date_str: str):
    # validation and feature building
    try:
        target_date = pd.to_datetime(date_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD HH:MM:SS")
    try:
        df = build_features(target_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    
    # prediction
    prediction = model.predict(df)
    return {"datetime": date_str, "prediction_MW": float(prediction[0])}
