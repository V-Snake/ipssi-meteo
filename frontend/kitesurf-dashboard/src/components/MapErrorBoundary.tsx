import React from 'react'

interface MapErrorBoundaryState {
  hasError: boolean
  error?: Error
}

interface MapErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export class MapErrorBoundary extends React.Component<MapErrorBoundaryProps, MapErrorBoundaryState> {
  constructor(props: MapErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): MapErrorBoundaryState {
    console.error('🗺️ Erreur de carte capturée par ErrorBoundary:', error)
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('🗺️ Détails de l\'erreur de carte:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="w-full h-full bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center">
          <div className="text-center p-6">
            <div className="text-6xl text-gray-400 mb-4">🗺️</div>
            <h3 className="text-lg font-semibold text-gray-700 mb-2">
              Carte non disponible
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Une erreur s'est produite lors du chargement de la carte
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: undefined })
                window.location.reload()
              }}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
            >
              Réessayer
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default MapErrorBoundary