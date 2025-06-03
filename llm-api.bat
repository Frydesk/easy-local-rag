@echo off
setlocal enabledelayedexpansion

echo Starting Spanish RAG System...

:: Set UV_LINK_MODE to copy to avoid hardlinking issues
set UV_LINK_MODE=copy

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Load environment variables from .env file
echo Loading environment variables...
python -c "from dotenv import load_dotenv; load_dotenv()"
if errorlevel 1 (
    echo Error: Failed to load environment variables
    pause
    exit /b 1
)

:: Check if Ollama is already running
echo Checking Ollama status...
netstat -ano | findstr :11434 >nul
if errorlevel 1 (
    echo Starting Ollama...
    start /B ollama serve
    :: Wait for Ollama to start
    timeout /t 5
) else (
    echo Ollama is already running...
)

:: Pre-load models for faster inference
echo Pre-loading models...

:: Check and load mistral model
echo Checking mistral model...
ollama show mistral >nul 2>&1
if errorlevel 1 (
    echo Loading mistral model...
    ollama pull mistral
    if errorlevel 1 (
        echo Error: Failed to load mistral model
        pause
        exit /b 1
    )
) else (
    echo mistral model is already loaded
)

:: Check and load embedding model
echo Checking mxbai-embed-large model...
ollama show mxbai-embed-large >nul 2>&1
if errorlevel 1 (
    echo Loading mxbai-embed-large model...
    ollama pull mxbai-embed-large
    if errorlevel 1 (
        echo Error: Failed to load mxbai-embed-large model
        pause
        exit /b 1
    )
) else (
    echo mxbai-embed-large model is already loaded
)

:: Process knowledge base
echo Processing knowledge base...
python process_knowledge.py
if errorlevel 1 (
    echo Error: Failed to process knowledge base
    pause
    exit /b 1
)

:: Start the API
echo Starting RAG API...
python rag_api.py
if errorlevel 1 (
    echo Error: Failed to start RAG API
    pause
    exit /b 1
)

pause