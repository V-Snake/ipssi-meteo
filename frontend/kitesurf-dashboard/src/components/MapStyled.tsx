import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { KitesurfSpot, KitesurfLevel } from '../types'

interface MapProps {
  spots: KitesurfSpot[]
  selectedSpot?: KitesurfSpot
  onSpotSelect: (spot: KitesurfSpot) => void
  className?: string
}

// Configuration des icônes colorées selon le niveau de surfabilité
const createColoredIcon = (level: KitesurfLevel) => {
  const colors = {
    red: '#ef4444',    // Tailwind red-500
    orange: '#f97316', // Tailwind orange-500  
    green: '#22c55e'   // Tailwind green-500
  }
  
  const color = colors[level]
  
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        width: 30px;
        height: 30px;
        background-color: ${color};
        border: 3px solid white;
        border-radius: 50%;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2), 0 0 0 2px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        position: relative;
      ">
        <div style="
          color: white;
          font-weight: bold;
          text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        ">🪁</div>
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15]
  })
}

// Spots de test avec différents niveaux
const TEST_SPOTS: Array<KitesurfSpot & { level: KitesurfLevel }> = [
  { 
    id: '1',
    lat: 43.6047, 
    lon: 1.4442, 
    name: 'Lac de la Ramée', 
    score: 8,
    level: 'green',
    reasons: ['Vent favorable', 'Bonnes conditions']
  },
  { 
    id: '2',
    lat: 43.6547, 
    lon: 1.4042, 
    name: 'Base nautique de Sesquières', 
    score: 5,
    level: 'orange',
    reasons: ['Vent moyen', 'Conditions acceptables']
  },
  { 
    id: '3',
    lat: 43.5847, 
    lon: 1.3842, 
    name: 'Lac de Reynerie', 
    score: 3,
    level: 'red',
    reasons: ['Vent faible', 'Conditions difficiles']
  }
]

