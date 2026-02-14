import { useState, useEffect } from 'react';
import './App.css'; 
import { type Receta } from './types/receta';

function App() {
  const [input, setInput] = useState("");
  const [nuevaReceta, setNuevaReceta] = useState<Receta | null>(null);
  const [historial, setHistorial] = useState<Receta[]>([]);
  const [cargando, setCargando] = useState(false);
  const [recetaSeleccionada, setRecetaSeleccionada] = useState<Receta | null>(null);

  // Fem servir la IP 127.0.0.1 per evitar problemes de connexió amb alguns navegadors
  const API_BASE_URL = 'http://127.0.0.1:8000';

  // 1. Carregar historial (GET)
  const carregarHistorial = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/recetas`);
      if (!response.ok) throw new Error("Error al carregar historial");
      const data = await response.json();
      if (data.status === "success") {
        setHistorial(data.recetas); 
      }
    } catch (error) {
      console.error("Error connectant amb el servidor:", error);
    }
  };

  // Carreguem en iniciar
  useEffect(() => {
    carregarHistorial();
  }, []);

  // 2. Eliminar recepta (DELETE)
  const eliminarReceta = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation(); // Imprescindible perquè no s'obri el modal alhora
    if (!confirm("Segur que vols eliminar aquesta recepta?")) return;

    try {
      const response = await fetch(`${API_BASE_URL}/recetas/${id}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      
      if (data.status === "success") {
        setHistorial(prev => prev.filter(r => r.id !== id));
        if (nuevaReceta?.id === id) setNuevaReceta(null);
        if (recetaSeleccionada?.id === id) setRecetaSeleccionada(null);
      }
    } catch (error) {
      alert("No s'ha pogut eliminar la recepta. Revisa el backend.");
    }
  };

  // 3. Generar recepta (POST)
  const enviarIngredients = async () => {
    if (!input.trim()) return;
    setCargando(true);
    setNuevaReceta(null); // Netegem la pantalla mentre cuina

    try {
      const listaIngredients = input.split(',').map(i => i.trim());

      const response = await fetch(`${API_BASE_URL}/generar-receta`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredientes: listaIngredients }),
      });

      if (!response.ok) throw new Error("Error en la generació");

      const data = await response.json();
      if (data.status === "success") {
        setNuevaReceta(data.receta);
        setInput(""); 
        carregarHistorial(); // Refresquem l'historial automàticament
      }
    } catch (error) {
      console.error("Error generant recepta:", error);
      alert("Error de connexió: Assegura't que el servidor de Python està funcionant.");
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h2>Chef IA 🧑‍🍳</h2>
        <p className="subtitle">Digues què tens i t'ajudaré a cuinar</p>
      </header>
      
      <div className="input-group">
        <input 
          type="text" 
          placeholder="poma, ous, formatge..." 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={cargando}
        />
        <button onClick={enviarIngredients} disabled={cargando || !input}>
          {cargando ? "Cuinant..." : "Generar"}
        </button>
      </div>

      {/* Targeta de la nova recepta (destacada) */}
      {nuevaReceta && (
        <div 
          className="receta-card nueva-destacada" 
          onClick={() => setRecetaSeleccionada(nuevaReceta)}
        >
          <button className="delete-btn" onClick={(e) => eliminarReceta(nuevaReceta.id!, e)}>🗑️</button>
          <span className="badge-new">✨ Nova recepta!</span>
          <h3>{nuevaReceta.titulo}</h3>
          <p>{nuevaReceta.instrucciones.substring(0, 120)}...</p>
        </div>
      )}

      <hr className="divider" />

      <div className="historial">
        <h3>Historial de Recetas</h3>
        {historial.length === 0 && !cargando ? (
          <p className="empty-msg">Encara no has guardat cap recepta.</p>
        ) : (
          <div className="recetas-grid">
            {historial.map((receta) => (
              <div 
                key={receta.id} 
                className="receta-card" 
                onClick={() => setRecetaSeleccionada(receta)}
              >
                <button 
                  onClick={(e) => eliminarReceta(receta.id!, e)}
                  className="delete-btn"
                >
                  🗑️
                </button>
                
                <h4>{receta.titulo}</h4>
                <p>{receta.instrucciones.substring(0, 80)}...</p>
                <div className="card-footer">
                  <small>{new Date(receta.creado_el!).toLocaleDateString()}</small>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal Detallat */}
      {recetaSeleccionada && (
        <div className="modal-overlay" onClick={() => setRecetaSeleccionada(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-modal" onClick={() => setRecetaSeleccionada(null)}>×</button>
            <h2>{recetaSeleccionada.titulo}</h2>
            <div className="modal-body">
              <strong>📝 Instruccions:</strong>
              <p className="instrucciones-text">{recetaSeleccionada.instrucciones}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;