Write-Host "Iniciando configuración del entorno..."

# Crear entorno virtual si no existe
if (-Not (Test-Path ".venv")) {
    Write-Host "Creando entorno virtual..."
    python -m venv .venv
}

# Activar entorno virtual
Write-Host "Activando entorno virtual..."
. .\.venv\Scripts\Activate.ps1

# Ruta de UV
$uvPath = "$env:USERPROFILE\AppData\Roaming\uv\bin\uv.exe"

# Instalar dependencias
if (Test-Path $uvPath) {
    Write-Host "Instalando dependencias con uv..."
    & "$uvPath" pip install -r requirements.txt
}
else {
    Write-Host "Instalando dependencias con pip..."
    pip install -r requirements.txt
}

# Instalar pre-commit
Write-Host "Instalando pre-commit..."
pip install pre-commit

# Configurar hooks de pre-commit
Write-Host "Configurando hooks..."
pre-commit install

# Ejecutar pre-commit en todos los archivos
Write-Host "Ejecutando verificación con pre-commit..."
pre-commit run -a

Write-Host ""
Write-Host "Configuración completada correctamente."
