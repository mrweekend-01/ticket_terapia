# ─────────────────────────────────────────────────────────────
# routers/medicos.py
# Endpoints relacionados a médicos
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db

router = APIRouter()


# ── GET /medicos/{especialidad} ───────────────────────────────
# Devuelve médicos filtrados por especialidad
# Ejemplo: /medicos/CM → solo médicos
# Ejemplo: /medicos/TM → solo técnicos médicos
@router.get("/medicos/{especialidad}")
async def listar_medicos_por_especialidad(
    especialidad: str,
    db: AsyncSession = Depends(get_db)
):
    query = text("""
        SELECT
            tp.persona_cod,
            TRIM(
                tp.persona_nmb1 || ' ' ||
                COALESCE(tp.persona_nmb2, '') || ' ' ||
                tp.persona_apep || ' ' ||
                tp.persona_apem
            ) AS nombre_completo
        FROM tbl_persona tp
        JOIN tbl_profatencion tp2
            ON tp.persona_cod = tp2.profatencion_persona_cod
        WHERE tp2.profatencion_tprofatencion_cod = :especialidad
        ORDER BY tp.persona_apep, tp.persona_nmb1
    """)

    result = await db.execute(query, {"especialidad": especialidad})
    medicos = result.mappings().all()

    if not medicos:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron médicos para la especialidad {especialidad}"
        )

    return [dict(m) for m in medicos]