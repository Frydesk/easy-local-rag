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

:: Load model configuration and set variables
echo Loading model configuration...
for /f "tokens=*" %%a in ('python -c "import yaml; config = yaml.safe_load(open('config.yaml')); print(config['ollama_model'])"') do set LLM_MODEL=%%a
for /f "tokens=*" %%a in ('python -c "import yaml; config = yaml.safe_load(open('config.yaml')); print(config['model']['embedding_model'])"') do set EMBEDDING_MODEL=%%a

echo LLM Model: !LLM_MODEL!
echo Embedding Model: !EMBEDDING_MODEL!

:: Check if Ollama is already running
echo Checking Ollama status...
netstat -ano | findstr :11434 >nul
if errorlevel 1 (
    echo Starting Ollama...
    start /B ollama serve >nul 2>&1
    
    :: Wait for Ollama to start with a more informative message
    echo Waiting for Ollama to start...
    set /a attempts=0
    :wait_loop
    timeout /t 1 /nobreak >nul
    netstat -ano | findstr :11434 >nul
    if errorlevel 1 (
        set /a attempts+=1
        if !attempts! lss 10 (
            echo Still waiting for Ollama to start... Attempt !attempts! of 10
            goto wait_loop
        ) else (
            echo Error: Ollama failed to start after 20 seconds
            pause
            exit /b 1
        )
    ) else (
        echo Ollama started successfully!
    )
) else (
    echo Ollama is already running...
)

:: Pre-load models for faster inference
echo Pre-loading models...

:: Check and load LLM model
echo Checking LLM model...
ollama show !LLM_MODEL! >nul 2>&1
if errorlevel 1 (
    echo Loading !LLM_MODEL! model...
    ollama pull !LLM_MODEL!
    if errorlevel 1 (
        echo Error: Failed to load !LLM_MODEL! model
        pause
        exit /b 1
    )
) else (
    echo !LLM_MODEL! model is already loaded
)

:: Check and load embedding model
echo Checking embedding model...
ollama show !EMBEDDING_MODEL! >nul 2>&1
if errorlevel 1 (
    echo Loading !EMBEDDING_MODEL! model...
    ollama pull !EMBEDDING_MODEL!
    if errorlevel 1 (
        echo Error: Failed to load !EMBEDDING_MODEL! model
        pause
        exit /b 1
    )
) else (
    echo !EMBEDDING_MODEL! model is already loaded
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