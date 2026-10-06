import React, { useState, useEffect, useRef } from 'react'
import { predictCrop, getSupportedCrops, predictDisease, sendChatMessage, checkHealth } from './api'

// Fallback supported crops if backend is offline
const DEFAULT_CROPS = [
  { key: 'apple', name: 'Apple' },
  { key: 'rice', name: 'Rice' },
  { key: 'maize', name: 'Maize' },
  { key: 'grapes', name: 'Grapes' },
  { key: 'mango', name: 'Mango' },
  { key: 'orange', name: 'Orange' },
  { key: 'coffee', name: 'Coffee' },
  { key: 'coconut', name: 'Coconut' },
  { key: 'jute', name: 'Jute' },
  { key: 'black_gram_leaf', name: 'Black Gram' },
  { key: 'pigonpea', name: 'Pigeon Pea' },
  { key: 'watermelon', name: 'Watermelon' },
  { key: 'plant_wild', name: 'Wild Plant' }
]

export default function App() {
  const [activeTab, setActiveTab] = useState('crop') // 'crop', 'disease', 'chat'
  const [backendStatus, setBackendStatus] = useState('checking') // 'online', 'offline', 'checking'
  const [predictionContext, setPredictionContext] = useState(null)

  // -----------------------------------------------------------
  // Check backend health on mount
  // -----------------------------------------------------------
  useEffect(() => {
    checkHealth().then(res => {
      setBackendStatus(res.status === 'ok' ? 'online' : 'offline')
    })
  }, [])

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.brand}>
          <span style={{ fontSize: '2rem' }}>🌾</span>
          <div>
            <h1 style={styles.title}>Smart Agriculture Assistant</h1>
            <p style={styles.subtitle}>AI Decision Support for Crop Recommendation, Disease Diagnosis & Advisory</p>
          </div>
        </div>

        {/* Backend health status badge */}
        <div style={styles.statusBadge}>
          <span style={{
            ...styles.statusDot,
            backgroundColor: backendStatus === 'online' ? '#10b981' : (backendStatus === 'checking' ? '#f59e0b' : '#ef4444')
          }} />
          <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>
            Backend: {backendStatus === 'online' ? 'Connected' : (backendStatus === 'checking' ? 'Connecting...' : 'Offline')}
          </span>
        </div>
      </header>

      {/* Tab Navigation */}
      <nav style={styles.tabBar}>
        <button
          onClick={() => setActiveTab('crop')}
          style={{ ...styles.tabBtn, ...(activeTab === 'crop' ? styles.activeTabBtn : {}) }}
        >
          🌱 Crop Recommendation
        </button>
        <button
          onClick={() => setActiveTab('disease')}
          style={{ ...styles.tabBtn, ...(activeTab === 'disease' ? styles.activeTabBtn : {}) }}
        >
          🍃 Disease Detection
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          style={{ ...styles.tabBtn, ...(activeTab === 'chat' ? styles.activeTabBtn : {}) }}
        >
          🤖 Agriculture Chatbot {predictionContext ? '•' : ''}
        </button>
      </nav>

      {/* Tab Content */}
      <main style={styles.mainContent}>
        {activeTab === 'crop' && (
          <CropTab
            onAskChatbot={(cropResult) => {
              setPredictionContext({
                type: 'crop',
                crop: cropResult.recommended_crop,
                confidence: cropResult.confidence,
                inputs: cropResult.inputs
              })
              setActiveTab('chat')
            }}
          />
        )}

        {activeTab === 'disease' && (
          <DiseaseTab
            onAskChatbot={(diseaseResult) => {
              setPredictionContext({
                type: 'disease',
                plant: diseaseResult.plant,
                disease: diseaseResult.disease,
                confidence: diseaseResult.confidence
              })
              setActiveTab('chat')
            }}
          />
        )}

        {activeTab === 'chat' && (
          <ChatTab
            predictionContext={predictionContext}
            onClearContext={() => setPredictionContext(null)}
          />
        )}
      </main>

      <footer style={styles.footer}>
        Smart Agriculture Assistant • Built for Farmers & Agronomists
      </footer>
    </div>
  )
}

