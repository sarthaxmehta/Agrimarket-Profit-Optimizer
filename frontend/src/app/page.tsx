"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [locations, setLocations] = useState<any>({ states: [], districts: [], markets: [], commodities: [], varieties: [] });
  const [formData, setFormData] = useState({ state: "", district: "", market: "", commodity: "", variety: "", quantity_kg: 100 });
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    // Using 127.0.0.1 instead of localhost to prevent IPv6 binding issues that might cause Failed to fetch
    fetch("http://127.0.0.1:8001/locations")
      .then(res => res.json())
      .then(data => setLocations(data))
      .catch(err => {
        console.error("Error fetching locations:", err);
        setError("Failed to connect to backend API. Please make sure the Python server is running.");
      });
  }, []);

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const res = await fetch("http://127.0.0.1:8001/predict_best_market", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...formData, quantity_kg: Number(formData.quantity_kg) })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Something went wrong");
      setResults(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredDistricts = locations.districts.filter((d: any) => d["State Name"] === formData.state);
  const filteredMarkets = locations.markets.filter((m: any) => m["District Name"] === formData.district);
  const filteredCommodities = locations.commodities.filter((c: any) => c["Market Name"] === formData.market);
  // Get unique commodities
  const uniqueCommodities = Array.from(new Set(filteredCommodities.map((c: any) => c["Group"])));
  const filteredVarieties = locations.varieties.filter((v: any) => v["Group"] === formData.commodity);
  const uniqueVarieties = Array.from(new Set(filteredVarieties.map((v: any) => v["Variety"])));

  return (
    <main className="min-h-screen p-8 md:p-24 relative overflow-hidden">
      <div className="max-w-6xl mx-auto space-y-12 relative z-10">
        <div className="text-center space-y-4">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600 drop-shadow-sm">
            AgriMarket
          </h1>
          <p className="text-xl text-slate-600 font-medium">
            AI-Powered Profit Optimization for Farmers
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          {/* Input Form */}
          <div className="glass-panel p-8 lg:col-span-1">
            <h2 className="text-2xl font-bold mb-6 text-slate-800">Your Produce</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              
              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">State</label>
                <select 
                  className="w-full p-3 rounded-xl glass-input"
                  value={formData.state}
                  onChange={e => setFormData({ ...formData, state: e.target.value, district: "", market: "", commodity: "", variety: "" })}
                  required
                >
                  <option value="">Select State</option>
                  {locations.states.map((state: string) => (
                    <option key={state} value={state}>{state}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">District</label>
                <select 
                  className="w-full p-3 rounded-xl glass-input disabled:opacity-50"
                  value={formData.district}
                  onChange={e => setFormData({ ...formData, district: e.target.value, market: "", commodity: "", variety: "" })}
                  disabled={!formData.state}
                  required
                >
                  <option value="">Select District</option>
                  {filteredDistricts.map((d: any, i: number) => (
                    <option key={i} value={d["District Name"]}>{d["District Name"]}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Local Market</label>
                <select 
                  className="w-full p-3 rounded-xl glass-input disabled:opacity-50"
                  value={formData.market}
                  onChange={e => setFormData({ ...formData, market: e.target.value, commodity: "", variety: "" })}
                  disabled={!formData.district}
                  required
                >
                  <option value="">Select Market</option>
                  {filteredMarkets.map((m: any, i: number) => (
                    <option key={i} value={m["Market Name"]}>{m["Market Name"]}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Commodity Group</label>
                <select 
                  className="w-full p-3 rounded-xl glass-input disabled:opacity-50"
                  value={formData.commodity}
                  onChange={e => setFormData({ ...formData, commodity: e.target.value, variety: "" })}
                  disabled={!formData.market}
                  required
                >
                  <option value="">Select Commodity</option>
                  {uniqueCommodities.map((c: any, i: number) => (
                    <option key={i} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Variety</label>
                <select 
                  className="w-full p-3 rounded-xl glass-input disabled:opacity-50"
                  value={formData.variety}
                  onChange={e => setFormData({ ...formData, variety: e.target.value })}
                  disabled={!formData.commodity}
                  required
                >
                  <option value="">Select Variety</option>
                  {uniqueVarieties.map((v: any, i: number) => (
                    <option key={i} value={v}>{v}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-slate-700">Quantity (Kg)</label>
                <input 
                  type="number"
                  className="w-full p-3 rounded-xl glass-input"
                  value={formData.quantity_kg}
                  onChange={e => setFormData({ ...formData, quantity_kg: Number(e.target.value) })}
                  min="1"
                  required
                />
              </div>

              <button 
                type="submit" 
                disabled={loading}
                className="w-full py-4 mt-6 rounded-xl text-emerald-800 font-bold text-lg glass-button disabled:opacity-50"
              >
                {loading ? "Analyzing Markets..." : "Find Best Market"}
              </button>

            </form>
          </div>

          {/* Results Area */}
          <div className="lg:col-span-2 space-y-6">
            {error && (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-700 backdrop-blur-md">
                {error}
              </div>
            )}

            {!results && !error && !loading && (
              <div className="glass-panel p-12 text-center flex flex-col items-center justify-center min-h-[500px]">
                <div className="w-24 h-24 mb-6 rounded-full bg-white/40 shadow-sm flex items-center justify-center border border-white/60">
                  <span className="text-5xl">🌾</span>
                </div>
                <h3 className="text-2xl font-bold text-slate-800 mb-2">Ready to optimize your profit?</h3>
                <p className="text-slate-600 font-medium">Enter your produce details to discover the most profitable market, considering predictive pricing and transportation costs.</p>
              </div>
            )}

            {results && (
              <div className="space-y-6">
                
                {results.chosen_market && (
                  <div className="glass-panel p-6 border-l-4 border-l-teal-500 bg-white/50">
                    <h3 className="text-xs font-black text-teal-600 uppercase tracking-widest mb-2">Your Local Market</h3>
                    <div className="flex justify-between items-end">
                      <div>
                        <p className="text-2xl font-extrabold text-slate-800">{results.chosen_market.market}</p>
                        <p className="text-sm font-semibold text-slate-500">Price: ₹{results.chosen_market.predicted_price_per_quintal} / quintal</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs font-bold text-slate-500 uppercase tracking-wide">Est. Revenue</p>
                        <p className="text-3xl font-black text-teal-600">₹{results.chosen_market.predicted_revenue}</p>
                      </div>
                    </div>
                  </div>
                )}

                <h3 className="text-2xl font-extrabold text-slate-800 pt-4">Top Recommended Markets</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {results.recommendations.map((market: any, idx: number) => (
                    <div key={idx} className={`glass-panel p-6 relative overflow-hidden ${idx === 0 ? 'ring-2 ring-emerald-400 bg-emerald-50/50' : 'bg-white/30'}`}>
                      {idx === 0 && (
                        <div className="absolute top-0 right-0 bg-gradient-to-bl from-emerald-400 to-teal-500 text-white text-[10px] uppercase tracking-widest font-black px-4 py-1 rounded-bl-xl shadow-sm">
                          Top Choice
                        </div>
                      )}
                      <h4 className="text-xl font-extrabold text-slate-800 mb-1">{market.market}</h4>
                      <p className="text-sm font-medium text-slate-500 mb-5">{market.district}, {market.state}</p>
                      
                      <div className="space-y-3 text-sm">
                        <div className="flex justify-between items-center text-slate-600">
                          <span className="font-semibold">Est. Revenue</span>
                          <span className="font-bold text-slate-800">₹{market.predicted_revenue}</span>
                        </div>
                        <div className="flex justify-between items-center text-rose-500 font-medium">
                          <span>Transport Cost ({market.distance_km === 9999 ? 'Unknown' : market.distance_km + 'km'})</span>
                          <span>-₹{market.transport_cost}</span>
                        </div>
                        
                        <div className="w-full h-px bg-slate-300/50 my-2"></div>
                        
                        <div className="flex justify-between items-center mt-3">
                          <span className="font-black text-slate-700">Net Profit</span>
                          <span className="text-2xl font-black text-emerald-600">₹{market.net_profit}</span>
                        </div>
                        
                        {market.profit_relative_to_chosen > 0 && (
                          <div className="mt-4 inline-flex px-3 py-1.5 bg-emerald-100/80 border border-emerald-200 rounded-full text-emerald-700 text-xs font-bold shadow-sm">
                            +₹{market.profit_relative_to_chosen} vs Local Market
                          </div>
                        )}
                        {market.profit_relative_to_chosen < 0 && (
                          <div className="mt-4 inline-flex px-3 py-1.5 bg-rose-100/80 border border-rose-200 rounded-full text-rose-700 text-xs font-bold shadow-sm">
                            -₹{Math.abs(market.profit_relative_to_chosen)} vs Local Market
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
