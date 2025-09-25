// Application principale avec architecture modulaire améliorée
import { useState, useEffect } from 'react'
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import { Header, Sidebar, MapComponent } from './components'
import MapErrorBoundary from './components/MapErrorBoundary'
import { backendApi } from './services/backendApi'
import type { KitesurfSpot } from './types'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function KitesurfDashboard() {
  const [selectedSpot, setSelectedSpot] = useState<KitesurfSpot | undefined>()
  
  // Query pour récupérer les données des spots
  const { data: spots = [], isLoading, error, refetch } = useQuery({
    queryKey: ['kitesurf-spots'],
    queryFn: async () => {
      console.log('🔄 Fetching kitesurf spots...')
      const spots = await backendApi.getAllKitesurfSpots()
      console.log(`✅ Loaded ${spots.length} spots with weather data`)
      return spots
    },
    refetchInterval: 10 * 60 * 1000, // Refresh toutes les 10 minutes
  })

  // Auto-refresh périodique en arrière-plan
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('🔄 Auto-refreshing data...')
      refetch()
    }, 15 * 60 * 1000) // 15 minutes

    return () => clearInterval(interval)
  }, [refetch])

  // Sélectionner automatiquement le meilleur spot
  useEffect(() => {
    if (spots.length > 0 && !selectedSpot) {
      const bestSpot = [...spots].sort((a, b) => (b.score || 0) - (a.score || 0))[0]
      setSelectedSpot(bestSpot)
    }
  }, [spots, selectedSpot])

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-red-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md mx-auto text-center border border-red-200">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Erreur de connexion</h2>
          <p className="text-gray-600 mb-4">
            Impossible de se connecter au serveur backend. Vérifiez que le serveur FastAPI est démarré.
          </p>
          <button 
            onClick={() => refetch()}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Réessayer
          </button>
          <div className="mt-4 p-3 bg-gray-50 rounded-lg text-left">
            <p className="text-xs text-gray-500 font-mono">
              Backend: http://localhost:8001
            </p>
            <p className="text-xs text-red-500 mt-1">
              {error instanceof Error ? error.message : 'Erreur inconnue'}
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-blue-50 via-cyan-50 to-indigo-50">
      <Header spotsCount={spots.length} isLoading={isLoading} spots={spots} />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Panneau latéral avec design amélioré */}
        <div className="w-96 flex-shrink-0 bg-gradient-to-b from-white to-gray-50 shadow-xl border-r border-gray-200">
          <Sidebar 
            spots={spots}
            onSpotSelect={setSelectedSpot}
            selectedSpot={selectedSpot}
            isLoading={isLoading}
          />
        </div>

        {/* Carte principale */}
        <div className="flex-1 relative">
          <MapErrorBoundary>
            <MapComponent 
              spots={spots}
              onSpotSelect={setSelectedSpot}
              selectedSpot={selectedSpot}
              className="w-full h-full"
            />
          </MapErrorBoundary>
          
          {/* Bouton de refresh */}
          <button
            onClick={() => refetch()}
            disabled={isLoading}
            className="absolute top-4 right-4 bg-white hover:bg-gray-50 text-gray-700 font-medium py-2 px-4 rounded-lg shadow-lg border border-gray-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed z-10"
          >
            {isLoading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span>Actualisation...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>Actualiser</span>
              </div>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

// Composant principal avec provider
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <KitesurfDashboard />
    </QueryClientProvider>
  )
}

export default App