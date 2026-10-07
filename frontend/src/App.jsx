import React, { useState, useEffect } from 'react'
import { checkHealth } from './api'
import Header from './components/Header'
import BottomNav from './components/BottomNav'
import CropTab from './components/CropTab'
import DiseaseTab from './components/DiseaseTab'
import ChatTab from './components/ChatTab'

export default function App() {
  const [activeTab, setActiveTab] = useState('crop') // 'crop' | 'disease' | 'chat'
  const [backendStatus, setBackendStatus] = useState('checking') // 'online' | 'offline' | 'checking'
  const [predictionContext, setPredictionContext] = useState(null)

  // Verify backend health on mount and periodically
  useEffect(() => {
    let isMounted = true

    const verifyBackend = async () => {
      try {
        const res = await checkHealth()
        if (isMounted) {
          setBackendStatus(res.status === 'ok' ? 'online' : 'offline')
        }
      } catch {
        if (isMounted) setBackendStatus('offline')
      }
    }

    verifyBackend()
    const interval = setInterval(verifyBackend, 25000)
    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [])

  // Handlers to link Crop / Disease results directly into the Chatbot
  const handleAskAboutCrop = (cropResult) => {
    setPredictionContext({
      type: 'crop',
      crop: cropResult.recommended_crop,
      confidence: cropResult.confidence,
      inputs: cropResult.inputs
    })
    setActiveTab('chat')
  }

  const handleAskAboutDisease = (diseaseResult) => {
    setPredictionContext({
      type: 'disease',
      plant: diseaseResult.plant,
      disease: diseaseResult.disease,
      confidence: diseaseResult.confidence
    })
    setActiveTab('chat')
  }

  return (
    <div className="app-container">
      {/* Top Header with Brand, Server Status, and Desktop Navigation Tabs */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendStatus={backendStatus}
        hasPredictionContext={Boolean(predictionContext)}
      />

      {/* Main Content Area (Layout never shifts when switching tabs) */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {activeTab === 'crop' && (
          <CropTab onAskChatbot={handleAskAboutCrop} />
        )}

        {activeTab === 'disease' && (
          <DiseaseTab onAskChatbot={handleAskAboutDisease} />
        )}

        {activeTab === 'chat' && (
          <ChatTab
            predictionContext={predictionContext}
            onClearContext={() => setPredictionContext(null)}
          />
        )}
      </main>

      {/* Footer Info */}
      <footer style={{
        marginTop: '2rem',
        paddingTop: '1rem',
        borderTop: '1px solid var(--border-light)',
        textAlign: 'center',
        fontSize: 'var(--fs-xs)',
        color: 'var(--text-muted)'
      }}>
        <p>Smart Agriculture Assistant • Decision Support for Agronomists & Growers</p>
      </footer>

      {/* Mobile Fixed Bottom Navigation Bar (< 768px) */}
      <BottomNav
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        hasPredictionContext={Boolean(predictionContext)}
      />
    </div>
  )
}
