# 🪁 KiteSurf Dashboard - Projet Final

Dashboard météo temps réel pour le kitesurf avec code couleur selon les conditions de navigation.

## 🎯 Fonctionnalités

- **Carte interactive** avec marqueurs colorés selon la surfabilité
- **Interface moderne** avec design cohérent et animations fluides  
- **Données temps réel** via API météo intégrée
- **Code couleur** : 🟢 Excellent | 🟠 Modéré | 🔴 Difficile
- **Responsive design** adaptatif

## 🏗️ Architecture

### Frontend (`frontend/kitesurf-dashboard/`)
```
src/
├── components/          # Composants React finaux
│   ├── HeaderStyled.tsx     # En-tête avec statistiques
│   ├── MapStyled.tsx        # Carte Leaflet avec marqueurs colorés
│   ├── SpotCardStyled.tsx   # Cartes de spots avec design moderne
│   ├── Sidebar.tsx          # Panneau latéral avec liste des spots
│   └── MapErrorBoundary.tsx # Gestion d'erreurs carte
├── services/
│   └── backendApi.ts        # Service API avec fallback mock
├── types/
│   └── index.ts             # Types TypeScript centralisés
├── utils/
│   └── index.ts             # Calcul score kitesurf
└── App.tsx                  # Application principale
```

### Backend (`backend/`)
```
├── app_stable.py        # Backend FastAPI principal
├── app.py               # Backend original de base
├── requirements.txt     # Dépendances Python
└── config.env          # Configuration environnement
```

## 🚀 Lancement

### Backend
```bash
cd backend
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt
uvicorn app_stable:app --reload --port 8001
```

### Frontend  
```bash
cd frontend/kitesurf-dashboard
npm install
npm run dev  # http://localhost:5173
```

## 🎨 Design

- **Palette** : Bleu/Cyan/Indigo avec gradients subtils
- **Code couleur surfabilité** :
  - 🟢 Vert : Score ≥ 7 (Excellentes conditions)
  - 🟠 Orange : Score 4-6 (Conditions moyennes) 
  - 🔴 Rouge : Score < 4 (Conditions difficiles)
- **Composants** : Cartes avec ombres, bordures arrondies, effets hover
- **Typographie** : Gradients sur les titres, hiérarchie claire

## 🛠️ Stack Technique

**Frontend :** React 18 + TypeScript + Vite + TailwindCSS + Leaflet + React Query
**Backend :** FastAPI + Python + WeatherAPI + CORS
**Cartes :** OpenStreetMap avec marqueurs personnalisés
**État :** React Query pour la gestion des données asynchrones

---
*Dashboard réalisé avec architecture modulaire et design system cohérent* ✨