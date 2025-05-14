@echo off
echo Starting Spanish RAG System...

:: Load environment variables from .env file
echo Loading environment variables...
python -c "from dotenv import load_dotenv; load_dotenv()"

:: Activate virtual environment
call venv\Scripts\activate

:: Check if Ollama is already running
netstat -ano | findstr :11434 > nul
if errorlevel 1 (
    echo Starting Ollama...
    start /B ollama serve
    :: Wait for Ollama to start
    timeout /t 5
) else (
    echo Ollama is already running...
)

:: Process knowledge base
echo Processing knowledge base...
python process_knowledge.py

:: Start the API
echo Starting RAG API...
python rag_api.py 
pause