// =============================================================
// TAB 1: CROP RECOMMENDATION COMPONENT
// =============================================================
function CropTab({ onAskChatbot }) {
  const [formData, setFormData] = useState({
    nitrogen: 90,
    phosphorus: 42,
    potassium: 43,
    temperature: 20.8,
    humidity: 82.0,
    ph: 6.5,
    rainfall: 202.0
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: parseFloat(e.target.value) || 0 })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const data = await predictCrop(formData)
      setResult({ ...data, inputs: formData })
    } catch (err) {
      setError(err.message || 'Crop recommendation failed. Check backend connection.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.card}>
      <h2 style={styles.cardTitle}>🌱 Soil & Climate Crop Recommendation</h2>
      <p style={styles.cardDesc}>
        Enter soil nutrient values (N-P-K), soil pH, and climate conditions to predict the most profitable and suitable crop.
      </p>

      {error && <div style={styles.errorBox}>{error}</div>}

      <form onSubmit={handleSubmit}>
        <div style={styles.formGrid}>
          <div>
            <label style={styles.label}>Nitrogen (N) - kg/ha</label>
            <input type="number" name="nitrogen" value={formData.nitrogen} onChange={handleChange} required style={styles.input} />
          </div>
          <div>
            <label style={styles.label}>Phosphorus (P) - kg/ha</label>
            <input type="number" name="phosphorus" value={formData.phosphorus} onChange={handleChange} required style={styles.input} />
          </div>
          <div>
            <label style={styles.label}>Potassium (K) - kg/ha</label>
            <input type="number" name="potassium" value={formData.potassium} onChange={handleChange} required style={styles.input} />
          </div>
          <div>
            <label style={styles.label}>Soil pH (1 - 14)</label>
            <input type="number" step="0.1" name="ph" value={formData.ph} onChange={handleChange} required style={styles.input} />
          </div>
          <div>
            <label style={styles.label}>Temperature (°C)</label>
            <input type="number" step="0.1" name="temperature" value={formData.temperature} onChange={handleChange} required style={styles.input} />
          </div>
          <div>
            <label style={styles.label}>Relative Humidity (%)</label>
            <input type="number" step="0.1" name="humidity" value={formData.humidity} onChange={handleChange} required style={styles.input} />
          </div>
          <div>
            <label style={styles.label}>Rainfall (mm)</label>
            <input type="number" step="0.1" name="rainfall" value={formData.rainfall} onChange={handleChange} required style={styles.input} />
          </div>
        </div>

        <button type="submit" disabled={loading} style={styles.primaryBtn}>
          {loading ? '🔮 Analyzing Soil & Climate...' : '🔮 Recommend Optimal Crop'}
        </button>
      </form>

      {result && (
        <div style={styles.resultCard}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <span style={{ fontSize: '0.85rem', color: '#15803d', fontWeight: 700, textTransform: 'uppercase' }}>Recommended Crop</span>
              <h3 style={{ fontSize: '1.8rem', color: '#0f172a', margin: '4px 0', textTransform: 'capitalize' }}>
                🌾 {result.recommended_crop}
              </h3>
            </div>
            <div style={styles.metricBadge}>
              Confidence: {result.confidence}%
            </div>
          </div>

          <button onClick={() => onAskChatbot(result)} style={styles.contextActionBtn}>
            💬 Ask AI Chatbot about {result.recommended_crop} →
          </button>
        </div>
      )}
    </div>
  )
}

