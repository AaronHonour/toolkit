@echo off
REM Build Docker services in batches to avoid overwhelming Docker Desktop

echo Building Unistax services in batches...
echo =========================================
echo.

echo [Batch 1/5] Building infrastructure services...
docker compose build postgres redis zookeeper kafka loki prometheus jaeger timescale
if %errorlevel% neq 0 goto :error

echo.
echo [Batch 2/5] Building apps 01-05...
docker compose build app01 app02 app03 app04 app05
if %errorlevel% neq 0 goto :error

echo.
echo [Batch 3/5] Building apps 06-10...
docker compose build app06 app07 app08 app09 app10
if %errorlevel% neq 0 goto :error

echo.
echo [Batch 4/5] Building apps 11-15...
docker compose build app11 app12 app13 app14 app15
if %errorlevel% neq 0 goto :error

echo.
echo [Batch 5/5] Building apps 16-19 and frontend...
docker compose build app16 app17 app18 app19 frontend
if %errorlevel% neq 0 goto :error

echo.
echo =========================================
echo All services built successfully!
echo =========================================
echo.
echo To start services:
echo   docker compose up -d
echo.
echo To run tests:
echo   docker compose exec app01 pytest -v
echo.
goto :end

:error
echo.
echo ERROR: Build failed!
exit /b 1

:end
