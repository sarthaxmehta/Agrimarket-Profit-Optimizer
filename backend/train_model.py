import sqlite3
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.ensemble import HistGradientBoostingRegressor

DB_PATH = "agrimarket.db"
MODEL_PATH = "model.pkl"
ENCODERS_PATH = "encoders.pkl"

def train_model():
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    
    query = 'SELECT "State Name", "District Name", "Market Name", "Variety", "Group", "Month", "Year", "Modal Price" FROM market_prices'
    print("Reading data from DB...")
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("Error: No data found in the database. Run data_pipeline.py first.")
        return

    print(f"Data loaded: {len(df)} rows.")

    df = df.dropna()

    categorical_features = ["State Name", "District Name", "Market Name", "Variety", "Group"]
    numeric_features = ["Month", "Year"]

    encoders = {}
    print("Encoding categorical features...")
    for col in categorical_features:
        le = LabelEncoder()
        df[col] = df[col].astype(str)
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    X = df[categorical_features + numeric_features]
    y = df["Modal Price"]

    print("Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training HistGradientBoostingRegressor (this may take a while)...")
    # HistGradientBoostingRegressor is fast and native to sklearn
    model = HistGradientBoostingRegressor(max_iter=100, max_depth=6, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    print("Evaluating model...")
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Performance -> MAE: {mae:.2f}, R-squared: {r2:.4f}")

    print("Saving model and encoders...")
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODERS_PATH)
    print("Done!")

if __name__ == "__main__":
    train_model()
