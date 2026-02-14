import os
import json
from datetime import datetime
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client
from groq import Groq

# 1. Carreguem les claus del fitxer .env
load_dotenv()

# 2. Creem l'aplicació
app = FastAPI(title="Vacíate API - Edició Xef Gourmet")

# 3. Configurem el CORS per al Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Connectem amb els serveis
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 5. Model de dades
class IngredientsRequest(BaseModel):
    ingredientes: List[str]

# --- RUTES ---

@app.get("/")
def home():
    return {"status": "online", "mensaje": "El xef de Vacíate està a la cuina!"}

@app.post("/generar-receta")
async def generar_receta(request: IngredientsRequest):
    if not request.ingredientes:
        raise HTTPException(status_code=400, detail="No has enviat ingredients")

    try:
        # A. Prompt millorat amb lògica d'humor, calories, temps i validació
        prompt = f"""
        Actua com un xef català expert i amb molt de sentit de l'humor. 
        Ingredients rebuts: {', '.join(request.ingredientes)}.
        
        INSTRUCCIONS:
        1. Si els ingredients NO són comestibles (ex: pedres, cargols de ferro, sabó, mòbils), respon amb un JSON que tingui NOMÉS un camp "error" amb una crítica divertida.
        2. Si són comestibles, crea una recepta i respon NOMÉS en format JSON amb aquesta estructura:
        {{
            "titulo": "nom creatiu de la recepta",
            "ingredientes": ["llista detallada"],
            "instrucciones": ["passos a seguir"],
            "calories": "estimació aprox (ex: 450 kcal)",
            "tiempo": "temps aprox (ex: 25 minuts)",
            "humor": "un comentari curt i divertit sobre aquesta combinació"
        }}
        """
        
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Ets un xef expert que només respon en JSON i detecta si el que li donen es pot menjar."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        receta_data = json.loads(completion.choices[0].message.content)

        # B. Si la IA detecta que no és menjar, no guardem a la DB i enviem l'error
        if "error" in receta_data:
            return {"status": "error", "message": receta_data["error"]}

        # C. Guardem a Supabase
        # Nota: Hem afegit 'calories' i 'tiempo' al insert. 
        # Si no tens les columnes a la DB, aquesta part podria donar error fins que les creis.
        res = supabase.table("recetas").insert({
            "titulo": receta_data.get("titulo"),
            "ingredientes": receta_data.get("ingredientes"),
            "instrucciones": receta_data.get("instrucciones"),
            "calories": receta_data.get("calories"), # Opcional: crea la columna a Supabase
            "tiempo": receta_data.get("tiempo"),     # Opcional: crea la columna a Supabase
            "es_ia": True
        }).execute()

        # Tornem la recepta completa (amb l'humor inclòs per al front-end)
        return {
            "status": "success", 
            "receta": receta_data,
            "id_database": res.data[0]["id"] if res.data else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recetas")
async def llistar_recetas():
    try:
        res = supabase.table("recetas")\
            .select("*")\
            .is_("borrado_el", "null")\
            .order("creado_el", desc=True)\
            .execute()
        return {"status": "success", "recetas": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/recetas/{receta_id}")
async def marcar_como_borrada(receta_id: int):
    try:
        res = supabase.table("recetas").update({
            "borrado_el": datetime.now().isoformat()
        }).eq("id", receta_id).execute()
        
        if not res.data:
            raise HTTPException(status_code=404, detail="Recepta no trobada")
            
        return {"status": "success", "message": f"Recepta {receta_id} enviada a la paperera."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))