// Utilitaires réutilisables pour l'application
import { KITESURF_CONFIG } from '../types'
import type { KitesurfLevel, ScoreAnalysis, WeatherData } from '../types'

/**
 * Retourne la couleur associée à un niveau de kitesurf
 */
export function getColorByLevel(level: KitesurfLevel): string {
  switch (level) {
    case 'green': return 'bg-green-100 text-green-800 border-green-200'
    case 'orange': return 'bg-orange-100 text-orange-800 border-orange-200'
    case 'red': return 'bg-red-100 text-red-800 border-red-200'
    default: return 'bg-gray-100 text-gray-800 border-gray-200'
  }
}

/**
 * Retourne le texte associé à un niveau de kitesurf
 */
export function getLabelByLevel(level: KitesurfLevel): string {
  switch (level) {
    case 'green': return KITESURF_CONFIG.levels.excellent.label
    case 'orange': return KITESURF_CONFIG.levels.good.label
    case 'red': return KITESURF_CONFIG.levels.poor.label
    default: return KITESURF_CONFIG.levels.good.label
  }
}

/**
 * Retourne la couleur basée sur le score numérique
 */
export function getColorByScore(score: number): string {
  if (score >= KITESURF_CONFIG.levels.excellent.min) return KITESURF_CONFIG.levels.excellent.color
  if (score >= KITESURF_CONFIG.levels.good.min) return KITESURF_CONFIG.levels.good.color
  return KITESURF_CONFIG.levels.poor.color
}

/**
 * Calcule le score de kitesurf basé sur les conditions météo
 */
export function calculateKitesurfScore(weather: WeatherData): ScoreAnalysis {
  // Vérification de sécurité
  if (!weather || !weather.current) {
    console.warn('Weather data invalid:', weather)
    return {
      score: 0,
      level: 'red',
      reasons: ['Données météo indisponibles']
    }
  }

  const { current } = weather
  let score = 50 // Score de base
  const reasons: string[] = []

  // Analyse du vent (facteur le plus important)
  const windKph = current.wind_kph || 0
  const { optimal, acceptable } = KITESURF_CONFIG.wind
  
  if (windKph >= optimal.min && windKph <= optimal.max) {
    score += 30
    reasons.push(`🌪️ Vent idéal: ${windKph} km/h`)
  } else if (windKph >= acceptable.min && windKph <= acceptable.max) {
    score += 15
    reasons.push(`💨 Vent correct: ${windKph} km/h`)
  } else if (windKph < acceptable.min) {
    score -= 20
    reasons.push(`😴 Vent trop faible: ${windKph} km/h`)
  } else {
    score -= 30
    reasons.push(`⚠️ Vent trop fort: ${windKph} km/h`)
  }

  // Analyse de la direction du vent
  const windDir = current.wind_dir || 'N'
  if (['N', 'NE', 'E', 'SE', 'S'].includes(windDir)) {
    score += 10
    reasons.push(`🧭 Direction favorable: ${windDir}`)
  } else if (['SW', 'W', 'NW'].includes(windDir)) {
    score -= 15
    reasons.push(`⚠️ Direction offshore: ${windDir}`)
  }

  // Analyse de la température
  const temp = current.temp_c || 15
  if (temp >= 18 && temp <= 30) {
    score += 10
    reasons.push(`🌡️ Température agréable: ${temp}°C`)
  } else if (temp < 10) {
    score -= 10
    reasons.push(`🥶 Température froide: ${temp}°C`)
  }

  // Analyse de la visibilité
  const visibility = current.vis_km || 10
  if (visibility >= 10) {
    score += 5
  } else if (visibility < 5) {
    score -= 10
    reasons.push(`🌫️ Visibilité réduite: ${visibility} km`)
  }

  // Analyse des conditions météo
  const condition = (current.condition?.text || 'partly cloudy').toLowerCase()
  if (condition.includes('rain') || condition.includes('storm')) {
    score -= 20
    reasons.push(`🌧️ Mauvaises conditions: ${current.condition?.text || 'Pluie'}`)
  } else if (condition.includes('sunny') || condition.includes('clear')) {
    score += 5
    reasons.push(`☀️ Belles conditions: ${current.condition?.text || 'Ensoleillé'}`)
  }

  // Limiter le score entre 0 et 100
  score = Math.max(0, Math.min(100, score))

  // Déterminer le niveau
  let level: KitesurfLevel
  if (score >= KITESURF_CONFIG.levels.excellent.min) {
    level = 'green'
  } else if (score >= KITESURF_CONFIG.levels.good.min) {
    level = 'orange'
  } else {
    level = 'red'
  }

  return { score, level, reasons }
}

/**
 * Formate une date pour l'affichage français
 */
export function formatDateFr(date: Date, includeTime = true): string {
  const options: Intl.DateTimeFormatOptions = {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    ...(includeTime && {
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  return date.toLocaleDateString('fr-FR', options)
}

/**
 * Génère des données de série temporelle simulées pour les prévisions
 */
export function generateTimeSeriesData(hours = 24) {
  const data = []
  const now = new Date()
  
  for (let i = 0; i < hours; i++) {
    const time = new Date(now.getTime() + i * 60 * 60 * 1000)
    // Simulation basée sur les patterns réels de vent (sinusoïdale avec du bruit)
    const baseScore = 45 + Math.sin(i * 0.5) * 20 + Math.random() * 15
    const score = Math.max(0, Math.min(100, baseScore))
    const level: KitesurfLevel = score >= 70 ? 'green' : score >= 45 ? 'orange' : 'red'
    
    data.push({
      t: time.toISOString(),
      score: Math.round(score),
      level,
      ok: level === 'green' ? 1 : level === 'orange' ? 0.5 : 0,
      reasons: score < 45 ? ['Vent faible'] : score > 80 ? ['Conditions parfaites'] : ['Conditions correctes']
    })
  }
  
  return data
}

/**
 * Vérifie si une date est aujourd'hui
 */
export function isToday(date: Date): boolean {
  return new Date().toDateString() === date.toDateString()
}

/**
 * Calcule le rayon d'une zone en fonction du score
 */
export function calculateZoneRadius(score: number, minRadius = 1000, maxRadius = 5000): number {
  return Math.max(minRadius, Math.min(maxRadius, score * 50))
}