@echo off
chcp 65001 > nul
echo Bienvenido al Sistema de Chat en Español
echo ======================================
echo.

:: Activate virtual environment
call venv\Scripts\activate

:chat_loop
echo.
set /p query="Tú: "
if "%query%"=="" goto chat_loop
if /i "%query%"=="salir" goto end
if /i "%query%"=="exit" goto end

echo.
echo Dr. Simi: 
curl -s -X POST "http://localhost:8000/query" ^
-H "Content-Type: application/json; charset=utf-8" ^
-d "{\"text\": \"%query%\"}" ^
-H "Accept: application/json; charset=utf-8" | python -c "import sys, json, codecs; response = json.load(codecs.getreader('utf-8-sig')(sys.stdin.buffer)); print(response.get('answer', 'No answer found'))"

goto chat_loop

:end
echo.
echo ¡Gracias por usar el sistema! ¡Hasta pronto!
pause 