import os
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

TRANSPORTATION_COST_PER_KG_PER_KM = 3.6
DATASET_FOLDER = r"C:\Users\munis\Downloads\Dataset"
def load_data(folder_path):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".csv")]
    dataframes = []
    
    for file in files:
        if os.stat(file).st_size == 0:
            continue
        try:
            df = pd.read_csv(file)
            if not df.empty:
                dataframes.append(df)
        except pd.errors.EmptyDataError:
            continue
    print("DATA HAS BEEN LOADED SUCCESSFULLY")
    return pd.concat(dataframes, ignore_index=True)
def get_latest_data(df):
    latest_date = df["Reported Date"].max()
    return df[df["Reported Date"] == latest_date]
    
print("Loading data...")
data = load_data(DATASET_FOLDER)
data = get_latest_data(data)
def select_option(options, prompt):
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    choice = int(input("Enter the number of your choice: "))
    return options[choice - 1]

def calculate_distance(city1, city2):
    geolocator = Nominatim(user_agent="city_distance_calculator")

    def get_coordinates(city):
        location = geolocator.geocode(city)
        if location:
            return (location.latitude, location.longitude)
        return None

    coords_1 = get_coordinates(city1)
    coords_2 = get_coordinates(city2)

    if coords_1 and coords_2:
        return geodesic(coords_1, coords_2).kilometers
    else:
        print("Could not calculate distance due to missing coordinates or if the best market is your own district.")
        return float("inf")

def calculate_transport_cost(distance_km, weight_kg):
    return distance_km * weight_kg * TRANSPORTATION_COST_PER_KG_PER_KM
def main():

    states = data["State Name"].unique().tolist()
    state = select_option(states, "Select your state:")

    districts = data[data["State Name"] == state]["District Name"].unique().tolist()
    district = select_option(districts, "Select your district:")

    markets = data[data["District Name"] == district]["Market Name"].unique().tolist()
    market = select_option(markets, "Select your market:")

    commodities = data[data["Market Name"] == market]["Group"].unique().tolist()
    if not commodities:
        print("No commodities available in the selected market.")
        return
    commodity = select_option(commodities, "Select the commodity you want to sell:")

    market_data = data[(data["Market Name"] == market) & (data["Group"] == commodity)]
    if market_data.empty:
        print("No data available for the selected market and commodity.")
        return

    varieties = market_data["Variety"].unique().tolist()
    variety = select_option(varieties, "Select the variety of the commodity:")

    quantity = float(input("Enter the quantity (in kg) you want to sell: "))
    
    main_data = data[(data["State Name"] == state) & 
                     (data["Group"] == commodity) & 
                     (data["Variety"] == variety)].copy()

    print("Calculating best market options...")
    profits = []
     
    selling_price_user_market = (market_data.loc[market_data["Market Name"] == market, "Modal Price (Rs./Quintal)"].values[0]* quantity/ 100)

    print(f"Selling price at your chosen market: Rs. {selling_price_user_market:.2f}")

    profits = []

    for _, row in main_data.iterrows():
        if row["Market Name"] == market:
            net_selling_price = row["Modal Price (Rs./Quintal)"] * quantity / 100
        else:
         
            distance = calculate_distance(district, row["District Name"])
            transport_cost = calculate_transport_cost(distance, quantity)
            net_selling_price = (row["Modal Price (Rs./Quintal)"] * quantity / 100) + transport_cost
     
        profit_difference = net_selling_price - selling_price_user_market
        profits.append(profit_difference)
        
    main_data.loc[:, "Profit Relative to Chosen Market"] = profits
    best_market = main_data.loc[main_data["Profit Relative to Chosen Market"].idxmax()]

    if district == best_market['District Name']:
        print(f"The best market to sell your produce is your own market in {district}, Congratulations!")
    else:
        print(f"Best market for maximum profit relative to your chosen market: {best_market['Market Name']}")
        print(f"Profit relative to your market: Rs. {best_market['Profit Relative to Chosen Market']:.2f}")
        
        distance = calculate_distance(district, best_market['District Name'])
        if distance != float("inf"):
            print(f"Distance to the market: {distance:.2f} km.")

if __name__ == "__main__":
    main()
