# ─────────────────────────────────────────────────────────────
# routers/tickets.py
# Endpoints relacionados a tickets y sesiones
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
from models import TicketUpdate
import json

# APIRouter es como un mini FastAPI solo para este grupo de endpoints
router = APIRouter()


# ── GET /ticket/{codigo} ──────────────────────────────────────
# Devuelve la última sesión de un ticket
@router.get("/ticket/{codigo}")
async def obtener_ticket(
    codigo: int,
    db: AsyncSession = Depends(get_db)
):
    query = text("""
        SELECT
            tts.tratamiento_sesion_cod,
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


# ── GET /ticket/{codigo}/sesiones ─────────────────────────────
# Devuelve todas las sesiones de un ticket
@router.get("/ticket/{codigo}/sesiones")
async def obtener_sesiones(
    codigo: int,
    db: AsyncSession = Depends(get_db)
):
    query = text("""
        SELECT
            tts.tratamiento_sesion_cod,
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
    """)

    result = await db.execute(query, {"codigo": codigo})
    sesiones = result.mappings().all()

    if not sesiones:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron sesiones para el ticket {codigo}"
        )

    return [dict(s) for s in sesiones]


# ── PUT /ticket/sesion ────────────────────────────────────────
# Modifica fecha y médico de una sesión específica
@router.put("/ticket/sesion")
async def actualizar_sesion(
    datos: TicketUpdate,
    db: AsyncSession = Depends(get_db)
):
    # Verificar que la sesión existe
    check = text("""
        SELECT tratamiento_sesion_cod
        FROM tbl_tratamiento_sesion
        WHERE tratamiento_sesion_cod = :cod
    """)
    result = await db.execute(check, {"cod": datos.tratamiento_sesion_cod})
    if not result.first():
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró la sesión {datos.tratamiento_sesion_cod}"
        )

    # Actualizar solo esa sesión
    query = text("""
        UPDATE tbl_tratamiento_sesion
        SET
            tratamiento_sesion_fprogramada = :fecha,
            tratamiento_sesion_pacod       = :medico_cod
        WHERE tratamiento_sesion_cod = :cod
    """)
    await db.execute(query, {
        "fecha":      datos.tratamiento_sesion_fprogramada,
        "medico_cod": datos.tratamiento_sesion_pacod,
        "cod":        datos.tratamiento_sesion_cod
    })

    await db.commit()

    return {
        "ok": True,
        "cod": datos.tratamiento_sesion_cod,
        "mensaje": "Sesión actualizada correctamente"
    }