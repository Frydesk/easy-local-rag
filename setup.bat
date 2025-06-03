@echo off
echo Setting up Spanish RAG System...

:: Set UV_LINK_MODE to copy to avoid hardlinking issues
set UV_LINK_MODE=copy

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

:: Check if Ollama is installed
ollama --version >nul 2>&1
if errorlevel 1 (
    echo Ollama is not installed! Please install Ollama from https://ollama.com/download
    pause
    exit /b 1
)

:: Check if uv is installed, if not install it
uv --version >nul 2>&1
if errorlevel 1 (
    echo Installing uv...
    pip install uv
)

:: Create and activate virtual environment using uv
echo Creating virtual environment with uv...
uv venv

:: Activate virtual environment
call .venv\Scripts\activate

:: Install requirements using uv
echo Installing requirements...
uv pip install -r requirements.txt

:: Install additional dependencies
echo Installing additional dependencies...
uv pip install "uvicorn[standard]" websockets python-dotenv

:: Pull required Ollama models
echo Pulling Ollama models...
ollama pull mxbai-embed-large

:: Create knowledge directory if it doesn't exist
if not exist knowledge (
    echo Creating knowledge directory...
    mkdir knowledge
)

:: Create text directory if it doesn't exist
if not exist text (
    echo Creating text directory...
    mkdir text
)

:: Check if vault.txt exists, if not create it
if not exist vault.txt (
    echo Creating vault.txt...
    echo. > vault.txt
)

echo.
echo Setup complete! You can now:
echo 1. Place your documents in the 'knowledge' folder
echo 2. Run 'start_rag.bat' to start the system
echo 3. Run 'test_rag.bat' to test the system
echo.
pause 