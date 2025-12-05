@echo off
title ReaView - Backend & Frontend Server

echo.
echo ========================================
echo   ReaView - Tum Sunuculari Baslatiyor
echo ========================================
echo.

REM Backend
echo [1] Backend baslatiliyor (port 8000)...
cd backend
start "" python -m uvicorn app.main:app --reload --port 8000

timeout /t 3

REM Frontend
echo [2] Frontend baslatiliyor (port 8080)...
cd ..\frontend
start "" python -m http.server 8080

echo.
echo ========================================
echo   Sunucular baslatildi!
echo ========================================
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:8080
echo.
echo   Kapatmak icin pencereyi kapayin
echo ========================================
echo.



pause