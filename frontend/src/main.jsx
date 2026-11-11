import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './studio.css'
import App from './App.jsx'

// Keep the previous presentation available without touching reference data.
try {
  document.documentElement.dataset.presentation = localStorage.getItem('refedia-presentation') === 'classic' ? 'classic' : 'studio'
} catch {
  document.documentElement.dataset.presentation = 'studio'
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
