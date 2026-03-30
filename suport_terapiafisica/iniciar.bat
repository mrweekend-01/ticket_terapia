@echo off
echo =====================================================
echo   Hema Suport - Iniciando servidor...
echo =====================================================
echo.

:: Limpiar log del dia anterior
echo. > "C:\HemaSuport\logs\servidor.log"

:: Ir a la carpeta del backend
cd /d "C:\HemaSuport\backend"

:: Activar entorno virtual
call venv\Scripts\activate

:: Arrancar servidor guardando logs
echo [%date% %time%] Servidor iniciado >> "C:\HemaSuport\logs\servidor.log"
uvicorn main:app --host 0.0.0.0 --port 8001 >> "C:\HemaSuport\logs\servidor.log" 2>&1