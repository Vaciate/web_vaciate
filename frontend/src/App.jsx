import { useState } from 'react'
import axios from 'axios'

function App() {
  const [ingredients, setIngredients] = useState("")
  const [receta, setReceta] = useState(null)

  const cuinar = async () => {
    try {
      // Recorda que el teu main.py ara està a la carpeta backend/
      const res = await axios.post('http://localhost:8000/generar-receta', {
        ingredientes: ingredients.split(",").map(i => i.trim())
      })
      setReceta(res.data.receta)
    } catch (err) {
      alert("Error connectant amb el Backend. Està encès el main.py dins de /backend?")
    }
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Vacíate 🍳</h1>
      <input 
        placeholder="ous, patates..." 
        value={ingredients} 
        onChange={(e) => setIngredients(e.target.value)} 
      />
      <button onClick={cuinar}>Generar Recepta</button>

      {receta && (
        <div style={{ marginTop: '20px' }}>
          <h2>{receta.titulo}</h2>
          <p><em>{receta.humor}</em></p>
          <p>{receta.instrucciones}</p>
        </div>
      )}
    </div>
  )
}

export default App