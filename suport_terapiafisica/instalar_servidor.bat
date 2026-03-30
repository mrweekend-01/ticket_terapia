@echo off
echo =====================================================
echo   Hema Suport - Instalador completo del servidor
echo =====================================================
echo.

:: ── Verificar Python ─────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado.
    echo Descargalo desde https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH"
    pause
    exit
)
echo [OK] Python encontrado
echo.

:: ── Crear carpeta del proyecto ────────────────────────
echo [1/6] Creando estructura de carpetas...
mkdir "C:\HemaSuport\backend" 2>nul
mkdir "C:\HemaSuport\logs" 2>nul
echo [OK] Carpetas creadas

:: ── Copiar archivos del proyecto ──────────────────────
echo [2/6] Copiando archivos del proyecto...
xcopy "%~dp0backend" "C:\HemaSuport\backend" /E /I /Y /EXCLUDE:%~dp0exclude.txt
echo [OK] Archivos copiados

:: ── Crear entorno virtual ─────────────────────────────
echo [3/6] Creando entorno virtual...
cd /d "C:\HemaSuport\backend"
python -m venv venv
echo [OK] Entorno virtual creado

:: ── Instalar dependencias ─────────────────────────────────
echo [4/6] Instalando dependencias...
cd /d "C:\HemaSuport\backend"
call venv\Scripts\activate
pip install fastapi uvicorn[standard] sqlalchemy asyncpg python-dotenv
echo [OK] Dependencias instaladas

:: ── Crear tarea programada de arranque ────────────────
echo [5/6] Configurando arranque automatico...
schtasks /create /tn "HemaSuport-Backend" /tr "C:\HemaSuport\iniciar.bat" /sc onstart /rl highest /f
echo [OK] Arranque automatico configurado

:: ── Crear tarea de reinicio a las 12am ───────────────
echo [6/6] Configurando reinicio diario 12am...
schtasks /create /tn "HemaSuport-Reinicio" /tr "taskkill /f /im uvicorn.exe" /sc daily /st 00:00 /rl highest /f
echo [OK] Reinicio diario configurado

:: ── Copiar iniciar.bat ────────────────────────────────
copy "%~dp0iniciar.bat" "C:\HemaSuport\iniciar.bat" /Y

echo.
echo =====================================================
echo   Instalacion completada exitosamente
echo   El servidor arrancara automaticamente
echo   al iniciar Windows en el puerto 8001
echo =====================================================
echo.
echo Iniciando servidor ahora...
start "" "C:\HemaSuport\iniciar.bat"
pause
```

---

También crea el archivo **`exclude.txt`** en la misma carpeta:
```
venv\
__pycache__\
*.pyc
.git\
```

---

### En el USB solo necesitas copiar:
```
USB/
├── INSTALAR_SERVIDOR.bat  ← doble click y listo
├── exclude.txt
├── iniciar.bat
└── backend/
    ├── routers/
    ├── .env
    ├── main.py
    ├── database.py
    ├── models.py
    └── requirements.txt   ← genera con pip freeze
```

---

### En el servidor solo hacen:
```
1. Conectar USB
2. Doble click en INSTALAR_SERVIDOR.bat
3. Listo — el servidor arranca solo y queda configurado para siempre