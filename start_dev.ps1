Write-Host "🚀 Starting SEO Machine Development Environment..." -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "backend/main.py")) {
    Write-Host "❌ Error: Please run this script from the SEO_Machine_2 root directory" -ForegroundColor Red
    exit 1
}

# Start Backend in a new window (keeping it open)
Write-Host "🔧 Starting Backend..." -ForegroundColor Yellow
Start-Process -FilePath "cmd.exe" -ArgumentList '/k cd backend & python -m uvicorn main:app --reload --port 8000'

# Start Frontend in a new window (keeping it open)
Write-Host "🎨 Starting Frontend..." -ForegroundColor Yellow
Start-Process -FilePath "cmd.exe" -ArgumentList '/k cd frontend & python -m http.server 8080'

Write-Host ""
Write-Host "✅ Development environment started!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 URLs:"
Write-Host "   Frontend: http://localhost:8080"
Write-Host "   Backend:  http://localhost:8000"
Write-Host "   API Docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "🛑 To stop: Close the opened terminal windows."
