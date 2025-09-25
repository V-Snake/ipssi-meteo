from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import random
from datetime import datetime

# Créer l'application FastAPI
app = FastAPI(title="KiteSurf Weather API", version="2.0.0")

# Configuration CORS la plus permissive pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Données statiques des spots
SPOTS = [
    {"type": "node", "id": 1001, "lat": 43.6047, "lon": 1.4442, "tags": {"name": "Lac de la Ramée"}},
    {"type": "node", "id": 1002, "lat": 43.6547, "lon": 1.4042, "tags": {"name": "Base nautique de Sesquières"}},
    {"type": "node", "id": 1003, "lat": 43.5847, "lon": 1.3842, "tags": {"name": "Lac de Reynerie"}},
    {"type": "node", "id": 1004, "lat": 43.6247, "lon": 1.5042, "tags": {"name": "Port Sud Toulouse"}},
    {"type": "node", "id": 1005, "lat": 43.5647, "lon": 1.4642, "tags": {"name": "Base de loisirs de Roques"}},
]

def create_mock_weather():
    """Génère des données météo réalistes"""
    conditions = ["Sunny", "Partly cloudy", "Cloudy", "Light rain"]
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    
    return {
        "location": {
            "name": f"Weather Station",
            "region": "Toulouse",
            "country": "France"
        },
        "current": {
            "temp_c": round(random.uniform(15.0, 28.0), 1),
            "condition": {
                "text": random.choice(conditions),
                "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png"
            },
            "wind_kph": round(random.uniform(8.0, 35.0), 1),
            "wind_dir": random.choice(directions),
            "humidity": random.randint(45, 85),
            "pressure_mb": round(random.uniform(1005.0, 1025.0), 1),
            "vis_km": round(random.uniform(8.0, 25.0), 1)
        }
    }

@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return JSONResponse({
        "message": "🏄‍♂️ KiteSurf Weather API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "/": "API info",
            "/weather": "Weather data by coordinates",
            "/kitesurf-spots": "Kitesurf spots list"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.get("/weather")
async def get_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """Retourne les données météo pour des coordonnées"""
    try:
        weather = create_mock_weather()
        weather["location"]["lat"] = lat
        weather["location"]["lon"] = lon
        weather["location"]["name"] = f"Spot {lat:.3f},{lon:.3f}"
        
        return JSONResponse({
            "status": "ok",
            "data": weather
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.get("/kitesurf-spots")
async def get_spots():
    """Retourne la liste des spots de kitesurf"""
    return JSONResponse({
        "status": "ok", 
        "count": len(SPOTS),
        "elements": SPOTS
    })

# Gestion des requêtes OPTIONS pour CORS
@app.options("/weather")
async def options_weather():
    return JSONResponse({"status": "ok"})

@app.options("/kitesurf-spots")  
async def options_spots():
    return JSONResponse({"status": "ok"})

if __name__ == "__main__":
    print("🚀 Démarrage KiteSurf Weather API v2.0.0")
    print("📍 URL: http://localhost:8001")
    print("📚 Docs: http://localhost:8001/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        access_log=True
    )