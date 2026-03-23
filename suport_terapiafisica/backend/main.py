# ─────────────────────────────────────────────────────────────
# main.py
# Archivo principal del servidor FastAPI
# Aquí se definen todos los endpoints y el WebSocket
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# Importamos nuestra conexión a la BD y los modelos
from database import get_db
from models import TicketUpdate, TicketResponse, MedicoResponse

from dotenv import load_dotenv
from typing import List
import json

load_dotenv()

# ── Crear la aplicación FastAPI ───────────────────────────────
# Este objeto "app" es el servidor completo
app = FastAPI(
    title="Hema Suport - Terapia Fisica",
    description="Backend para gestión de tickets clínicos",
    version="1.0.0"
)

# ── Configurar CORS ───────────────────────────────────────────
# CORS permite que el frontend (React) pueda hablar con este servidor
# Sin esto, el navegador bloquearía las peticiones por seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Lista de clientes WebSocket conectados ────────────────────
# Cada vez que alguien abre la app se agrega a esta lista
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
async def notificar_cambio(codigo: int, mensaje: str):
    data = json.dumps({"codigo": codigo, "mensaje": mensaje})
    for cliente in clientes:
        try:
            await cliente.send_text(data)
        except:
            pass


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────

# ── GET / ─────────────────────────────────────────────────────
# Verifica que el servidor está corriendo
@app.get("/")
async def inicio():
    return {"mensaje": "Servidor Hema Suport funcionando correctamente"}


# ── GET /ticket/{codigo} ──────────────────────────────────────
# Busca un ticket por su código
# Ejemplo: GET http://localhost:8000/ticket/103520
@app.get("/ticket/{codigo}")
async def obtener_ticket(
    codigo: int,
    db: AsyncSession = Depends(get_db)
):
    query = text("""
        SELECT
            tts.tratamiento_sesion_tcod,
            tts.tratamiento_sesion_fprogramada,
            tts.tratamiento_sesion_pacod,
            TRIM(
                tp.persona_nmb1 || ' ' ||
                COALESCE(tp.persona_nmb2, '') || ' ' ||
                tp.persona_apep || ' ' ||
                tp.persona_apem
            ) AS nombre_medico
        FROM tbl_tratamiento_sesion tts
        INNER JOIN tbl_persona tp
            ON tp.persona_cod = tts.tratamiento_sesion_pacod
        WHERE tts.tratamiento_sesion_tcod = :codigo
        ORDER BY tts.tratamiento_sesion_fprogramada DESC
        LIMIT 1
    """)

    result = await db.execute(query, {"codigo": codigo})
    ticket = result.mappings().first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró el ticket con código {codigo}"
        )

    return dict(ticket)


# ── PUT /ticket/{codigo} ──────────────────────────────────────
# Actualiza la fecha y el médico de un ticket
@app.put("/ticket/{codigo}")
async def actualizar_ticket(
    codigo: int,
    datos: TicketUpdate,
    db: AsyncSession = Depends(get_db)
):
    # Verificar que el ticket existe
    check = text("""
        SELECT tratamiento_sesion_tcod
        FROM tbl_tratamiento_sesion
        WHERE tratamiento_sesion_tcod = :codigo
    """)
    result = await db.execute(check, {"codigo": codigo})
    if not result.first():
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró el ticket con código {codigo}"
        )

    # Ejecutar el UPDATE
    query = text("""
        UPDATE tbl_tratamiento_sesion
        SET
            tratamiento_sesion_fprogramada = :fecha,
            tratamiento_sesion_pacod       = :medico_cod
        WHERE tratamiento_sesion_tcod = :codigo
    """)
    await db.execute(query, {
        "fecha":      datos.tratamiento_sesion_fprogramada,
        "medico_cod": datos.tratamiento_sesion_pacod,
        "codigo":     codigo
    })

    await db.commit()

    # Notificar a todos los clientes conectados
    await notificar_cambio(codigo, f"Ticket {codigo} actualizado correctamente")

    return {"ok": True, "codigo": codigo, "mensaje": "Ticket actualizado correctamente"}


# ── GET /medicos ──────────────────────────────────────────────
# Devuelve la lista de médicos para el dropdown del formulario
@app.get("/medicos")
async def listar_medicos(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT
            persona_cod,
            TRIM(
                persona_nmb1 || ' ' ||
                COALESCE(persona_nmb2, '') || ' ' ||
                persona_apep || ' ' ||
                persona_apem
            ) AS nombre_completo
        FROM tbl_persona
        WHERE persona_tipo = 'M'
        ORDER BY persona_apep, persona_nmb1
    """)

    result = await db.execute(query)
    medicos = result.mappings().all()

    return [dict(m) for m in medicos]