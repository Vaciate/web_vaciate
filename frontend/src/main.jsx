import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx' // Aquesta és la línia que fallava

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)