# ─────────────────────────────────────────────────────────────
# models.py
# Define la estructura de los datos que entran y salen del API
# ─────────────────────────────────────────────────────────────

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


# ── Modelo para actualizar una sesión específica ──────────────
class TicketUpdate(BaseModel):
    tratamiento_sesion_cod: int              # llave primaria de la sesión
    tratamiento_sesion_fprogramada: datetime # nueva fecha y hora
    tratamiento_sesion_pacod: int            # nuevo médico


# ── Modelo de respuesta del ticket ───────────────────────────
class TicketResponse(BaseModel):
    tratamiento_sesion_cod: int              # llave primaria de la sesión
    tratamiento_sesion_tcod: int             # código del ticket
    tratamiento_sesion_fprogramada: datetime # fecha y hora de la cita
    tratamiento_sesion_pacod: int            # código del médico
    nombre_medico: Optional[str]             # nombre completo del médico


# ── Modelo de respuesta para la lista de médicos ─────────────
class MedicoResponse(BaseModel):
    persona_cod: int        # código único del médico
    nombre_completo: str    # nombre para mostrar en pantalla