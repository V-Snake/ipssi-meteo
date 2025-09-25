// Composant d'en-tête moderne avec statistiques et design cohérent
import React from 'react'
import { BACKEND_CONFIG } from '../types'
import type { KitesurfSpot } from '../types'

interface HeaderProps {
  spotsCount: number
  isLoading: boolean
  spots?: KitesurfSpot[]
}

// Fonction pour déterminer le niveau basé sur le score sur 100
const getSpotLevel = (spot: KitesurfSpot) => {
  if (spot.level) return spot.level
  const score = spot.score || 0
  if (score >= 70) return 'green'    // Excellent  
  if (score >= 45) return 'orange'   // Moyen
  return 'red'                       // Mauvais
}

export const HeaderStyled: React.FC<HeaderProps> = ({ spotsCount, isLoading, spots = [] }) => {
  // Calculer les statistiques par niveau
  const stats = {
    green: spots.filter(s => getSpotLevel(s) === 'green').length,
    orange: spots.filter(s => getSpotLevel(s) === 'orange').length,
    red: spots.filter(s => getSpotLevel(s) === 'red').length
  }

  const bestSpot = spots.length > 0 ? [...spots].sort((a, b) => (b.score || 0) - (a.score || 0))[0] : null

  return (
    <div className="relative z-20 bg-gradient-to-r from-blue-50 via-white to-cyan-50 border-b border-blue-100 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo et titre */}
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-600 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-2xl">🪁</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-900 to-cyan-700 bg-clip-text text-transparent">
                KiteSurf Dashboard
              </h1>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>⚡ Temps réel</span>
                <span>•</span>
                <span>🌐 {BACKEND_CONFIG.url.replace('http://', '')}</span>
                {bestSpot && (
                  <>
                    <span>•</span>
                    <span className="font-medium text-blue-600">
                      🏆 {bestSpot.name} ({bestSpot.score}/100)
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Statistiques et statut */}
          <div className="flex items-center space-x-6">
            {/* Statistiques par niveau */}
            {spots.length > 0 && (
              <div className="hidden md:flex items-center space-x-4">
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 rounded-full bg-green-500 shadow-sm"></div>
                  <span className="text-sm font-semibold text-green-700">{stats.green}</span>
                  <span className="text-xs text-gray-500">excellents</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 rounded-full bg-orange-500 shadow-sm"></div>
                  <span className="text-sm font-semibold text-orange-700">{stats.orange}</span>
                  <span className="text-xs text-gray-500">modérés</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 rounded-full bg-red-500 shadow-sm"></div>
                  <span className="text-sm font-semibold text-red-700">{stats.red}</span>
                  <span className="text-xs text-gray-500">difficiles</span>
                </div>
              </div>
            )}

            {/* Indicateur de chargement */}
            {isLoading && (
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm px-3 py-1.5 rounded-full border border-blue-200 shadow-sm">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-sm font-medium text-blue-700">Actualisation...</span>
              </div>
            )}
            
            {/* Compteur total */}
            <div className="text-right bg-white/80 backdrop-blur-sm px-4 py-2 rounded-lg border border-blue-200 shadow-sm">
              <div className="text-lg font-bold text-gray-900">
                {spotsCount}
              </div>
              <div className="text-xs text-gray-600 font-medium">
                spots analysés
              </div>
            </div>
          </div>
        </div>

        {/* Barre de progression si chargement */}
        {isLoading && (
          <div className="absolute bottom-0 left-0 right-0">
            <div className="h-1 bg-blue-100">
              <div className="h-1 bg-gradient-to-r from-blue-500 to-cyan-500 animate-pulse"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}