# ─────────────────────────────────────────────────────────────
# routers/especialidades.py
# Endpoints relacionados a especialidades
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db

router = APIRouter()


# ── GET /especialidades ───────────────────────────────────────
# Devuelve la lista de especialidades para el primer dropdown
# Excluye la especialidad NA
@router.get("/especialidades")
async def listar_especialidades(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT
            tpprofatencion_cod,
            tpprofatencion_dsc
        FROM tbl_tpprofatencion
        WHERE tpprofatencion_cod != 'NA'
        ORDER BY tpprofatencion_dsc
    """)

    result = await db.execute(query)
    especialidades = result.mappings().all()

    return [dict(e) for e in especialidades]