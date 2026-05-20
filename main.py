from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI()

# Configurar CORS (permite que el frontend hable con el backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar el modelo de IA
print("Cargando modelo... (esto toma 1-2 minutos la primera vez)")
modelo_nombre = "microsoft/DialoGPT-small"
tokenizer = AutoTokenizer.from_pretrained(modelo_nombre)
modelo = AutoModelForCausalLM.from_pretrained(modelo_nombre)
print("✅ Modelo cargado exitosamente")

# Diccionario para guardar conversaciones por usuario
conversaciones = {}

class Mensaje(BaseModel):
    texto: str
    session_id: str = "default"

def generar_respuesta(mensaje_usuario, historial_ids):
    # Convertir texto a números que el modelo entiende
    nuevos_ids = tokenizer.encode(mensaje_usuario + tokenizer.eos_token, return_tensors='pt')
    
    # Unir con historial
    if historial_ids is not None:
        entrada_ids = torch.cat([historial_ids, nuevos_ids], dim=-1)
    else:
        entrada_ids = nuevos_ids
    
    # Generar respuesta
    salida_ids = modelo.generate(
        entrada_ids, 
        max_length=1000,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.7
    )
    
    # Extraer solo la parte nueva de la respuesta
    respuesta_texto = tokenizer.decode(salida_ids[:, entrada_ids.shape[-1]:][0], skip_special_tokens=True)
    
    return respuesta_texto, salida_ids

# ENDPOINT para que el frontend envíe mensajes
@app.post("/chat")
async def chat(mensaje: Mensaje):
    historia = conversaciones.get(mensaje.session_id)
    respuesta, nuevo_historial = generar_respuesta(mensaje.texto, historia)
    conversaciones[mensaje.session_id] = nuevo_historial
    return {"respuesta": respuesta}

# SERVIR el frontend (archivos estáticos)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def mostrar_frontend():
    return FileResponse("static/index.html")

# EJECUTAR el servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)