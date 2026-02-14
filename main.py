import os
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client
from groq import Groq
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <--- Afegeix això
# ... la resta d'imports (os, Groq, supabase, etc.)

app = FastAPI(title="Vacíate API")

# --- AFEGEIX AQUEST BLOC ARA ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet que qualsevol web es connecti
    allow_credentials=True,
    allow_methods=["*"],  # Permet tots els mètodes (GET, POST, etc.)
    allow_headers=["*"],
)
# -------------------------------

# Després continua el teu codi normal:
# supabase = create_client(...)

# 1. Carreguem claus
load_dotenv()
app = FastAPI(title="Vacíate API")

# Connectem serveis
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Model de dades per rebre ingredients
class IngredientsRequest(BaseModel):
    ingredientes: List[str]

# 3. La ruta que farà la feina
@app.post("/generar-receta")
async def generar_receta(request: IngredientsRequest):
    if not request.ingredientes:
        raise HTTPException(status_code=400, detail="No has enviat ingredients")

    try:
        # A. Demanem la recepta a Groq
        prompt = f"Crea una recepta amb: {', '.join(request.ingredientes)}. Respon NOMÉS en format JSON amb: titulo, ingredientes (llista), instrucciones."
        
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ets un xef català expert que respon en JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        receta_data = json.loads(completion.choices[0].message.content)

        # B. Guardem a Supabase
        res = supabase.table("recetas").insert({
            "titulo": receta_data.get("titulo") or receta_data.get("recepta"),
            "ingredientes": receta_data.get("ingredients") or receta_data.get("ingredientes"),
            "instrucciones": receta_data.get("instruccions") or receta_data.get("instrucciones"),
            "es_ia": True
        }).execute()

        return {"status": "success", "receta": res.data[0]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"status": "online", "mensaje": "Servidor de Vacíate preparat!"}

@app.get("/recetas")
async def llistar_recetas():
    try:
        # Demanem totes les receptes a Supabase ordenades per la més nova
        res = supabase.table("recetas").select("*").order("creado_el", desc=True).execute()
        return {"status": "success", "recetas": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))