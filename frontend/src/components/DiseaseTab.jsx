import React, { useState, useEffect, useRef } from 'react'
import { Stethoscope, UploadCloud, Camera, Trash2, Loader2, AlertCircle, Info, Sparkles, CheckCircle2 } from 'lucide-react'
import { getSupportedCrops, predictDisease } from '../api'
import ResultCard from './ResultCard'

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

const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024 // 10MB

export default function DiseaseTab({ onAskChatbot }) {
  const [crops, setCrops] = useState(DEFAULT_CROPS)
  const [selectedCrop, setSelectedCrop] = useState('apple')
  const [imageFile, setImageFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [isDragging, setIsDragging] = useState(false)

  const fileInputRef = useRef(null)

  // Fetch supported crops from backend
  useEffect(() => {
    getSupportedCrops()
      .then(list => {
        if (list && list.length > 0) setCrops(list)
      })
      .catch(() => {})
  }, [])

  const handleProcessFile = (file) => {
    if (!file) return

    // Type validation
    if (!ALLOWED_TYPES.includes(file.type.toLowerCase()) && !/\.(jpe?g|png|webp)$/i.test(file.name)) {
      setError('Unsupported file type. Please upload a JPG, PNG, or WEBP image.')
      return
    }

    // Size validation
    if (file.size > MAX_FILE_SIZE_BYTES) {
      const sizeMb = (file.size / (1024 * 1024)).toFixed(1)
      setError(`File size (${sizeMb} MB) exceeds maximum allowed 10 MB limit.`)
      return
    }

    setError('')
    setImageFile(file)
    setPreviewUrl(URL.createObjectURL(file))
    setResult(null)
  }

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (file) handleProcessFile(file)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) handleProcessFile(file)
  }

  const handleRemoveImage = () => {
    setImageFile(null)
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl('')
    setResult(null)
    setError('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!imageFile) {
      setError('Please upload or snap a leaf photo before submitting.')
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
    <section className="card">
      {/* Title */}
      <div style={{ marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: 'var(--fs-xl)', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Stethoscope size={22} color="var(--primary)" />
          Plant Leaf Disease Diagnosis
        </h2>
        <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Diagnose foliar diseases across 13 commercial crops using deep convolutional neural networks (ResNet50).
        </p>
      </div>

      {/* Model warmup notice */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.5rem',
        padding: '0.75rem 1rem',
        borderRadius: 'var(--radius-md)',
        background: 'var(--primary-light)',
        border: '1px solid var(--primary-subtle-border)',
        color: 'var(--primary)',
        fontSize: 'var(--fs-xs)',
        lineHeight: 1.45,
        marginBottom: '1.25rem'
      }}>
        <Info size={16} flexShrink={0} style={{ marginTop: '2px' }} />
        <span>
          <strong>Pro-tip:</strong> The first diagnosis for a selected crop may take 5–15 seconds while the deep learning model weights load into server memory. Subsequent queries are near-instant.
        </span>
      </div>

      {/* Error alert */}
      {error && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-md)',
          background: 'var(--danger-bg)',
          border: '1px solid var(--danger-border)',
          color: 'var(--danger)',
          fontSize: 'var(--fs-sm)',
          marginBottom: '1.25rem'
        }}>
          <AlertCircle size={18} flexShrink={0} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Plant / Crop Selector */}
        <div style={{ marginBottom: '1.25rem' }}>
          <label htmlFor="crop-select" style={{
            display: 'block',
            fontSize: 'var(--fs-sm)',
            fontWeight: 600,
            color: 'var(--text-secondary)',
            marginBottom: '0.35rem'
          }}>
            Select Crop Species
          </label>
          <select
            id="crop-select"
            value={selectedCrop}
            onChange={(e) => {
              setSelectedCrop(e.target.value)
              setResult(null)
            }}
            className="form-select"
            style={{ fontWeight: 500 }}
          >
            {crops.map(c => (
              <option key={c.key} value={c.key}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        {/* Drag and drop / Tap / Camera upload box */}
        {!previewUrl ? (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: `2px dashed ${isDragging ? 'var(--primary)' : 'var(--border-medium)'}`,
              borderRadius: 'var(--radius-lg)',
              padding: '2.5rem 1rem',
              textAlign: 'center',
              backgroundColor: isDragging ? 'var(--primary-light)' : 'var(--surface-raised)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem'
            }}
          >
            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              background: 'var(--primary-subtle)',
              color: 'var(--primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <UploadCloud size={28} />
            </div>

            <div>
              <p style={{ fontSize: 'var(--fs-base)', fontWeight: 600, color: 'var(--text-main)' }}>
                Drag & drop leaf photo, or <span style={{ color: 'var(--primary)', textDecoration: 'underline' }}>browse</span>
              </p>
              <p style={{ fontSize: 'var(--fs-xs)', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Supports JPG, PNG, WEBP up to 10 MB. Camera capture supported on mobile.
              </p>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              capture="environment"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
          </div>
        ) : (
          /* Image Preview with Remove Button */
          <div style={{
            position: 'relative',
            borderRadius: 'var(--radius-lg)',
            overflow: 'hidden',
            border: '1px solid var(--border-medium)',
            background: 'var(--surface-raised)',
            padding: '1rem',
            textAlign: 'center'
          }}>
            <img
              src={previewUrl}
              alt="Uploaded plant leaf"
              style={{
                maxWidth: '100%',
                maxHeight: '320px',
                borderRadius: 'var(--radius-md)',
                objectFit: 'contain',
                display: 'block',
                margin: '0 auto'
              }}
            />

            <div style={{
              marginTop: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem'
            }}>
              <button
                type="button"
                onClick={handleRemoveImage}
                className="btn-secondary"
                style={{ color: 'var(--danger)', borderColor: 'var(--danger-border)' }}
              >
                <Trash2 size={16} />
                <span>Remove & Choose Different Photo</span>
              </button>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !imageFile}
          className="btn-primary"
          style={{ width: '100%', marginTop: '1.25rem', minHeight: '48px' }}
        >
          {loading ? (
            <>
              <Loader2 size={20} className="spin-icon" />
              <span>Analyzing Leaf Pathology with ResNet50...</span>
            </>
          ) : (
            <>
              <Sparkles size={20} />
              <span>Diagnose Leaf Disease</span>
            </>
          )}
        </button>
      </form>

      {/* Disease Diagnosis Result */}
      {result && (
        <ResultCard
          type="disease"
          title={`${result.plant} — ${result.disease}`}
          subtitle={result.is_healthy ? 'Leaf exhibits normal chlorophyll and tissue structure.' : 'Pathogenic symptoms detected by convolutional classification model.'}
          confidence={result.confidence}
          isHealthy={result.is_healthy}
          actionLabel="Ask the chatbot how to treat and manage this"
          onAction={() => onAskChatbot(result)}
        />
      )}
    </section>
  )
}
