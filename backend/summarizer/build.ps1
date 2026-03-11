# build.ps1 — empaqueta la Lambda con sus dependencias
$ErrorActionPreference = "Stop"

Write-Host "Limpiando builds anteriores..." -ForegroundColor Yellow
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue package
Remove-Item -Force -ErrorAction SilentlyContinue summarizer.zip

Write-Host "Instalando dependencias en package/..." -ForegroundColor Yellow
pip install -r requirements.txt --target ./package --quiet

Write-Host "Copiando codigo fuente..." -ForegroundColor Yellow
Copy-Item handler.py package/
Copy-Item transcript.py package/
Copy-Item bedrock_client.py package/

Write-Host "Creando ZIP..." -ForegroundColor Yellow
cd package
Compress-Archive -Path * -DestinationPath ../summarizer.zip
cd ..

Write-Host "ZIP creado: $(Get-Item summarizer.zip | Select-Object -ExpandProperty Length) bytes" -ForegroundColor Green