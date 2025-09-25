# 🌊 KiteSurf Weather API

> Backend FastAPI pour le dashboard météorologique kitesurf

## 🚀 Démarrage Rapide

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
```bash
# Copier le fichier d'exemple
cp config.env.example config.env

# Éditer vos variables d'environnement
nano config.env
```

### Lancement
```bash
# Démarrage standard
python app_stable.py

# Mode développement avec auto-reload
python -m uvicorn app_stable:app --reload --port 8001
```

L'API sera disponible sur http://localhost:8001

## 📊 Endpoints Disponibles

### 🏠 Endpoints Principaux

- **GET /** - Accueil de l'API avec informations de base
- **GET /api/spots** - Liste complète des spots avec données météo
- **GET /api/weather/{spot_id}** - Données météo détaillées pour un spot
- **GET /docs** - Documentation Swagger interactive
- **GET /redoc** - Documentation ReDoc alternative

### 📝 Exemples de Réponse

**GET /api/spots**
```json
[
  {
    "id": "hossegor",
    "name": "Hossegor",
    "location": {
      "lat": 43.6618,
      "lng": -1.4085
    },
    "weather": {
      "temperature": 22,
      "wind_speed": 18,
      "wind_direction": 270,
      "conditions": "sunny"
    },
    "kite_score": 85,
    "level": "excellent"
  }
]
```

## ⚙️ Configuration

### Variables d'Environnement (config.env)

```env
# Configuration API
API_NAME=KiteSurf Weather API
API_VERSION=2.0.0
DEBUG_MODE=true

# Configuration serveur
HOST=0.0.0.0
PORT=8001

# Configuration CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Clés API (si nécessaire)
WEATHER_API_KEY=your_api_key_here
```

## 🧮 Algorithme de Scoring

Le système de scoring évalue la praticabilité d'un spot sur 100 points :

### Critères d'Évaluation

1. **Vent (40%)**
   - Force du vent (optimal 15-25 knots)
   - Direction (offshore/onshore/side)
   - Régularité

2. **Météo Générale (30%)**
   - Conditions atmosphériques
   - Visibilité
   - Précipitations

3. **Conditions Mer (20%)**
   - État de la mer
   - Marées
   - Courants

4. **Sécurité (10%)**
   - Obstacles
   - Zone de navigation
   - Conditions de sauvetage

### Classification des Scores

- **🟢 Excellent (67-100)** : Conditions idéales
- **🟠 Modéré (34-66)** : Praticable avec expérience
- **🔴 Difficile (0-33)** : Conditions dangereuses

## 📦 Dépendances

### Production
- **FastAPI** - Framework web moderne
- **Uvicorn** - Serveur ASGI
- **Pydantic** - Validation des données
- **Python-dateutil** - Manipulation des dates

### Développement
- **Pytest** - Tests unitaires
- **Black** - Formatage du code
- **Flake8** - Linting

## 🔧 Structure du Code

```python
# app_stable.py - Structure principale

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configuration de l'application
app = FastAPI(title="KiteSurf Weather API", version="2.0.0")

# Configuration CORS
app.add_middleware(CORSMiddleware, ...)

# Routes API
@app.get("/")
@app.get("/api/spots")
@app.get("/api/weather/{spot_id}")

# Lancement du serveur
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

## 🧪 Tests et Développement

### Lancement des Tests
```bash
# Tests unitaires
pytest

# Tests avec coverage
pytest --cov=app_stable

# Tests en mode verbose
pytest -v
```

### Mode Développement
```bash
# Auto-reload activé
uvicorn app_stable:app --reload --port 8001

# Avec logs détaillés
uvicorn app_stable:app --reload --log-level debug
```

## 🚀 Déploiement

### Production avec Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "app_stable.py"]
```

### Production avec Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app_stable:app
```

## 📊 Monitoring et Logs

L'API génère des logs structurés pour :
- Requêtes entrantes
- Erreurs et exceptions
- Performance des endpoints
- Santé de l'application

## 🔒 Sécurité

- **CORS** configuré pour les domaines autorisés
- **Validation** stricte des paramètres avec Pydantic
- **Rate limiting** (à implémenter si nécessaire)
- **HTTPS** ready pour la production

## 🤝 Contribution

1. Fork le repository
2. Créer une branche feature
3. Ajouter des tests pour les nouvelles fonctionnalités
4. Vérifier que tous les tests passent
5. Ouvrir une Pull Request

---

*🌊 API développée pour optimiser vos sessions de kitesurf*