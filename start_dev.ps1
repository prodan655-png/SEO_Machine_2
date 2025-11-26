Write-Host "🚀 Starting SEO Machine Development Environment..." -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "backend/main.py")) {
    Write-Host "❌ Error: Please run this script from the SEO_Machine_2 root directory" -ForegroundColor Red
    exit 1
}

# Get the current directory
$rootDir = Get-Location

# Start Backend in a new window (keeping it open)
Write-Host "🔧 Starting Backend..." -ForegroundColor Yellow
$backendCmd = 'cd /d "' + $rootDir + '\backend" & python -m uvicorn main:app --reload --port 8000'
Start-Process -FilePath "cmd.exe" -ArgumentList "/k $backendCmd"

# Wait a moment before starting frontend
Start-Sleep -Seconds 1

# Start Frontend in a new window (keeping it open)
Write-Host "🎨 Starting Frontend..." -ForegroundColor Yellow
$frontendCmd = 'cd /d "' + $rootDir + '\frontend" & python -m http.server 8080'
Start-Process -FilePath "cmd.exe" -ArgumentList "/k $frontendCmd"

Write-Host ""
Write-Host "✅ Development environment started!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 URLs:"
Write-Host "   Frontend: http://localhost:8080"
Write-Host "   Backend:  http://localhost:8000"
Write-Host "   API Docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "🛑 To stop: Close the opened terminal windows."
