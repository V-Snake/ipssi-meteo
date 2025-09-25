# 🏄‍♂️ KiteSurf Weather Dashboard

Un dashboard météorologique moderne et interactif pour les passionnés de kitesurf, développé avec React, TypeScript et Vite.

![Dashboard Preview](https://img.shields.io/badge/Status-Production%20Ready-green)
![React](https://img.shields.io/badge/React-18+-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-blue)
![Tailwind](https://img.shields.io/badge/TailwindCSS-3.4+-green)

## ✨ Fonctionnalités

- 🌍 **Carte Interactive** - Visualisation des spots de kitesurf avec marqueurs colorés selon les conditions
- 🎯 **Scoring Intelligent** - Système de notation sur 100 points basé sur les conditions météo
- 🗺️ **Navigation Intuitive** - Clic depuis la sidebar pour centrer la carte sur un spot
- 🎨 **Design Moderne** - Interface responsive avec TailwindCSS
- 🔄 **Données Temps Réel** - Intégration API météorologique avec mise à jour automatique
- 📊 **Statistiques** - Vue d'ensemble des conditions par niveaux de surfabilité

## 🎯 Code de Couleurs des Spots

- 🔴 **Rouge** (0-33/100) : Conditions difficiles ou dangereuses
- 🟠 **Orange** (34-66/100) : Conditions moyennes, praticable avec expérience  
- 🟢 **Vert** (67-100/100) : Conditions excellentes pour le kitesurf

## 🚀 Technologies Utilisées

### Frontend
- **React 18** - Bibliothèque UI avec hooks modernes
- **TypeScript 5.8+** - Typage statique pour plus de robustesse
- **Vite** - Build tool ultra-rapide avec HMR
- **TailwindCSS 3.4** - Framework CSS utility-first
- **Leaflet** - Cartographie interactive
- **React Query** - Gestion d'état et cache pour les APIs
- **Recharts** - Graphiques et visualisations

### Backend
- **FastAPI** - API Python moderne et rapide
- **Uvicorn** - Serveur ASGI haute performance
- **CORS** - Configuration pour les requêtes cross-origin

## 📦 Installation et Lancement

### Prérequis
- Node.js 18+ 
- Python 3.11+
- npm ou yarn

### 1. Clonage du Repository
```bash
git clone https://github.com/V-Snake/ipssi-meteo.git
cd ipssi-meteo
```

### 2. Installation Backend
```bash
cd backend
pip install -r requirements.txt
```

### 3. Installation Frontend
```bash
cd ../frontend/kitesurf-dashboard
npm install
```

### 4. Lancement du Backend
```bash
cd ../../backend
python app_stable.py
```
Le backend sera disponible sur `http://localhost:8001`

### 5. Lancement du Frontend
```bash
cd ../frontend/kitesurf-dashboard
npm run dev
```
Le frontend sera disponible sur `http://localhost:5173`

## 📂 Structure du Projet

```
meteo-ipssi/
├── backend/
│   ├── app_stable.py          # API FastAPI principale
│   ├── requirements.txt       # Dépendances Python
│   ├── config.env.example     # Configuration exemple
│   └── .venv/                 # Environnement virtuel
├── frontend/kitesurf-dashboard/
│   ├── src/
│   │   ├── components/        # Composants React
│   │   │   ├── MapStyled.tsx      # Carte avec marqueurs colorés
│   │   │   ├── SpotCardStyled.tsx # Cartes des spots
│   │   │   ├── HeaderStyled.tsx   # En-tête avec stats
│   │   │   └── Sidebar.tsx        # Panneau latéral
│   │   ├── services/          # Services API
│   │   ├── types/             # Types TypeScript
│   │   └── utils/             # Utilitaires
│   ├── package.json
│   └── tailwind.config.js
└── .gitignore
```

## 🔧 Scripts Disponibles

### Frontend
```bash
npm run dev      # Serveur de développement
npm run build    # Build de production
npm run preview  # Aperçu du build
npm run lint     # Linting ESLint
```

### Backend
```bash
python app_stable.py                    # Lancement direct
python -m uvicorn app_stable:app --reload  # Avec auto-reload
```

## 🌐 API Endpoints

- `GET /` - Page d'accueil de l'API
- `GET /api/spots` - Liste des spots avec données météo
- `GET /api/weather/{spot_id}` - Données météo détaillées pour un spot
- `GET /docs` - Documentation Swagger automatique

## 🎨 Composants Principaux

### MapStyled.tsx
- Carte interactive avec Leaflet
- Marqueurs colorés selon le score
- Navigation par clic depuis la sidebar
- Popups avec informations détaillées

### SpotCardStyled.tsx  
- Affichage des spots en cards
- Barres de progression pour les scores
- Badges colorés par niveau
- Informations météo synthétiques

### HeaderStyled.tsx
- Statistiques globales
- Compteurs par niveau de difficulté
- Affichage du meilleur spot

## 🔄 Gestion d'État

- **React Query** pour le cache et la synchronisation des données API
- **React Hooks** (useState, useEffect) pour l'état local des composants
- **Props drilling** contrôlé pour la communication parent-enfant

## 🎯 Prochaines Évolutions

- [ ] Historique des conditions météo
- [ ] Notifications push pour conditions favorables  
- [ ] Mode sombre/clair
- [ ] Export des données en PDF/CSV
- [ ] Intégration réseaux sociaux
- [ ] Application mobile (React Native)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalité`)
3. Commit les changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalité`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👨‍💻 Auteur

**Nassim** - Étudiant IPSSI
- GitHub: [@V-Snake](https://github.com/V-Snake)

---

*Dashboard développé avec ❤️ pour la communauté kitesurf*
