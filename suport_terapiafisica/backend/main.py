# ─────────────────────────────────────────────────────────────
# main.py
# Archivo principal — solo arranca la app y registra los routers
# Toda la lógica está separada en la carpeta routers/
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import List
import json

# Importamos los routers de cada módulo
from routers import tickets, medicos, especialidades

load_dotenv()

# ── Crear la aplicación FastAPI ───────────────────────────────
app = FastAPI(
    title="Hema Suport - Terapia Fisica",
    description="Backend para gestión de tickets clínicos",
    version="1.0.0"
)

# ── Configurar CORS ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registrar los routers ─────────────────────────────────────
# Cada router trae sus propios endpoints
app.include_router(tickets.router)
app.include_router(medicos.router)
app.include_router(especialidades.router)

# ── Lista de clientes WebSocket conectados ────────────────────
clientes: List[WebSocket] = []


# ── WebSocket ─────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clientes.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clientes.remove(websocket)


# ── Notificar cambios a todos los clientes ────────────────────
async def notificar_cambio(cod: int, mensaje: str):
    data = json.dumps({"cod": cod, "mensaje": mensaje})
    for cliente in clientes:
        try:
            await cliente.send_text(data)
        except:
            pass


# ── GET / ─────────────────────────────────────────────────────
@app.get("/")
async def inicio():
    return {"mensaje": "Servidor Hema Suport funcionando correctamente"}
