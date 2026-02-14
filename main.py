import os
import json
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client
from groq import Groq

# 1. Carreguem les claus del fitxer .env primer de tot
load_dotenv()

# 2. Creem l'aplicació UNA SOLA VEGADA
app = FastAPI(title="Vacíate API")

# 3. Configurem el CORS (Súper important per al teu amic del Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Connectem amb els serveis externs
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 5. Model de dades (El contracte del JSON)
class IngredientsRequest(BaseModel):
    ingredientes: List[str]

# --- RUTES ---

@app.get("/")
def home():
    return {"status": "online", "mensaje": "Servidor de Vacíate preparat!"}

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

@app.get("/recetas")
async def llistar_recetas():
    try:
        res = supabase.table("recetas").select("*").order("creado_el", desc=True).execute()
        return {"status": "success", "recetas": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))