// =============================================================
// TAB 2: DISEASE DETECTION COMPONENT
// =============================================================
function DiseaseTab({ onAskChatbot }) {
  const [crops, setCrops] = useState(DEFAULT_CROPS)
  const [selectedCrop, setSelectedCrop] = useState('apple')
  const [imageFile, setImageFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getSupportedCrops().then(list => {
      if (list && list.length > 0) setCrops(list)
    }).catch(() => {})
  }, [])

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImageFile(file)
      setPreviewUrl(URL.createObjectURL(file))
      setResult(null)
      setError('')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!imageFile) {
      setError('Please select or upload a plant leaf image.')
      return
    }

    setLoading(true)
    setError('')
    try {
      const data = await predictDisease(imageFile, selectedCrop)
      setResult(data)
    } catch (err) {
      setError(err.message || 'Disease detection failed. Ensure the backend model is available.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.card}>
      <h2 style={styles.cardTitle}>🍃 Plant Leaf Disease Detection</h2>
      <p style={styles.cardDesc}>
        Upload a photo of a plant leaf to diagnose diseases using deep learning (ResNet50).
      </p>

      {error && <div style={styles.errorBox}>{error}</div>}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '16px' }}>
          <label style={styles.label}>Select Plant / Crop Type</label>
          <select value={selectedCrop} onChange={(e) => setSelectedCrop(e.target.value)} style={styles.input}>
            {crops.map(c => (
              <option key={c.key} value={c.key}>{c.name}</option>
            ))}
          </select>
        </div>

        <div style={styles.uploadArea}>
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            id="leaf-upload"
            onChange={handleImageChange}
            style={{ display: 'none' }}
          />
          <label htmlFor="leaf-upload" style={{ cursor: 'pointer', textAlign: 'center', width: '100%', display: 'block' }}>
            {previewUrl ? (
              <img src={previewUrl} alt="Leaf Preview" style={styles.imagePreview} />
            ) : (
              <div style={{ padding: '30px 10px' }}>
                <span style={{ fontSize: '2.5rem' }}>📸</span>
                <p style={{ fontWeight: 600, marginTop: '8px' }}>Click to Upload Leaf Photo</p>
                <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Supports JPG, JPEG, PNG, WEBP (Max 10MB)</p>
              </div>
            )}
          </label>
        </div>

        <button type="submit" disabled={loading || !imageFile} style={{ ...styles.primaryBtn, marginTop: '16px' }}>
          {loading ? '🔍 Diagnosing Leaf Disease...' : '🔍 Detect Disease'}
        </button>
      </form>

      {result && (
        <div style={{ ...styles.resultCard, borderColor: result.is_healthy ? '#10b981' : '#f59e0b' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <span style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color: result.is_healthy ? '#15803d' : '#b45309',
                textTransform: 'uppercase'
              }}>
                {result.is_healthy ? '✅ Healthy Plant' : '⚠️ Disease Detected'}
              </span>
              <h3 style={{ fontSize: '1.6rem', color: '#0f172a', margin: '4px 0' }}>
                {result.plant} - {result.disease}
              </h3>
            </div>
            <div style={styles.metricBadge}>
              Confidence: {result.confidence}%
            </div>
          </div>

          <button onClick={() => onAskChatbot(result)} style={styles.contextActionBtn}>
            💬 Ask AI Chatbot How to Treat This →
          </button>
        </div>
      )}
    </div>
  )
}

