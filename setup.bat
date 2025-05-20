@echo off
echo Setting up Spanish RAG System...

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

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

:: Install WebSocket dependencies
echo Installing WebSocket dependencies...
pip install "uvicorn[standard]" websockets

:: Pull required Ollama models
echo Pulling Ollama models...
ollama pull llama2
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