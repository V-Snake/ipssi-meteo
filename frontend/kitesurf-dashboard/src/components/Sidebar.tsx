// Panneau latéral avec liste des spots
import React from 'react'
import type { KitesurfSpot } from '../types'
import { SpotCard } from './SpotCardStyled'

interface SidebarProps {
  spots: KitesurfSpot[]
  onSpotSelect: (spot: KitesurfSpot) => void
  selectedSpot?: KitesurfSpot
  isLoading?: boolean
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  spots, 
  onSpotSelect, 
  selectedSpot,
  isLoading = false 
}) => {
  const sortedSpots = [...spots].sort((a, b) => (b.score || 0) - (a.score || 0))
  
  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-white to-gray-50">
      {/* En-tête du panneau avec design amélioré */}
      <div className="flex-shrink-0 p-4 bg-gradient-to-r from-blue-50 to-cyan-50 border-b border-blue-100">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-gray-900 flex items-center">
              🪁 Spots Kitesurf
            </h2>
            <p className="text-sm text-gray-600">
              {spots.length} zones analysées
            </p>
          </div>
          
          {isLoading && (
            <div className="bg-white/80 backdrop-blur-sm rounded-full p-2 shadow-sm">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            </div>
          )}
        </div>
        
        {/* Légende des niveaux avec design amélioré */}
        <div className="mt-3 flex items-center space-x-4 bg-white/60 backdrop-blur-sm p-2 rounded-lg">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-green-500 shadow-sm"></div>
            <span className="text-xs text-gray-700 font-medium">Excellent</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-orange-500 shadow-sm"></div>
            <span className="text-xs text-gray-700 font-medium">Modéré</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-red-500 shadow-sm"></div>
            <span className="text-xs text-gray-700 font-medium">Difficile</span>
          </div>
        </div>
      </div>

      {/* Liste des spots */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Chargement des données météo...</p>
          </div>
        ) : spots.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <p className="text-gray-500">Aucun spot trouvé</p>
            <p className="text-sm text-gray-400 mt-1">
              Déplacez la carte pour explorer d'autres zones
            </p>
          </div>
        ) : (
          sortedSpots.map(spot => (
            <SpotCard 
              key={spot.id} 
              spot={spot} 
              onSpotClick={onSpotSelect}
              isSelected={selectedSpot?.id === spot.id}
            />
          ))
        )}
      </div>
      
      {/* Statistiques en bas */}
      {spots.length > 0 && (
        <div className="flex-shrink-0 p-4 bg-white border-t border-gray-200">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-green-600">
                {sortedSpots.filter(s => (s.level === 'green')).length}
              </div>
              <div className="text-xs text-gray-500">Excellents</div>
            </div>
            <div>
              <div className="text-lg font-bold text-orange-500">
                {sortedSpots.filter(s => (s.level === 'orange')).length}
              </div>
              <div className="text-xs text-gray-500">Modérés</div>
            </div>
            <div>
              <div className="text-lg font-bold text-red-500">
                {sortedSpots.filter(s => (s.level === 'red')).length}
              </div>
              <div className="text-xs text-gray-500">Faibles</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}