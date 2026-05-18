import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { API_BASE } from '../utils/api'
import { useAuth } from './AuthContext'
const DEFAULT_LOCATION = '上海, 上海市, 中国'
const CACHE_KEY = 'aiwardrobe_recommendation_cache'
const CACHE_EXPIRY_HOURS = 24

const RecommendationContext = createContext(null)

const INITIAL_STATE = {
  loading: false,
  error: '',
  weather: null,
  horoscope: null,
  temperatureRule: null,
  recommendation: '',
  outfitSummary: '',
  selectionReasons: {},
  suggestedTop: null,
  suggestedBottom: null,
  suggestedShoes: null,
  suggestedAccessories: [],
  purchaseSuggestions: [],
  goalRaw: '',
  goalNormalized: '',
  recordId: null,
  isFavorited: false,
  selectedCity: {
    name: DEFAULT_LOCATION,
    id: DEFAULT_LOCATION
  }
}

function getCache() {
  try {
    const cached = localStorage.getItem(CACHE_KEY)
    if (!cached) {
      console.log('[RecommendationContext] No cache found in localStorage')
      return null
    }

    const { data, timestamp } = JSON.parse(cached)
    const now = Date.now()
    const hoursSinceCached = (now - timestamp) / (1000 * 60 * 60)

    console.log('[RecommendationContext] Cache found, age:', hoursSinceCached.toFixed(1), 'hours')

    if (hoursSinceCached > CACHE_EXPIRY_HOURS) {
      localStorage.removeItem(CACHE_KEY)
      console.log('[RecommendationContext] Cache expired, removed')
      return null
    }

    console.log('[RecommendationContext] Cache data keys:', Object.keys(data))
    return data
  } catch (e) {
    console.log('[RecommendationContext] Cache read error:', e)
    return null
  }
}

function setCache(data) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify({
      data,
      timestamp: Date.now()
    }))
    console.log('[RecommendationContext] Cache saved')
  } catch {
    // ignore storage errors
  }
}

function clearCache() {
  try {
    localStorage.removeItem(CACHE_KEY)
  } catch {
    // ignore
  }
}

export function RecommendationProvider({ children }) {
  const { token } = useAuth()
  const [state, setState] = useState(() => {
    const cached = getCache()
    if (cached) {
      console.log('[RecommendationContext] Loaded from cache:', cached)
      return { ...INITIAL_STATE, ...cached }
    }
    console.log('[RecommendationContext] No cache, using initial state')
    return INITIAL_STATE
  })
  const requestIdRef = useRef(0)

  useEffect(() => {
    console.log('[RecommendationContext] State updated, weather:', !!state.weather, 'recommendation:', state.recommendation?.slice(0, 50))
    const fetchDefaultCity = async () => {
      try {
        const response = await fetch(`${API_BASE}/config`)
        if (!response.ok) {
          return
        }

        const data = await response.json()
        const location = (data.weather_location || '').trim()
        if (!location) {
          return
        }

        setState(prev => ({
          ...prev,
          selectedCity: {
            name: location,
            id: location
          }
        }))
      } catch (error) {
        console.error('Failed to fetch default city config:', error)
      }
    }

    void fetchDefaultCity()
  }, [])

  const fetchRecommendation = useCallback(async (location, preferredName = null, goal = '') => {
    if (!location) {
      return null
    }

    // 确保 token 已加载
    if (!token) {
      console.log('[RecommendationContext] Token not ready, skipping fetch')
      return null
    }

    const requestId = requestIdRef.current + 1
    requestIdRef.current = requestId
    setState(prev => ({ ...prev, loading: true, error: '' }))

    try {
      const params = new URLSearchParams({ location })
      const trimmedGoal = (goal || '').trim()
      if (trimmedGoal) {
        params.set('goal', trimmedGoal)
      }
      const response = await fetch(`${API_BASE}/recommendation?${params.toString()}`, {
                headers: { Authorization: `Bearer ${token}` }
            })
      if (!response.ok) {
        const errorPayload = await response.json().catch(() => ({}))
        if (requestId === requestIdRef.current) {
          setState(prev => ({
            ...prev,
            loading: false,
            error: errorPayload.detail || 'Failed to fetch recommendation'
          }))
        }
        return null
      }

      const data = await response.json()
      console.log('[RecommendationContext] API response keys:', Object.keys(data), 'record_id:', data.record_id)
      if (requestId !== requestIdRef.current) {
        return null
      }

      const newSelectedCity = preferredName
        ? { name: preferredName, id: location }
        : (data.weather?.location ? { name: data.weather.location, id: location } : state.selectedCity)

      setState(prev => ({
        ...prev,
        loading: false,
        error: '',
        weather: data.weather || null,
        horoscope: data.horoscope || null,
        temperatureRule: data.temperature_rule || null,
        recommendation: data.recommendation_text || '',
        outfitSummary: data.outfit_summary || '',
        selectionReasons: data.selection_reasons || {},
        suggestedTop: data.suggested_top || null,
        suggestedBottom: data.suggested_bottom || null,
        suggestedShoes: data.suggested_shoes || null,
        suggestedAccessories: data.suggested_accessories || [],
        purchaseSuggestions: data.purchase_suggestions || [],
        goalRaw: data.goal_raw || '',
        goalNormalized: data.goal_normalized || '',
        recordId: data.record_id || null,
        isFavorited: false,
        selectedCity: newSelectedCity
      }))

      setCache({
        weather: data.weather,
        horoscope: data.horoscope,
        temperatureRule: data.temperature_rule,
        recommendation: data.recommendation_text,
        outfitSummary: data.outfit_summary,
        selectionReasons: data.selection_reasons,
        suggestedTop: data.suggested_top,
        suggestedBottom: data.suggested_bottom,
        suggestedShoes: data.suggested_shoes,
        suggestedAccessories: data.suggested_accessories,
        purchaseSuggestions: data.purchase_suggestions,
        goalRaw: data.goal_raw,
        goalNormalized: data.goal_normalized,
        selectedCity: newSelectedCity,
        recordId: data.record_id || null,
        isFavorited: data.is_favorited || false
      })

      return data
    } catch (error) {
      if (requestId === requestIdRef.current) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: error?.message || 'Failed to fetch recommendation'
        }))
      }
      return null
    }
  }, [])

  const toggleFavorite = useCallback(async () => {
    if (!state.recordId) return
    try {
      const method = state.isFavorited ? 'DELETE' : 'POST'
      const response = await fetch(`${API_BASE}/recommendations/${state.recordId}/favorite`, {
        method,
        headers: { Authorization: `Bearer ${token}` }
      })
      if (response.ok) {
        setState(prev => ({ ...prev, isFavorited: !prev.isFavorited }))
      } else if (response.status === 404) {
        // 记录不属于当前用户，不做任何操作
        console.log('[toggleFavorite] Record not found or not owned by current user')
      } else {
        const errorData = await response.json().catch(() => ({}))
        console.error('Failed to toggle favorite:', errorData.detail || response.status)
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error)
    }
  }, [state.recordId, state.isFavorited, token])

  const value = useMemo(() => ({
    ...state,
    fetchRecommendation,
    toggleFavorite,
    clearRecommendationCache: clearCache
  }), [state, fetchRecommendation, toggleFavorite])

  return (
    <RecommendationContext.Provider value={value}>
      {children}
    </RecommendationContext.Provider>
  )
}

export function useRecommendation() {
  const context = useContext(RecommendationContext)
  if (!context) {
    throw new Error('useRecommendation must be used within RecommendationProvider')
  }
  return context
}

