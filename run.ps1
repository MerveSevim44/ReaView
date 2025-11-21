#!/usr/bin/env powershell
# ReaView - Backend & Frontend Server Starter
# Windows PowerShell uyumlu script

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ReaView - Tum Sunuculari Baslatiyor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Backend
Write-Host "[1] Backend baslatiliyor (port 8000)..." -ForegroundColor Green
Set-Location backend
Start-Process python.exe -ArgumentList "-m uvicorn app.main:app --reload --port 8000"

Start-Sleep -Seconds 3

# Frontend
Write-Host "[2] Frontend baslatiliyor (port 8080)..." -ForegroundColor Green
Set-Location ..\frontend
Start-Process python.exe -ArgumentList "-m http.server 8080"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Sunucular baslatildi!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:8080" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Kapatmak icin Ctrl+C yasin" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Keep script running
Read-Host "Press Enter to continue..."
