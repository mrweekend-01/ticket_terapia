@echo off
echo =====================================================
echo   Hema Suport - Iniciando servidor desarrollo
echo =====================================================
echo.

cd /d "C:\Hema Suport\suport_terapiafisica\backend"
call venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8001
pause