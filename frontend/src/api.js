/**
 * API Client for Smart Agriculture Assistant Backend
 * Reads base URL from VITE_API_URL environment variable.
 */

const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '')

/**
 * Health check
 */
export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    return { status: 'error', message: err.message }
  }
}

/**
 * Predict optimal crop from soil & weather parameters
 */
export async function predictCrop(data) {
  const res = await fetch(`${API_BASE}/api/crop/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })

  const json = await res.json()
  if (!res.ok) {
    throw new Error(json.detail || 'Crop prediction failed')
  }
  return json.data
}

/**
 * Fetch supported plants for disease diagnosis
 */
export async function getSupportedCrops() {
  const res = await fetch(`${API_BASE}/api/disease/crops`)
  const json = await res.json()
  if (!res.ok) {
    throw new Error(json.detail || 'Failed to fetch supported crops')
  }
  return json.crops || []
}

/**
 * Detect plant leaf disease from image upload and crop identifier
 */
export async function predictDisease(imageFile, cropName) {
  const formData = new FormData()
  formData.append('file', imageFile)
  formData.append('crop_name', cropName)

  const res = await fetch(`${API_BASE}/api/disease/predict`, {
    method: 'POST',
    body: formData
  })

  const json = await res.json()
  if (!res.ok) {
    throw new Error(json.detail || 'Disease detection failed')
  }
  return json.data
}

/**
 * Send farming question to AI chatbot with session history & prediction context
 */
export async function sendChatMessage(message, history = [], context = null) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history, context })
  })

  const json = await res.json()
  if (!res.ok) {
    throw new Error(json.detail || 'Chatbot request failed')
  }
  return json.reply
}