export function MapStyled({ spots, selectedSpot, onSpotSelect, className }: MapProps) {
  const mapRef = useRef<L.Map | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  const [markersCount, setMarkersCount] = useState(0)
  const [useTestData, setUseTestData] = useState(false)
  const markersLayerRef = useRef<L.LayerGroup | null>(null)
  const markersRef = useRef<Map<string, L.Marker>>(new Map()) // Stocker les marqueurs par ID
  const initTimeoutRef = useRef<number | null>(null)

  // Fonction pour déterminer le niveau basé sur le score sur 100
  const getSpotLevel = (spot: KitesurfSpot): KitesurfLevel => {
    if (spot.level) return spot.level
    
    const score = spot.score || 0
    if (score >= 70) return 'green'    // Excellent
    if (score >= 45) return 'orange'   // Moyen
    return 'red'                       // Mauvais
  }

  // Fonction pour obtenir le texte du niveau
  const getLevelText = (level: KitesurfLevel): string => {
    const texts = {
      green: '✅ Excellentes conditions',
      orange: '⚠️ Conditions moyennes', 
      red: '❌ Conditions difficiles'
    }
    return texts[level]
  }

  // Fonction pour créer et ajouter un marqueur stylé
  const createStyledMarker = (spot: KitesurfSpot, isTestData = false) => {
    if (!markersLayerRef.current) return null

    try {
      const level = getSpotLevel(spot)
      const marker = L.marker([spot.lat, spot.lon], {
        icon: createColoredIcon(level)
      })
      
      const popupContent = `
        <div style="
          padding: 16px; 
          font-family: system-ui, -apple-system, sans-serif;
          max-width: 280px;
          background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        ">
          <div style="
            display: flex;
            align-items: center;
            margin-bottom: 12px;
          ">
            <div style="
              width: 8px;
              height: 8px;
              background-color: ${level === 'green' ? '#22c55e' : level === 'orange' ? '#f97316' : '#ef4444'};
              border-radius: 50%;
              margin-right: 8px;
            "></div>
            <h3 style="
              margin: 0; 
              font-weight: 600; 
              color: #1e293b;
              font-size: 16px;
            ">
              ${spot.name} ${isTestData ? '(TEST)' : ''}
            </h3>
          </div>
          
          <div style="
            background: white;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 12px;
            border-left: 4px solid ${level === 'green' ? '#22c55e' : level === 'orange' ? '#f97316' : '#ef4444'};
          ">
            <p style="margin: 0 0 8px 0; font-weight: 600; color: #1e293b;">
              ${getLevelText(level)}
            </p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="color: #64748b; font-size: 14px;">Score surfabilité</span>
              <div style="
                background: ${level === 'green' ? '#dcfce7' : level === 'orange' ? '#fed7aa' : '#fecaca'};
                color: ${level === 'green' ? '#166534' : level === 'orange' ? '#9a3412' : '#991b1b'};
                padding: 4px 8px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
              ">
                ${spot.score || 0}/100
              </div>
            </div>
          </div>

          ${spot.weather ? `
            <div style="
              background: white;
              padding: 12px;
              border-radius: 8px;
              border: 1px solid #e2e8f0;
            ">
              <h4 style="margin: 0 0 8px 0; color: #475569; font-size: 14px; font-weight: 600;">
                🌤️ Conditions météo
              </h4>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                <div>
                  <span style="color: #64748b;">Température</span><br>
                  <strong style="color: #1e293b;">${spot.weather.current?.temp_c || 'N/A'}°C</strong>
                </div>
                <div>
                  <span style="color: #64748b;">Vent</span><br>
                  <strong style="color: #1e293b;">${spot.weather.current?.wind_kph || 'N/A'} km/h</strong>
                </div>
                <div>
                  <span style="color: #64748b;">Direction</span><br>
                  <strong style="color: #1e293b;">${spot.weather.current?.wind_dir || 'N/A'}</strong>
                </div>
                <div>
                  <span style="color: #64748b;">Humidité</span><br>
                  <strong style="color: #1e293b;">${spot.weather.current?.humidity || 'N/A'}%</strong>
                </div>
              </div>
            </div>
          ` : ''}

          ${spot.reasons && spot.reasons.length > 0 ? `
            <div style="
              margin-top: 12px;
              padding: 10px;
              background: #f1f5f9;
              border-radius: 6px;
              border-left: 3px solid #3b82f6;
            ">
              <h4 style="margin: 0 0 6px 0; color: #475569; font-size: 13px; font-weight: 600;">
                📝 Détails
              </h4>
              ${spot.reasons.map(reason => `
                <p style="margin: 2px 0; font-size: 12px; color: #64748b;">• ${reason}</p>
              `).join('')}
            </div>
          ` : ''}
        </div>
      `

      marker.bindPopup(popupContent, {
        maxWidth: 300,
        className: 'custom-popup'
      })
      
      // Gestionnaire de clic
      if (!isTestData && spots.length > 0) {
        const realSpot = spots.find(s => s.lat === spot.lat && s.lon === spot.lon)
        if (realSpot) {
          marker.on('click', () => {
            console.log(`🎯 Spot sélectionné: ${realSpot.name}`)
            onSpotSelect(realSpot)
          })
        }
      }

      markersLayerRef.current.addLayer(marker)
      
      // Stocker le marqueur par ID pour pouvoir le retrouver facilement
      markersRef.current.set(spot.id || `${spot.lat}-${spot.lon}`, marker)
      
      return marker
    } catch (error) {
      console.error('Erreur création marqueur stylé:', error)
      return null
    }
  }

  // Initialisation de la carte
  useEffect(() => {
    if (!containerRef.current || isInitialized) return

    console.log('🗺️ Initialisation de la carte stylée...')

    if (initTimeoutRef.current) {
      clearTimeout(initTimeoutRef.current)
    }

    const initMap = () => {
      try {
        if (!containerRef.current) return

        const map = L.map(containerRef.current, {
          center: [43.6047, 1.4442],
          zoom: 11,
          zoomControl: true,
          attributionControl: false
        })

        // Style de carte plus attrayant
        L.tileLayer('https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap France | © OpenStreetMap contributors'
        }).addTo(map)

        // Créer le groupe de marqueurs
        const markersLayer = L.layerGroup()
        markersLayer.addTo(map)
        markersLayerRef.current = markersLayer

        mapRef.current = map

        // Attendre que la carte soit prête
        map.whenReady(() => {
          console.log('✅ Carte stylée prête !')
          setIsInitialized(true)
          
          // Ajouter les marqueurs de test stylés
          console.log('🎨 Ajout des marqueurs stylés...')
          let testCount = 0
          TEST_SPOTS.forEach(testSpot => {
            const marker = createStyledMarker(testSpot, true)
            if (marker) testCount++
          })
          
          if (testCount > 0) {
            setMarkersCount(testCount)
            setUseTestData(true)
            console.log(`✅ ${testCount} marqueurs stylés ajoutés`)
          }
        })

      } catch (error) {
        console.error('❌ Erreur initialisation carte stylée:', error)
      }
    }

    initTimeoutRef.current = setTimeout(initMap, 100)

    return () => {
      if (initTimeoutRef.current) {
        clearTimeout(initTimeoutRef.current)
      }
      if (markersLayerRef.current) {
        markersLayerRef.current.clearLayers()
      }
      if (mapRef.current) {
        mapRef.current.remove()
      }
      mapRef.current = null
      markersLayerRef.current = null
      setIsInitialized(false)
    }
  }, [])

  // Effet pour ajouter les vrais spots quand ils arrivent
  useEffect(() => {
    if (!isInitialized || !markersLayerRef.current || spots.length === 0) return

    console.log(`🗺️ Mise à jour avec ${spots.length} spots réels`)
    
    // Vider les anciens marqueurs et les références
    markersLayerRef.current.clearLayers()
    markersRef.current.clear()
    
    // Ajouter les nouveaux marqueurs
    let realMarkersCount = 0
    spots.forEach(spot => {
      const marker = createStyledMarker(spot, false)
      if (marker) realMarkersCount++
    })

    setMarkersCount(realMarkersCount)
    setUseTestData(false)
    
    if (realMarkersCount > 0) {
      console.log(`✅ ${realMarkersCount} marqueurs réels ajoutés`)
      
      // Ajuster la vue pour inclure tous les spots
      const layers = Object.values(markersLayerRef.current.getLayers())
      if (layers.length > 0) {
        const group = L.featureGroup(layers as L.Layer[])
        if (mapRef.current && group.getBounds().isValid()) {
          mapRef.current.fitBounds(group.getBounds(), { padding: [20, 20] })
        }
      }
    }
  }, [spots, isInitialized])

  // Effet pour centrer la carte sur le spot sélectionné depuis la sidebar
  useEffect(() => {
    if (!selectedSpot || !mapRef.current || !markersRef.current) return

    console.log(`🎯 Centrage sur le spot sélectionné: ${selectedSpot.name}`)
    
    const spotId = selectedSpot.id || `${selectedSpot.lat}-${selectedSpot.lon}`
    const marker = markersRef.current.get(spotId)
    
    if (marker) {
      // Centrer la carte sur le marqueur avec un zoom approprié
      mapRef.current.setView([selectedSpot.lat, selectedSpot.lon], 13, {
        animate: true,
        duration: 0.8
      })
      
      // Ouvrir le popup du marqueur après un petit délai pour l'animation
      setTimeout(() => {
        marker.openPopup()
      }, 500)
    } else {
      // Si pas de marqueur trouvé, au moins centrer la carte
      mapRef.current.setView([selectedSpot.lat, selectedSpot.lon], 13, {
        animate: true,
        duration: 0.8
      })
    }
  }, [selectedSpot])

  return (
    <div className={`relative ${className || ''}`}>
      {/* Header avec informations */}
      <div className="absolute top-4 left-4 z-[1000] bg-white/95 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg border border-white/20">
        <div className="flex items-center gap-2 text-sm">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-gray-600">Excellent</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
            <span className="text-gray-600">Moyen</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span className="text-gray-600">Difficile</span>
          </div>
        </div>
      </div>

      {/* Compteur de spots */}
      <div className="absolute top-4 right-4 z-[1000] bg-white/95 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg border border-white/20">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-blue-600 font-semibold">🪁 {markersCount} spots</span>
          {useTestData && <span className="text-orange-500 text-xs">(TEST)</span>}
        </div>
      </div>

      {/* Container de la carte */}
      <div 
        ref={containerRef}
        className="w-full h-full rounded-xl overflow-hidden shadow-xl"
        style={{ minHeight: '500px' }}
      />
    </div>
  )
}

// CSS personnalisé pour les popups (à ajouter au CSS global si nécessaire)
const popupStyles = `
  .custom-popup .leaflet-popup-content-wrapper {
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
  }
  
  .custom-popup .leaflet-popup-tip {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0 !important;
  }
`

// Injecter les styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style')
  styleSheet.textContent = popupStyles
  document.head.appendChild(styleSheet)
}