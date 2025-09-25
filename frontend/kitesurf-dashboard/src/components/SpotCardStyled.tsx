// Carte de spot avec design moderne et couleurs selon la surfabilité
import React from 'react'
import type { KitesurfSpot, KitesurfLevel } from '../types'

interface SpotCardProps {
  spot: KitesurfSpot
  onSpotClick?: (spot: KitesurfSpot) => void
  isSelected?: boolean
}

// Fonction pour déterminer le niveau basé sur le score sur 100
const getSpotLevel = (spot: KitesurfSpot): KitesurfLevel => {
  if (spot.level) return spot.level
  
  const score = spot.score || 0
  if (score >= 70) return 'green'    // Excellent
  if (score >= 45) return 'orange'   // Moyen  
  return 'red'                       // Mauvais
}

// Fonction pour obtenir les styles selon le niveau
const getLevelStyles = (level: KitesurfLevel) => {
  const styles = {
    green: {
      badge: 'bg-green-100 text-green-800 border border-green-200',
      label: 'Excellent',
      icon: '✅',
      gradient: 'from-green-400 to-green-600',
      border: 'border-green-200',
      glow: 'shadow-green-100'
    },
    orange: {
      badge: 'bg-orange-100 text-orange-800 border border-orange-200',
      label: 'Modéré',
      icon: '⚠️',
      gradient: 'from-orange-400 to-orange-600',
      border: 'border-orange-200',
      glow: 'shadow-orange-100'
    },
    red: {
      badge: 'bg-red-100 text-red-800 border border-red-200',
      label: 'Difficile',
      icon: '❌',
      gradient: 'from-red-400 to-red-600',
      border: 'border-red-200',
      glow: 'shadow-red-100'
    }
  }
  return styles[level]
}

export const SpotCard: React.FC<SpotCardProps> = ({ 
  spot, 
  onSpotClick, 
  isSelected = false 
}) => {
  const level = getSpotLevel(spot)
  const levelStyles = getLevelStyles(level)
  
  return (
    <div 
      className={`group relative bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer border-2 ${
        isSelected 
          ? 'border-blue-500 scale-[1.02] shadow-lg shadow-blue-100' 
          : `border-transparent hover:${levelStyles.border} hover:${levelStyles.glow}`
      }`}
      onClick={() => onSpotClick?.(spot)}
    >
      {/* Badge de niveau avec icône */}
      <div className={`absolute top-3 right-3 px-3 py-1.5 rounded-full text-xs font-bold shadow-sm ${levelStyles.badge}`}>
        <span className="mr-1">{levelStyles.icon}</span>
        {levelStyles.label}
      </div>

      <div className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 pr-16">
            <h3 className="font-bold text-gray-900 text-lg group-hover:text-blue-600 transition-colors line-clamp-2">
              {spot.name}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              📍 {spot.lat.toFixed(4)}, {spot.lon.toFixed(4)}
            </p>
          </div>
        </div>

        {/* Score avec couleur selon le niveau */}
        <div className="mb-4">
          <div className={`bg-gradient-to-r ${levelStyles.gradient} rounded-lg p-3 text-white`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-white/90">🪁 Score Kitesurf</span>
              <span className="text-2xl font-bold">
                {spot.score || 0}/100
              </span>
            </div>
            
            <div className="w-full bg-white/20 rounded-full h-2">
              <div 
                className="h-2 rounded-full transition-all duration-500 bg-white/80"
                style={{ width: `${Math.min(spot.score || 0, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Conditions météo avec design amélioré */}
        {spot.weather?.current && (
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-3 border border-blue-100">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-blue-700">💨 Vent</span>
                <div className="text-lg font-bold text-blue-900">
                  {spot.weather.current.wind_kph || 0}
                  <span className="text-xs font-normal ml-1">km/h</span>
                </div>
              </div>
              <div className="text-xs text-blue-600 font-medium">
                Direction: {spot.weather.current.wind_dir || 'N/A'}
              </div>
            </div>

            <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-lg p-3 border border-emerald-100">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-emerald-700">🌡️ Temp.</span>
                <div className="text-lg font-bold text-emerald-900">
                  {spot.weather.current.temp_c || 0}°C
                </div>
              </div>
              <div className="text-xs text-emerald-600 font-medium">
                Ressenti: {spot.weather.current.temp_c}°C
              </div>
            </div>
          </div>
        )}

        {/* Informations supplémentaires */}
        {spot.weather?.current && (
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 font-medium">💧 Humidité</span>
                <span className="text-gray-800 font-semibold">{spot.weather.current.humidity}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 font-medium">👁️ Visibilité</span>
                <span className="text-gray-800 font-semibold">{spot.weather.current.vis_km}km</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 font-medium">🌊 Pression</span>
                <span className="text-gray-800 font-semibold">{spot.weather.current.pressure_mb}mb</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 font-medium">🌤️ Conditions</span>
                <span className="text-gray-800 font-semibold text-right truncate max-w-16" title={spot.weather.current.condition?.text}>
                  {spot.weather.current.condition?.text?.split(' ')[0] || 'N/A'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Raisons si disponibles */}
        {spot.reasons && spot.reasons.length > 0 && (
          <div className="mt-3 p-2 bg-blue-50 rounded-lg border border-blue-100">
            <div className="text-xs font-medium text-blue-700 mb-1">📝 Détails:</div>
            <ul className="text-xs text-blue-600 space-y-0.5">
              {spot.reasons.slice(0, 2).map((reason, index) => (
                <li key={index} className="truncate">• {reason}</li>
              ))}
              {spot.reasons.length > 2 && (
                <li className="text-blue-500 font-medium">+{spot.reasons.length - 2} autres...</li>
              )}
            </ul>
          </div>
        )}
      </div>

      {/* Indicateur de sélection */}
      {isSelected && (
        <div className="absolute inset-0 rounded-xl border-2 border-blue-500 pointer-events-none">
          <div className="absolute top-2 left-2 w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
        </div>
      )}
    </div>
  )
}