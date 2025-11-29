@echo off
echo 🛡️ Starting Sovereign GRC Auditor...
echo -----------------------------------
echo 1. Checking for Ollama...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Ollama not found! Please install it from ollama.com
    pause
    exit
)

echo 2. Checking Model (llama3.2)...
ollama list | findstr "llama3.2" >nul
if %errorlevel% neq 0 (
    echo ⚠️ Model not found. Downloading llama3.2 (this happens only once)...
    ollama pull llama3.2
)

echo 3. Launching App...
streamlit run app.py
pause
