// Service API amélioré pour intégration avec le backend du collègue
import { BACKEND_CONFIG } from '../types'
import { calculateKitesurfScore } from '../utils'
import type { OSMSpot, WeatherResponse } from '../types'

// Service API
export class BackendApiService {
  private baseUrl: string

  constructor(baseUrl: string = BACKEND_CONFIG.url) {
    this.baseUrl = baseUrl
  }

  // Récupérer les données météo pour une position
  async getWeather(lat: number, lon: number): Promise<WeatherResponse> {
    try {
      const url = `${this.baseUrl}${BACKEND_CONFIG.endpoints.weather}?lat=${lat}&lon=${lon}`
      console.log('🌡️ Fetching weather from:', url)
      
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`Weather API error: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('🌡️ Weather response received:', data)
      
      // Vérifier et normaliser la structure des données
      if (data && data.status === 'ok' && data.data) {
        return {
          status: 'success',
          data: data.data
        }
      } else if (data && data.data && data.data.current) {
        return data
      } else {
        console.warn('Unexpected backend response format:', data)
        throw new Error('Invalid response format from backend')
      }
    } catch (error) {
      console.warn('Weather API unavailable, using mock data:', error)
      // Fallback vers des données simulées
      const mockData = this.getMockWeatherData(lat, lon)
      console.log('🌡️ Using mock data:', mockData)
      return mockData
    }
  }

  // Déclencher l'envoi des spots kitesurf dans Kafka
  async sendKitesurfData(): Promise<{ status: string; count: number }> {
    const response = await fetch(`${this.baseUrl}${BACKEND_CONFIG.endpoints.kitesurf}`)
    if (!response.ok) {
      throw new Error(`Kitesurf API error: ${response.status}`)
    }
    return response.json()
  }

    // Récupérer tous les spots avec données météo (point d'entrée principal)
  async getAllKitesurfSpots() {
    const mockSpots: OSMSpot[] = [
      {
        type: 'node',
        id: 1,
        lat: 43.6047,
        lon: 1.4442,
        tags: { leisure: 'water_sports', sport: 'kitesurfing', name: 'Lac de la Ramée' }
      },
      {
        type: 'node', 
        id: 2,
        lat: 43.6547,
        lon: 1.4042,
        tags: { leisure: 'water_sports', sport: 'kitesurfing', name: 'Base nautique de Sesquières' }
      },
      {
        type: 'node',
        id: 3,
        lat: 43.5847,
        lon: 1.3842, 
        tags: { leisure: 'water_sports', sport: 'kitesurfing', name: 'Lac de Reynerie' }
      },
      {
        type: 'node',
        id: 4,
        lat: 43.6247,
        lon: 1.5042,
        tags: { leisure: 'water_sports', sport: 'kitesurfing', name: 'Port Sud Toulouse' }
      },
      {
        type: 'node',
        id: 5,
        lat: 43.5647,
        lon: 1.4642,
        tags: { leisure: 'water_sports', sport: 'kitesurfing', name: 'Base de loisirs de Roques' }
      }
    ]

    const spotsWithWeather = await this.getSpotsWithWeather(mockSpots)
    return spotsWithWeather.map(spot => ({
      id: `spot-${spot.id}`,
      name: spot.tags.name || `Spot ${spot.id}`,
      lat: spot.lat,
      lon: spot.lon,
      weather: spot.weather,
      score: spot.score,
      level: spot.level as 'red' | 'orange' | 'green',
      reasons: spot.reasons
    }))
  }

  // Traiter une liste de spots OSM avec leurs données météo
  async getSpotsWithWeather(
    spots: OSMSpot[]
  ): Promise<Array<OSMSpot & { weather?: WeatherResponse['data']; score?: number; level?: string; reasons?: string[] }>> {
    const spotsWithWeather = []

    for (const spot of spots.slice(0, 15)) { // Optimiser le nombre de requêtes
      try {
        const weatherResponse = await this.getWeather(spot.lat, spot.lon)
        const analysis = calculateKitesurfScore(weatherResponse.data)
        
        spotsWithWeather.push({
          ...spot,
          weather: weatherResponse.data,
          score: analysis.score,
          level: analysis.level,
          reasons: analysis.reasons
        })

        // Délai pour éviter la limite de taux API (optimisé)
        await new Promise(resolve => setTimeout(resolve, 50))
      } catch (error) {
        console.warn(`Erreur météo pour le spot ${spot.id}:`, error)
        // Ajouter le spot avec données par défaut
        spotsWithWeather.push({
          ...spot,
          score: 50,
          level: 'orange',
          reasons: ['Données météo indisponibles']
        })
      }
    }

    return spotsWithWeather
  }

  // Données météo simulées pour le développement
  private getMockWeatherData(lat: number, lon: number): WeatherResponse {
    const mockConditions = [
      { text: 'Sunny', icon: '//cdn.weatherapi.com/weather/64x64/day/113.png' },
      { text: 'Partly cloudy', icon: '//cdn.weatherapi.com/weather/64x64/day/116.png' },
      { text: 'Cloudy', icon: '//cdn.weatherapi.com/weather/64x64/day/119.png' },
      { text: 'Light rain', icon: '//cdn.weatherapi.com/weather/64x64/day/296.png' }
    ]

    const condition = mockConditions[Math.floor(Math.random() * mockConditions.length)]
    const windSpeed = Math.random() * 40 + 5 // 5-45 km/h
    const windDirections = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    const windDir = windDirections[Math.floor(Math.random() * windDirections.length)]

    return {
      status: 'success',
      data: {
        location: {
          name: `Location ${lat.toFixed(2)},${lon.toFixed(2)}`,
          country: 'France',
          lat,
          lon
        },
        current: {
          temp_c: Math.random() * 15 + 10, // 10-25°C
          condition,
          wind_kph: windSpeed,
          wind_dir: windDir,
          humidity: Math.random() * 40 + 40, // 40-80%
          pressure_mb: Math.random() * 50 + 1000, // 1000-1050 mb
          vis_km: Math.random() * 15 + 5 // 5-20 km
        }
      }
    }
  }
}

// Instance par défaut
export const backendApi = new BackendApiService()

// Ré-exports pour compatibilité
export type { OSMSpot, WeatherResponse }