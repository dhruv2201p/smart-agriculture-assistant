import React from 'react'
import { Sprout, CheckCircle2, AlertTriangle, MessageSquare, ArrowRight } from 'lucide-react'

export default function ResultCard({
  type, // 'crop' | 'disease'
  title,
  subtitle,
  confidence,
  isHealthy,
  onAction,
  actionLabel
}) {
  const isDisease = type === 'disease'
  const badgeColor = isHealthy ? 'var(--success)' : (isDisease ? 'var(--warning)' : 'var(--primary)')
  const badgeBg = isHealthy ? 'var(--success-bg)' : (isDisease ? 'var(--warning-bg)' : 'var(--primary-subtle)')
  const badgeBorder = isHealthy ? 'var(--success-border)' : (isDisease ? 'var(--warning-border)' : 'var(--primary-subtle-border)')

  // Clamped confidence between 0 and 100
  const confValue = Math.min(Math.max(Number(confidence) || 0, 0), 100)

  return (
    <div style={{
      marginTop: '1.5rem',
      padding: '1.25rem',
      borderRadius: 'var(--radius-lg)',
      background: 'var(--surface-raised)',
      border: `1.5px solid ${badgeBorder}`,
      boxShadow: 'var(--shadow-md)',
      transition: 'all 0.25s ease'
    }}>
      {/* Top Header with Status/Type Badge */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem',
        marginBottom: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: 'var(--radius-md)',
            background: badgeBg,
            color: badgeColor,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0
          }}>
            {isDisease ? (
              isHealthy ? <CheckCircle2 size={22} /> : <AlertTriangle size={22} />
            ) : (
              <Sprout size={22} />
            )}
          </div>

          <div>
            <span style={{
              fontSize: 'var(--fs-xs)',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: badgeColor
            }}>
              {isDisease ? (isHealthy ? 'Healthy Specimen' : 'Condition Detected') : 'Recommended Optimal Crop'}
            </span>
            <h3 style={{
              fontSize: 'var(--fs-2xl)',
              fontWeight: 800,
              color: 'var(--text-main)',
              lineHeight: 1.2,
              textTransform: 'capitalize',
              margin: '2px 0 0 0'
            }}>
              {title}
            </h3>
            {subtitle && (
              <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--text-muted)' }}>
                {subtitle}
              </p>
            )}
          </div>
        </div>

        {/* Confidence Badge */}
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.35rem',
          padding: '0.35rem 0.75rem',
          borderRadius: 'var(--radius-pill)',
          background: 'var(--surface)',
          border: '1px solid var(--border-light)',
          fontSize: 'var(--fs-sm)',
          fontWeight: 700,
          color: 'var(--text-main)'
        }}>
          <span>Confidence:</span>
          <span style={{ color: badgeColor }}>{confValue.toFixed(1)}%</span>
        </div>
      </div>

      {/* Confidence Progress Bar */}
      <div style={{ marginBottom: '1.25rem' }}>
        <div style={{
          height: '8px',
          width: '100%',
          backgroundColor: 'var(--border-light)',
          borderRadius: 'var(--radius-pill)',
          overflow: 'hidden'
        }}>
          <div style={{
            height: '100%',
            width: `${confValue}%`,
            backgroundColor: badgeColor,
            borderRadius: 'var(--radius-pill)',
            transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)'
          }} />
        </div>
      </div>

      {/* Action to switch to Chatbot with Context */}
      {onAction && (
        <button
          type="button"
          onClick={onAction}
          className="btn-primary"
          style={{
            width: '100%',
            justifyContent: 'space-between',
            background: 'var(--surface)',
            color: 'var(--primary)',
            border: '1.5px solid var(--primary)',
            boxShadow: 'none'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--primary-light)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'var(--surface)'
          }}
        >
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
            <MessageSquare size={18} />
            <span>{actionLabel || 'Ask the Agriculture Chatbot about this'}</span>
          </span>
          <ArrowRight size={18} />
        </button>
      )}
    </div>
  )
}
