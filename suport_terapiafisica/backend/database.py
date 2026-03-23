# ─────────────────────────────────────────────────────────────
# database.py
# Este archivo maneja la conexión entre Python y PostgreSQL
# ─────────────────────────────────────────────────────────────

# Importamos las herramientas para manejar la BD de forma asíncrona
# "Asíncrono" significa que el servidor no se bloquea esperando
# respuesta de la BD — puede atender otras peticiones mientras espera
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# dotenv nos permite leer el archivo .env
from dotenv import load_dotenv
import os

# ── Paso 1: Cargar las variables del archivo .env ─────────────
# Sin esta línea, os.getenv() no encontraría nada
load_dotenv()

# ── Paso 2: Armar la URL de conexión ─────────────────────────
# SQLAlchemy necesita una URL con este formato:
# postgresql+asyncpg://usuario:contraseña@host:puerto/base_de_datos
# Los valores vienen del archivo .env que creamos antes
DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ── Paso 3: Crear el motor de conexión ───────────────────────
# El "engine" es el objeto principal que maneja la conexión
# connect_args le dice a PostgreSQL que use el schema sch_clinica
# (equivalente a poner search_path=sch_clinica en tu consulta SQL)
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"server_settings": {"search_path": os.getenv("DB_SCHEMA")}}
)

# ── Paso 4: Crear la fábrica de sesiones ─────────────────────
# Una "sesión" es como una conversación temporal con la BD
# Cada vez que un endpoint necesite hacer una consulta,
# abrirá una sesión nueva y la cerrará al terminar
AsyncSessionLocal = sessionmaker(
    bind=engine,           # usa el motor que creamos arriba
    class_=AsyncSession,   # sesiones asíncronas
    expire_on_commit=False # los datos siguen disponibles después de guardar
)

# ── Paso 5: Función que provee la sesión a los endpoints ──────
# FastAPI llama a esta función automáticamente en cada endpoint
# que la solicite — abre la sesión, la entrega y luego la cierra
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session  # "yield" entrega la sesión y espera a que el endpoint termine