// =============================================================
// TAB 3: AGRICULTURE CHATBOT COMPONENT
// =============================================================
function ChatTab({ predictionContext, onClearContext }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '👋 Hello! I am your AI Agriculture Assistant. Ask me anything about crop cultivation, soil health, irrigation, fertilizers, or plant disease treatments.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const chatBottomRef = useRef(null)

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (textToSend) => {
    const query = (textToSend || input).trim()
    if (!query || loading) return

    const newMessages = [...messages, { role: 'user', content: query }]
    setMessages(newMessages)
    setInput('')
    setLoading(true)

    try {
      const historyPayload = messages.slice(1) // omit greeting from LLM prompt
      const reply = await sendChatMessage(query, historyPayload, predictionContext)
      setMessages([...newMessages, { role: 'assistant', content: reply }])
    } catch (err) {
      setMessages([...newMessages, {
        role: 'assistant',
        content: `⚠️ Error contacting AI service: ${err.message || 'Please check your connection.'}`
      }])
    } finally {
      setLoading(false)
    }
  }

  // Quick suggestion chips based on active context
  const suggestions = predictionContext?.type === 'disease'
    ? ['How do I treat this disease?', 'Are there organic remedies?', 'How can I prevent it from spreading?']
    : (predictionContext?.type === 'crop'
      ? ['What is the best sowing date?', 'What fertilizer dosage is needed?', 'How should I irrigate this crop?']
      : ['What fertilizer is best for sandy soil?', 'How do I improve soil health?', 'When should I plant wheat?'])

  return (
    <div style={styles.card}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <h2 style={styles.cardTitle}>🤖 AI Agriculture Assistant Chatbot</h2>
        {messages.length > 1 && (
          <button onClick={() => setMessages([messages[0]])} style={styles.secondaryBtn}>
            🗑️ Clear Chat
          </button>
        )}
      </div>

      {/* Active Prediction Context Banner */}
      {predictionContext && (
        <div style={styles.contextBanner}>
          <div>
            <span style={{ fontWeight: 700, color: '#15803d' }}>📌 Active Context: </span>
            {predictionContext.type === 'disease' ? (
              <span><strong>{predictionContext.plant}</strong> - {predictionContext.disease} ({predictionContext.confidence}%)</span>
            ) : (
              <span>Recommended Crop: <strong>{predictionContext.crop}</strong> ({predictionContext.confidence}%)</span>
            )}
          </div>
          <button onClick={onClearContext} style={styles.clearContextBtn}>
            ✕ Clear
          </button>
        </div>
      )}

      {/* Quick Suggestions */}
      <div style={styles.chipsContainer}>
        {suggestions.map((q, idx) => (
          <button key={idx} onClick={() => handleSend(q)} style={styles.chipBtn}>
            {q}
          </button>
        ))}
      </div>

      {/* Chat Messages */}
      <div style={styles.chatArea}>
        {messages.map((m, idx) => (
          <div
            key={idx}
            style={{
              ...styles.messageBubble,
              ...(m.role === 'user' ? styles.userBubble : styles.assistantBubble)
            }}
          >
            <div style={{ fontSize: '0.75rem', fontWeight: 700, marginBottom: '2px', opacity: 0.8 }}>
              {m.role === 'user' ? 'You' : 'Agri Assistant'}
            </div>
            <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
          </div>
        ))}
        {loading && (
          <div style={{ ...styles.messageBubble, ...styles.assistantBubble }}>
            <em>Assistant is thinking...</em>
          </div>
        )}
        <div ref={chatBottomRef} />
      </div>

      {/* Chat Input */}
      <form
        onSubmit={(e) => { e.preventDefault(); handleSend() }}
        style={{ display: 'flex', gap: '8px', marginTop: '12px' }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a farming or crop question..."
          style={{ ...styles.input, flex: 1 }}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()} style={styles.primaryBtn}>
          Send
        </button>
      </form>
    </div>
  )
}

