# Energy Dashboard Startup Script
# Run this from PowerShell to start backend and frontend

Write-Host "⚡ Energy Dashboard Startup" -ForegroundColor Cyan
Write-Host "===========================`n" -ForegroundColor Cyan

# Navigate to backend API
Write-Host "📦 Starting Backend API..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\backend\api"

# Start backend in a new terminal
Write-Host "Opening backend server in new terminal..." -ForegroundColor Green
Start-Process pwsh -ArgumentList "-NoExit -Command python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

# Navigate to frontend
Write-Host "`n🎨 Starting Frontend..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\frontend"

Write-Host "Opening frontend dev server in new terminal..." -ForegroundColor Green
Start-Process pwsh -ArgumentList "-NoExit -Command npm run dev"

Write-Host "`n✅ Both servers starting..." -ForegroundColor Green
Write-Host "@@ Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "@@ Frontend: http://localhost:5176" -ForegroundColor Cyan
Write-Host "@@ API Docs: http://localhost:8000/docs`n" -ForegroundColor Cyan

Read-Host "Press Enter to close this window"
