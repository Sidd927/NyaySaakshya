import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource/ibm-plex-sans/400.css'
import '@fontsource/ibm-plex-sans/500.css'
import '@fontsource/ibm-plex-sans/600.css'
import '@fontsource/ibm-plex-sans/700.css'
import '@fontsource/ibm-plex-mono/400.css'
import '@fontsource/ibm-plex-mono/500.css'
import '@fontsource/ibm-plex-mono/600.css'
import '@fontsource/ibm-plex-mono/700.css'
// Brand layer. Subset files, one weight each: a face is only fetched when text falls
// through the font stack to it (see --brand-font-record / --brand-font-ui).
import '@fontsource/ibm-plex-serif/latin-500.css'
import '@fontsource/tiro-devanagari-marathi/devanagari-400.css'
import '@fontsource/ibm-plex-sans-devanagari/devanagari-400.css'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