// =============================================================
// COMPONENT STYLES
// =============================================================
const styles = {
  container: {
    maxWidth: '960px',
    margin: '0 auto',
    padding: '24px 16px',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column'
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: '12px',
    marginBottom: '20px'
  },
  brand: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  },
  title: {
    fontSize: '1.6rem',
    fontWeight: 700,
    color: '#0f172a'
  },
  subtitle: {
    fontSize: '0.9rem',
    color: '#64748b'
  },
  statusBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '6px 14px',
    borderRadius: '20px',
    background: '#ffffff',
    border: '1px solid #e2e8f0',
    boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
  },
  statusDot: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    display: 'inline-block'
  },
  tabBar: {
    display: 'flex',
    gap: '8px',
    borderBottom: '2px solid #e2e8f0',
    marginBottom: '20px',
    overflowX: 'auto'
  },
  tabBtn: {
    padding: '12px 18px',
    background: 'none',
    fontWeight: 600,
    fontSize: '0.95rem',
    color: '#64748b',
    borderBottom: '3px solid transparent',
    borderRadius: '8px 8px 0 0'
  },
  activeTabBtn: {
    color: '#15803d',
    borderBottom: '3px solid #15803d',
    background: '#f0fdf4'
  },
  mainContent: {
    flex: 1
  },
  card: {
    background: '#ffffff',
    borderRadius: '16px',
    padding: '24px',
    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)',
    border: '1px solid #f1f5f9'
  },
  cardTitle: {
    fontSize: '1.3rem',
    fontWeight: 700,
    marginBottom: '6px'
  },
  cardDesc: {
    fontSize: '0.9rem',
    color: '#64748b',
    marginBottom: '20px'
  },
  formGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '14px',
    marginBottom: '20px'
  },
  label: {
    display: 'block',
    fontSize: '0.85rem',
    fontWeight: 600,
    color: '#334155',
    marginBottom: '4px'
  },
  input: {
    width: '100%',
    boxSizing: 'border-box'
  },
  primaryBtn: {
    background: '#15803d',
    color: '#ffffff',
    padding: '12px 24px',
    fontWeight: 600,
    fontSize: '0.95rem'
  },
  secondaryBtn: {
    background: '#f1f5f9',
    color: '#475569',
    padding: '6px 12px',
    fontSize: '0.85rem'
  },
  resultCard: {
    marginTop: '24px',
    padding: '18px',
    background: '#f8fafc',
    borderRadius: '12px',
    border: '2px solid #bbf7d0'
  },
  metricBadge: {
    background: '#dcfce7',
    color: '#15803d',
    padding: '6px 14px',
    borderRadius: '20px',
    fontWeight: 700,
    fontSize: '0.9rem'
  },
  contextActionBtn: {
    marginTop: '12px',
    background: '#15803d',
    color: '#ffffff',
    padding: '8px 16px',
    fontWeight: 600,
    fontSize: '0.9rem'
  },
  errorBox: {
    background: '#fee2e2',
    color: '#991b1b',
    padding: '12px 16px',
    borderRadius: '8px',
    marginBottom: '16px',
    fontSize: '0.9rem'
  },
  uploadArea: {
    border: '2px dashed #cbd5e1',
    borderRadius: '12px',
    padding: '16px',
    background: '#f8fafc'
  },
  imagePreview: {
    maxWidth: '100%',
    maxHeight: '260px',
    borderRadius: '8px',
    objectFit: 'contain',
    display: 'block',
    margin: '0 auto'
  },
  contextBanner: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    background: '#dcfce7',
    padding: '10px 14px',
    borderRadius: '8px',
    marginBottom: '12px',
    fontSize: '0.9rem'
  },
  clearContextBtn: {
    background: 'none',
    color: '#166534',
    fontWeight: 700,
    fontSize: '0.85rem'
  },
  chipsContainer: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
    marginBottom: '14px'
  },
  chipBtn: {
    background: '#f1f5f9',
    color: '#334155',
    padding: '6px 12px',
    borderRadius: '16px',
    fontSize: '0.82rem',
    border: '1px solid #e2e8f0'
  },
  chatArea: {
    height: '380px',
    overflowY: 'auto',
    border: '1px solid #e2e8f0',
    borderRadius: '12px',
    padding: '16px',
    background: '#f8fafc',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  },
  messageBubble: {
    maxWidth: '80%',
    padding: '10px 14px',
    borderRadius: '12px',
    fontSize: '0.95rem',
    lineHeight: 1.4
  },
  userBubble: {
    alignSelf: 'flex-end',
    background: '#15803d',
    color: '#ffffff',
    borderBottomRightRadius: '2px'
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    background: '#ffffff',
    color: '#0f172a',
    border: '1px solid #e2e8f0',
    borderBottomLeftRadius: '2px'
  },
  footer: {
    textAlign: 'center',
    padding: '24px 0',
    fontSize: '0.85rem',
    color: '#94a3b8'
  }
}
