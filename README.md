# 🌊 IPSSI Météo - KiteSurf Weather Dashboard

> **Projet IPSSI** - Dashboard météorologique intelligent pour optimiser vos sessions de kitesurf

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-blue)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-blue)](https://www.typescriptlang.org/)

## 📋 Vue d'Ensemble

Ce projet combine une API FastAPI robuste avec une interface React moderne pour fournir des informations météorologiques précises aux kitesurfeurs. Le système utilise un algorithme de scoring intelligent pour évaluer la praticabilité des spots en temps réel.

## 🚀 Démarrage Rapide

### Installation Complète

1. **Cloner le repository**
```bash
git clone https://github.com/V-Snake/ipssi-meteo.git
cd ipssi-meteo
```

2. **Setup Backend**
```bash
cd backend
pip install -r requirements.txt
python app_stable.py
```
🌍 Backend disponible sur http://localhost:8001

3. **Setup Frontend**
```bash
cd ../frontend/kitesurf-dashboard
npm install
npm run dev
```
🖥️ Frontend disponible sur http://localhost:5173

## ✨ Fonctionnalités

### 🎯 Système de Scoring (0-100)
- **🟢 Vert (67-100)** : Conditions excellentes
- **🟠 Orange (34-66)** : Conditions moyennes  
- **🔴 Rouge (0-33)** : Conditions difficiles

### 🗺️ Cartographie Interactive
- Marqueurs colorés par niveau de praticabilité
- Navigation fluide entre spots via sidebar
- Popups informatifs détaillés
- Synchronisation carte ↔ sidebar

### 📊 Interface Moderne
- Design responsive avec TailwindCSS
- Composants React modulaires
- Barres de progression des scores
- Statistiques globales en temps réel
## 📂 Structure du Projet

```
meteo-ipssi/
├── 📁 backend/
│   ├── app_stable.py           # 🚀 API FastAPI principale
│   ├── requirements.txt        # 📦 Dépendances Python
│   ├── config.env.example      # ⚙️ Configuration template
│   └── .venv/                  # 🐍 Environnement virtuel
│
├── 📁 frontend/kitesurf-dashboard/
│   ├── 📁 src/
│   │   ├── 📁 components/      # 🧩 Composants React
│   │   │   ├── MapStyled.tsx       # 🗺️ Carte avec marqueurs colorés
│   │   │   ├── SpotCardStyled.tsx  # 📋 Cards des spots
│   │   │   ├── HeaderStyled.tsx    # 📊 Header avec statistiques
│   │   │   └── Sidebar.tsx         # 📱 Panneau latéral
│   │   ├── 📁 services/        # 🔌 Couche API
│   │   ├── 📁 types/          # 📝 Types TypeScript
│   │   └── 📁 utils/          # 🛠️ Utilitaires
│   ├── package.json           # 📦 Configuration NPM
│   └── tailwind.config.js     # 🎨 Configuration CSS
```

## 🛠️ Stack Technologique

### Backend
- **FastAPI** - Framework web moderne et performant
- **Uvicorn** - Serveur ASGI haute performance
- **CORS** - Support cross-origin pour le frontend
- **Pydantic** - Validation des données

### Frontend
- **React 18** - Hooks et features modernes
- **TypeScript 5.8+** - Typage strict
- **Vite** - Build tool ultra-rapide
- **TailwindCSS** - Framework CSS utility-first
- **Leaflet** - Cartographie interactive
- **React Query** - Gestion d'état et cache API

## 📊 API Endpoints

- `GET /` - Accueil API avec informations
- `GET /api/spots` - Liste complète des spots avec météo
- `GET /api/weather/{spot_id}` - Données météo détaillées
- `GET /docs` - Documentation Swagger interactive

## 🚀 Scripts de Développement

### Backend
```bash
# Démarrage standard
python app_stable.py

# Mode développement avec auto-reload
python -m uvicorn app_stable:app --reload
```

### Frontend
```bash
# Serveur de développement
npm run dev

# Build de production
npm run build

# Aperçu du build
npm run preview

# Linting
npm run lint
```

## 🎯 Fonctionnalités Avancées

- **Navigation Intelligente** : Clic sidebar → centrage carte automatique
- **Scoring Dynamique** : Algorithme basé sur vent, météo, marées
- **Design System** : Composants réutilisables avec TailwindCSS
- **Error Boundaries** : Gestion robuste des erreurs React
- **Responsive Design** : Optimisé mobile/tablet/desktop
- **Performance** : Lazy loading et optimisations Vite

## 📈 Prochaines Évolutions

- [ ] PWA (Progressive Web App)
- [ ] Notifications push conditions favorables
- [ ] Historique météorologique
- [ ] Partage social des spots
- [ ] Mode hors ligne

## 🤝 Développé par

**Nassim** - Étudiant IPSSI  
GitHub: [@V-Snake](https://github.com/V-Snake)

---

*🏄‍♂️ Dashboard créé avec passion pour la communauté kitesurf*

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