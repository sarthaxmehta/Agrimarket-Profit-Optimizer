# 🌾 AgriMarket Profit Optimizer

AgriMarket Profit Optimizer is a **Full-Stack Machine Learning Application** designed to empower farmers in India. By leveraging historical agricultural data, the application predicts future crop prices and calculates optimal market destinations by factoring in real-time geographic distances and transportation costs.

This ensures farmers achieve the **maximum possible net profit** for their produce.

![AgriMarket Demo](https://img.shields.io/badge/Status-Active-brightgreen) ![Tech Stack](https://img.shields.io/badge/Stack-Next.js%20%7C%20FastAPI%20%7C%20Scikit--Learn-blue)

---

## ✨ Features

- **Predictive Pricing Model**: Utilizes a highly optimized `HistGradientBoostingRegressor` trained on over 3.5 Million records spanning the last 8 years to predict modal prices per quintal.
- **Intelligent Transport Cost Calculation**: Integrates with `Geopy` to calculate precise real-world distances between the farmer's local market and alternative markets, automatically deducting transportation overhead.
- **Next-Gen Aesthetics**: A gorgeous "Light Liquid Glassmorphism" frontend built with **Next.js 15**, **React**, and **Tailwind CSS 4**.
- **Blazing Fast Backend**: A robust **FastAPI** Python backend utilizing a highly optimized SQLite database for millisecond querying of geographic metadata.

---

## 🛠️ Architecture & Tech Stack

### 1. Data Engineering (`backend/data_pipeline.py`)
- Ingested 325 independent CSV files containing historical Mandi prices.
- Cleaned, normalized, and optimized over **3.5 Million rows**.
- Stored safely into `agrimarket.db` with database indexing for instant retrieval.

### 2. Machine Learning (`backend/train_model.py`)
- **Scikit-Learn**: `HistGradientBoostingRegressor`
- Engineered features include `State`, `District`, `Market`, `Commodity Group`, `Variety`, `Month`, and `Year`.
- The model and categorical encoders are pickled (`joblib`) to ensure rapid backend inference without retraining.

### 3. Backend API (`backend/main.py`)
- **FastAPI** + **Uvicorn**
- `/locations`: Dynamic endpoint fetching all available locations, commodities, and varieties for dropdown population.
- `/predict_best_market`: The core ML endpoint. Evaluates all candidate markets, calculates geodesic distances, estimates transportation costs, and returns the top 10 most profitable markets.

### 4. Frontend Web App (`frontend/`)
- **Next.js 15** + **Tailwind CSS**
- State-of-the-art interactive Dashboard with real-time UI updates, dynamic form rendering, and visually striking profit comparisons.

---

## 🚀 How to Run Locally

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**

### 1. Backend Setup
Navigate to the `backend` directory, set up your Python virtual environment, install dependencies, and run the FastAPI server:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pandas scikit-learn geopy joblib
uvicorn main:app --host 0.0.0.0 --port 8001
```
*(Note: Ensure the data pipeline and model training scripts have been executed beforehand if `agrimarket.db` and `.pkl` files are not present).*

### 2. Frontend Setup
Navigate to the `frontend` directory, install NPM dependencies, and start the Next.js development server:

```bash
cd frontend
npm install
npm run dev
```

### 3. Usage
Open your browser and navigate to **http://localhost:3002**.
1. Select your State, District, and Local Market.
2. Choose your Commodity and Variety.
3. Enter the Quantity you wish to sell (in Kg).
4. Click **Find Best Market** to instantly discover your most profitable selling destinations!

---

## 📂 Repository Structure

```text
├── backend/
│   ├── data_pipeline.py      # Cleans CSVs and builds agrimarket.db
│   ├── train_model.py        # Trains the HistGradientBoostingRegressor
│   └── main.py               # FastAPI application
├── frontend/
│   ├── src/app/page.tsx      # Core React Dashboard UI
│   ├── src/app/globals.css   # Tailwind CSS & Glassmorphism Design System
│   └── next.config.ts        # Next.js Configuration
└── README.md                 # Project Documentation
```

## 🤝 Contribution & License
This project was developed for advanced predictive analytics in the agricultural space. Open for contributions, improvements, and feature requests. Feel free to open an Issue or PR!
