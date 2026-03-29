import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'https://fake-news-final-jeic.onrender.com'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
})

/**
 * POST /predict — classify a piece of text
 * @param {string} text
 * @returns {Promise<{prediction, label, confidence, probabilities, processed_text}>}
 */
export async function analyzeText(text) {
  const { data } = await api.post('/predict', { text })
  return data
}

/**
 * GET /health — check API + model status
 */
export async function fetchHealth() {
  const { data } = await api.get('/health')
  return data
}

/**
 * GET /model-info — full model metadata
 */
export async function fetchModelInfo() {
  const { data } = await api.get('/model-info')
  return data
}
