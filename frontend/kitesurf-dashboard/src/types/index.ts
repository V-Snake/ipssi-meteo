// Types centralisés pour toute l'application
export interface WeatherCondition {
  text: string
  icon: string
}

export interface WeatherLocation {
  name: string
  country: string
  lat: number
  lon: number
}

export interface CurrentWeather {
  temp_c: number
  condition: WeatherCondition
  wind_kph: number
  wind_dir: string
  humidity: number
  pressure_mb: number
  vis_km: number
}

export interface WeatherData {
  location: WeatherLocation
  current: CurrentWeather
}

export interface WeatherResponse {
  status: string
  data: WeatherData
}

export interface OSMSpot {
  type: string
  id: number
  lat: number
  lon: number
  tags: {
    leisure?: string
    sport?: string
    name?: string
    club?: string
    [key: string]: any
  }
}

export interface KitesurfSpot {
  id: string
  name: string
  lat: number
  lon: number
  score?: number
  level?: KitesurfLevel
  weather?: WeatherData
  reasons?: string[]
}

export type KitesurfLevel = 'red' | 'orange' | 'green'

export interface ScoreAnalysis {
  score: number
  level: KitesurfLevel
  reasons: string[]
}

// Configuration des couleurs et seuils
export const KITESURF_CONFIG = {
  levels: {
    excellent: { min: 70, color: '#22c55e', label: 'Excellent' },
    good: { min: 45, color: '#f59e0b', label: 'Moyen' },
    poor: { min: 0, color: '#ef4444', label: 'Mauvais' }
  },
  wind: {
    optimal: { min: 15, max: 35 },
    acceptable: { min: 10, max: 45 }
  }
} as const

export const BACKEND_CONFIG = {
  url: 'http://localhost:8001',
  endpoints: {
    weather: '/weather',
    kitesurf: '/kitesurf-spots',
    root: '/'
  }
} as const