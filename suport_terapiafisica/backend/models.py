# ─────────────────────────────────────────────────────────────
# models.py
# Define la estructura de los datos que entran y salen del API
# Pydantic valida automáticamente que los datos sean correctos
# ─────────────────────────────────────────────────────────────

# BaseModel es la clase base de Pydantic para crear modelos
from pydantic import BaseModel

# date nos permite trabajar con fechas (año-mes-dia)
from datetime import date

# Optional permite campos que pueden venir vacíos
from typing import Optional


# ── Modelo para actualizar un ticket ─────────────────────────
# Este es el "molde" de los datos que manda el frontend
# cuando las chicas de admisión guardan los cambios
class TicketUpdate(BaseModel):
    # La nueva fecha de la cita — debe ser una fecha válida
    # Pydantic rechaza automáticamente valores como "hola" o "32/13/2024"
    tratamiento_sesion_fprogramada: date

    # El código del médico seleccionado — debe ser un número entero
    # Este código es la FK que apunta a tbl_persona
    tratamiento_sesion_pacod: int


# ── Modelo de respuesta del ticket ───────────────────────────
# Define qué datos devuelve el servidor cuando se busca un ticket
# Optional significa que algunos campos podrían venir vacíos de la BD
class TicketResponse(BaseModel):
    tratamiento_sesion_tcod: int          # código del ticket
    tratamiento_sesion_fprogramada: date  # fecha de la cita
    tratamiento_sesion_pacod: int         # código del médico
    nombre_medico: Optional[str]          # nombre completo del médico


# ── Modelo de respuesta para la lista de médicos ─────────────
# Define la estructura de cada médico en el dropdown del formulario
class MedicoResponse(BaseModel):
    persona_cod: int        # código único del médico (para guardar en BD)
    nombre_completo: str    # nombre para mostrar en pantalla