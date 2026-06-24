import os
import pandas as pd
import sqlite3
import datetime

# Configuration
DATASET_FOLDER = "../archive (9)"
DB_PATH = "agrimarket.db"
START_YEAR = 2018 # Last 8 years (current year 2026)

def process_data():
    print("Starting data processing...")
    files = [os.path.join(DATASET_FOLDER, f) for f in os.listdir(DATASET_FOLDER) if f.endswith(".csv")]
    
    dataframes = []
    total_files = len(files)
    
    for i, file in enumerate(files):
        if os.stat(file).st_size == 0:
            continue
        try:
            # Only read necessary columns
            df = pd.read_csv(file, usecols=["State Name", "District Name", "Market Name", "Variety", "Group", "Modal Price", "Reported Date"])
            
            if not df.empty:
                # Convert date and filter
                df['Reported Date'] = pd.to_datetime(df['Reported Date'], errors='coerce')
                df = df.dropna(subset=['Reported Date', 'Modal Price'])
                df = df[df['Reported Date'].dt.year >= START_YEAR]
                
                if not df.empty:
                    df['Year'] = df['Reported Date'].dt.year
                    df['Month'] = df['Reported Date'].dt.month
                    dataframes.append(df)
                    
            if (i + 1) % 50 == 0:
                print(f"Processed {i + 1}/{total_files} files...")
                
        except Exception as e:
            print(f"Error processing {file}: {e}")
            continue

    if not dataframes:
        print("No valid data found in the dataset.")
        return

    print("Concatenating dataframes...")
    main_df = pd.concat(dataframes, ignore_index=True)
    
    print(f"Total records after filtering: {len(main_df)}")
    
    # Save to SQLite Database
    print(f"Saving to SQLite database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    
    # We will save the cleaned data to 'market_prices' table
    main_df.to_sql('market_prices', conn, if_exists='replace', index=False)
    
    # Create indexes for faster querying
    cursor = conn.cursor()
    print("Creating indexes...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_group ON market_prices("Group");')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_state ON market_prices("State Name");')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_district ON market_prices("District Name");')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_market ON market_prices("Market Name");')
    
    conn.commit()
    conn.close()
    
    print("Data processing and database creation completed successfully!")

if __name__ == "__main__":
    process_data()
