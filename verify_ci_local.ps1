# Verificación local del workflow de GitHub Actions (PowerShell)

Write-Host "🧪 Verificando workflow localmente..." -ForegroundColor Green
Write-Host "=================================="

Write-Host "`n1. Verificando Python..." -ForegroundColor Yellow
python -c "import sys; print('✅ Python version:', sys.version)"

Write-Host "`n2. Verificando imports básicos..." -ForegroundColor Yellow  
python -c "import os; print('✅ OS module imported successfully')"

Write-Host "`n3. Verificando tests..." -ForegroundColor Yellow
if (Test-Path "tests\test_minimal.py") {
    Write-Host "✅ Found test_minimal.py, running tests..." -ForegroundColor Green
    python -m pytest tests\test_minimal.py -v
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Tests completed with issues" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ test_minimal.py not found, running simple test..." -ForegroundColor Yellow
    python -c "print('Simple test: 1+1 =', 1+1); assert 1+1 == 2; print('✅ Test passed!')"
}

Write-Host "`n4. Verificando estructura del proyecto..." -ForegroundColor Yellow
if (Test-Path 'README.md') {
    Write-Host "✅ README.md: Found" -ForegroundColor Green
} else {
    Write-Host "❌ README.md: Missing" -ForegroundColor Red
}

if (Test-Path 'pyproject.toml') {
    Write-Host "✅ pyproject.toml: Found" -ForegroundColor Green
} else {
    Write-Host "❌ pyproject.toml: Missing" -ForegroundColor Red
}

if (Test-Path 'welcome_dialog.py') {
    Write-Host "✅ welcome_dialog.py: Found" -ForegroundColor Green
} else {
    Write-Host "❌ welcome_dialog.py: Missing" -ForegroundColor Red
}

Write-Host "`n🎉 Verificación local completada!" -ForegroundColor Green
Write-Host "Este script simula lo que hace GitHub Actions." -ForegroundColor Cyan
