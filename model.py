import pandas as pd
import joblib
import os
from prophet import Prophet

MODEL_PATH = "prophet_model.pkl"


# ==============================
# 1️⃣ PREPARE DATA
# ==============================
def prepare_prophet_data(df):
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month

    monthly = df.groupby(["year", "month"])["Amount"].sum().reset_index()

    monthly["ds"] = pd.to_datetime(
        monthly["year"].astype(str) + "-" + monthly["month"].astype(str) + "-01"
    )
    monthly["y"] = monthly["Amount"]

    return monthly[["ds", "y"]]


# ==============================
# 2️⃣ TRAIN MODEL
# ==============================
def train_model(df):
    prophet_df = prepare_prophet_data(df)

    if len(prophet_df) < 3:
        return None

    model = Prophet(
        growth='linear',
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False
    )

    model.fit(prophet_df)

    joblib.dump(model, MODEL_PATH)
    return model


# ==============================
# 3️⃣ LOAD MODEL
# ==============================
def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None


# ==============================
# 4️⃣ PREDICT NEXT MONTH (FINAL)
# ==============================
def predict_next_month(model, df):
    prophet_df = prepare_prophet_data(df)

    # fallback if less data
    if len(prophet_df) < 3:
        avg = prophet_df["y"].mean()
        return round(avg, 2), round(avg*0.9,2), round(avg*1.1,2), "Not enough data"

    future = model.make_future_dataframe(periods=1, freq='MS')
    forecast = model.predict(future)

    prediction = forecast.iloc[-1]["yhat"]

    last_value = prophet_df["y"].iloc[-1]
    avg_value = prophet_df["y"].mean()

    # 🔥 HARD LIMIT
    max_limit = last_value * 1.3
    min_limit = last_value * 0.7

    if prediction > max_limit:
        prediction = max_limit
    elif prediction < min_limit:
        prediction = min_limit

    # 🔥 SMOOTHING
    prediction = (prediction * 0.7) + (avg_value * 0.3)

    # 🔥 RANGE
    lower = prediction * 0.9
    upper = prediction * 1.1

    # 🔥 AI INSIGHT
    if prediction > last_value:
        insight = "📈 Spending trend increasing"
    elif prediction < last_value:
        insight = "📉 Spending trend decreasing"
    else:
        insight = "➖ Spending stable"

    return round(prediction, 2), round(lower,2), round(upper,2), insight


# ==============================
# 5️⃣ FORECAST FOR GRAPH
# ==============================
def get_forecast(model, df):
    future = model.make_future_dataframe(periods=3, freq='M')
    forecast = model.predict(future)
    return forecast



