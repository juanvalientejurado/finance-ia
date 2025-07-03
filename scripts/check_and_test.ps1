Write-Host "🔍 Ejecutando chequeo de código y tests..."

# Código limpio
black .
isort .
flake8 .

.venv\Scripts\black.exe app tests
.venv\Scripts\isort.exe app tests
.venv\Scripts\flake8.exe app tests

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Falló el chequeo de estilo. Corrige los errores antes de continuar."
    exit 1
}

# Tests
pytest

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Fallaron los tests. Corrige los errores antes de continuar."
    exit 1
}

Write-Host "`n✅ Todo correcto. Código limpio y tests superados."
