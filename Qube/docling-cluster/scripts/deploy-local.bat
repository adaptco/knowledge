@echo off
echo [DEPLOY] Starting Docling Cluster Deployment (Local)...

:: Check for Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not found. Please install Docker Desktop.
    exit /b 1
)

:: Navigate to root directory
cd /d "%~dp0\.."

:: Create data directories if they don't exist
if not exist "data\qdrant" mkdir "data\qdrant"
if not exist "data\ledger" mkdir "data\ledger"

:: Build and launch services
echo [DEPLOY] Building and starting services with Docker Compose...
docker-compose up --build -d

echo [DEPLOY] Environment health check:
timeout /t 10 /nobreak
docker-compose ps

echo [DEPLOY] Local deployment complete. 
echo [DEPLOY] Ingest API available at http://localhost:8000
echo [DEPLOY] Vector Store available at http://localhost:6333
echo [DEPLOY] Ledger available at http://localhost:8001
