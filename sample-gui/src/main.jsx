import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

import { PostHogProvider, PostHogErrorBoundary } from '@posthog/react'

const options = {
  api_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
  autocapture: true,
  capture_pageview: false // We already capture pageviews manually in App.jsx tab changes
}

const FallbackComponent = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', background: 'var(--bg-app)', color: 'var(--text-main)', fontFamily: 'sans-serif' }}>
      <h2 style={{ fontSize: '24px', fontWeight: 'bold' }}>Something went wrong.</h2>
      <p style={{ color: 'var(--text-secondary)', marginTop: '10px' }}>An error was detected and reported to Horizon Desk.</p>
      <button 
        onClick={() => window.location.reload()}
        style={{ marginTop: '20px', padding: '8px 16px', background: 'var(--accent)', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
      >
        Reload Application
      </button>
    </div>
  )
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <PostHogProvider apiKey={import.meta.env.VITE_PUBLIC_POSTHOG_KEY} options={options}>
      <PostHogErrorBoundary fallback={<FallbackComponent />}>
        <App />
      </PostHogErrorBoundary>
    </PostHogProvider>
  </StrictMode>
)
