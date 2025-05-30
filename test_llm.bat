@echo off
chcp 65001 > nul
echo Bienvenido al Sistema de Chat en Español
echo ======================================
echo.

:: Activate virtual environment
call .venv\Scripts\activate

:: Run the Python WebSocket client
python chat_client.py

echo.
echo ¡Gracias por usar el sistema! ¡Hasta pronto!
pause 