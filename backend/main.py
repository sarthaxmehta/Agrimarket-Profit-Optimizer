from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import joblib
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import functools
import datetime

app = FastAPI(title="AgriMarket Profit Optimizer API")

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "agrimarket.db"
MODEL_PATH = "model.pkl"
ENCODERS_PATH = "encoders.pkl"
TRANSPORTATION_COST_PER_KG_PER_KM = 3.6

print("Loading ML model and encoders...")
try:
    model = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODERS_PATH)
except:
    print("Warning: Model or encoders not found. Please train the model first.")
    model, encoders = None, None

geolocator = Nominatim(user_agent="agrimarket_profit_optimizer")

@functools.lru_cache(maxsize=1000)
def get_coordinates(city_name):
    """Cache coordinates to prevent Geopy API rate limits"""
    try:
        location = geolocator.geocode(city_name, timeout=10)
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Error geocoding {city_name}: {e}")
    return None

class PredictionRequest(BaseModel):
    state: str
    district: str
    market: str
    commodity: str # This maps to 'Group' in DB
    variety: str
    quantity_kg: float

@app.get("/locations")
def get_locations():
    """Fetch distinct states, districts, markets, commodities from DB"""
    try:
        conn = sqlite3.connect(DB_PATH)
        states = pd.read_sql_query('SELECT DISTINCT "State Name" FROM market_prices', conn)["State Name"].tolist()
        districts = pd.read_sql_query('SELECT DISTINCT "District Name", "State Name" FROM market_prices', conn)
        markets = pd.read_sql_query('SELECT DISTINCT "Market Name", "District Name" FROM market_prices', conn)
        commodities = pd.read_sql_query('SELECT DISTINCT "Group", "Market Name" FROM market_prices', conn)
        varieties = pd.read_sql_query('SELECT DISTINCT "Variety", "Group" FROM market_prices', conn)
        conn.close()
        
        # We can format this nicely or just return raw arrays
        return {
            "states": states,
            "districts": districts.to_dict(orient="records"),
            "markets": markets.to_dict(orient="records"),
            "commodities": commodities.to_dict(orient="records"),
            "varieties": varieties.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_best_market")
def predict_best_market(request: PredictionRequest):
    if model is None or encoders is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")
        
    conn = sqlite3.connect(DB_PATH)
    # Find all markets that sell this commodity and variety
    query = f'''
        SELECT DISTINCT "State Name", "District Name", "Market Name"
        FROM market_prices 
        WHERE "Group" = ? AND "Variety" = ?
    '''
    candidate_markets = pd.read_sql_query(query, conn, params=(request.commodity, request.variety))
    conn.close()

    if candidate_markets.empty:
        raise HTTPException(status_code=404, detail="No markets found for this commodity and variety.")

    results = []
    current_month = datetime.datetime.now().month
    current_year = datetime.datetime.now().year

    # Base coords
    base_coords = get_coordinates(request.district)
    
    # We also need to predict price at the user's chosen market
    def encode_safe(col, val):
        if val in encoders[col].classes_:
            return encoders[col].transform([val])[0]
        else:
            return 0 # Fallback to first class if unseen

    for _, row in candidate_markets.iterrows():
        c_state = row["State Name"]
        c_district = row["District Name"]
        c_market = row["Market Name"]
        
        # Prepare feature vector
        state_enc = encode_safe("State Name", c_state)
        district_enc = encode_safe("District Name", c_district)
        market_enc = encode_safe("Market Name", c_market)
        variety_enc = encode_safe("Variety", request.variety)
        group_enc = encode_safe("Group", request.commodity)
        
        features = pd.DataFrame([[state_enc, district_enc, market_enc, variety_enc, group_enc, current_month, current_year]], 
                                columns=["State Name", "District Name", "Market Name", "Variety", "Group", "Month", "Year"])
        
        # Predict Price per quintal (100kg)
        predicted_price_per_quintal = model.predict(features)[0]
        predicted_revenue = (predicted_price_per_quintal * request.quantity_kg) / 100.0
        
        # Distance calculation
        distance_km = 0
        if c_market != request.market:
            dest_coords = get_coordinates(c_district)
            if base_coords and dest_coords:
                distance_km = geodesic(base_coords, dest_coords).kilometers
            else:
                # If we can't geocode, assume very far or skip
                distance_km = 9999
                
        transport_cost = distance_km * request.quantity_kg * TRANSPORTATION_COST_PER_KG_PER_KM
        net_profit = predicted_revenue - transport_cost
        
        results.append({
            "market": c_market,
            "district": c_district,
            "state": c_state,
            "predicted_price_per_quintal": round(float(predicted_price_per_quintal), 2),
            "predicted_revenue": round(float(predicted_revenue), 2),
            "distance_km": round(distance_km, 2),
            "transport_cost": round(float(transport_cost), 2),
            "net_profit": round(float(net_profit), 2)
        })
    
    # Find user's chosen market profit to calculate relative profit
    chosen_market_result = next((r for r in results if r["market"] == request.market), None)
    chosen_profit = chosen_market_result["net_profit"] if chosen_market_result else 0
    
    for r in results:
        r["profit_relative_to_chosen"] = round(r["net_profit"] - chosen_profit, 2)
        
    # Sort by highest net profit
    results = sorted(results, key=lambda x: x["net_profit"], reverse=True)
    
    return {
        "chosen_market": chosen_market_result,
        "recommendations": results[:10] # Top 10 markets
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
