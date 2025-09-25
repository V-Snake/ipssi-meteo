# 🧪 Test de la Datasource Grafana

## 📋 **Étapes pour tester la datasource en mode Explore**

### 1. **Accéder à Grafana**
- URL: `http://localhost:3000`
- Login: `admin`
- Password: `admin`

### 2. **Aller en mode Explore**
- Cliquer sur l'icône "Explore" (🔍) dans le menu de gauche
- Ou aller directement à: `http://localhost:3000/explore`

### 3. **Sélectionner la datasource**
- Dans le dropdown "Data source", sélectionner **"BackendAPI"** ou **"json-datasource"**
- Les deux pointent vers `http://backend-api:8000`

### 4. **Tester l'endpoint /spots**
```
Query Type: JSON
URL: /spots
JSONPath: $.spots[*]
```

### 5. **Tester l'endpoint /weather**
```
Query Type: JSON
URL: /weather/670699720
JSONPath: $.data
```

### 6. **Tester des JSONPath spécifiques**
```
URL: /spots
JSONPath: $.spots[0].name          # Premier nom de spot
JSONPath: $.spots[*].latitude      # Toutes les latitudes
JSONPath: $.count                  # Nombre total de spots
```

## 🔧 **Configuration de la datasource**

### **BackendAPI**
- Type: `marcusolsson-json-datasource`
- URL: `http://backend-api:8000`
- Access: `proxy`

### **json-datasource**
- Type: `marcusolsson-json-datasource`
- URL: `http://backend-api:8000`
- Access: `proxy`

## 📊 **Endpoints disponibles**

### **GET /spots**
```json
{
  "status": "ok",
  "spots": [
    {
      "id": 670699720,
      "name": "Kitesurf Spot 670699720",
      "latitude": 16.2409545,
      "longitude": -61.3306582,
      "tags": {...},
      "country": "France"
    }
  ],
  "count": 177
}
```

### **GET /weather/{spot_id}**
```json
{
  "status": "ok",
  "data": {
    "timestamp": "2025-09-25T12:10:15.038048",
    "spot": {
      "id": 670699720,
      "name": "Kitesurf Spot 670699720",
      "latitude": 16.2409545,
      "longitude": -61.3306582,
      "country": "France"
    },
    "weather": {
      "temperature": 19.1,
      "humidity": 55.9,
      "wind_speed": 19.2,
      "wind_direction": 331,
      "condition": "cloudy",
      "kitesurf_rating": "good"
    }
  }
}
```

## 🚨 **Dépannage**

### **Si "No data"**
1. Vérifier que le backend-api est démarré
2. Tester l'API directement: `curl http://localhost:8001/spots`
3. Vérifier la configuration du datasource
4. Redémarrer Grafana si nécessaire

### **Si erreur de connexion**
1. Vérifier que les conteneurs sont dans le même réseau Docker
2. Tester: `docker exec grafana curl http://backend-api:8000/spots`
3. Vérifier les logs: `docker logs grafana`

## ✅ **Tests à effectuer**

1. **Test basique**: `$.spots[*]` sur `/spots`
2. **Test de comptage**: `$.count` sur `/spots`
3. **Test de météo**: `$.data.weather.temperature` sur `/weather/670699720`
4. **Test de filtrage**: `$.spots[?(@.latitude > 40)]` pour les spots au nord
5. **Test de transformation**: `$.spots[*].name` pour juste les noms
