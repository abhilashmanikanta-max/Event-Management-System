Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  EVENT MANAGEMENT SYSTEM - College DBMS Project" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "[INFO] Initializing Python virtual environment..." -ForegroundColor Yellow
    py -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

Write-Host "[INFO] Launching Full-Stack Application..." -ForegroundColor Green
Write-Host "[INFO] URL: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host ""

Start-Process "http://127.0.0.1:5000"
& ".\.venv\Scripts\python.exe" run.py
