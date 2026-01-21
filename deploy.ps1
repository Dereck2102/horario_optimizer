# deploy.ps1 - Deployment Script for Windows
# Usage: ./deploy.ps1

Write-Host ">>> Iniciando Despliegue a AWS..." -ForegroundColor Cyan

# 0. Configurar Credenciales
# NOTE: It is recommended to configure AWS CLI with `aws configure` instead of hardcoding keys here.
# If you must use these variables, set them in your terminal session before running the script.
# $env:AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY"
# $env:AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_KEY"
# $env:AWS_SESSION_TOKEN = "YOUR_SESSION_TOKEN"
$env:AWS_REGION = "us-east-1"

# Hardcoded URI to avoid variable issues
$ECR_REGISTRY = "307218437237.dkr.ecr.us-east-1.amazonaws.com"
$ECR_REPO = "horarios-uce"
$FULL_IMAGE_URI = "307218437237.dkr.ecr.us-east-1.amazonaws.com/horarios-uce:latest"

# 1. Login ECR
Write-Host "[1/5] Autenticando con ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REGISTRY
if ($LASTEXITCODE -ne 0) { Write-Error "Fallo en Login ECR"; exit 1 }

# 2. Build
Write-Host "[2/5] Construyendo Imagen Docker..."
docker build -t horarios-uce .
if ($LASTEXITCODE -ne 0) { Write-Error "Fallo en Build"; exit 1 }

# 3. Tag
Write-Host "[3/5] Etiquetando Imagen..."
Write-Host "Destino: $FULL_IMAGE_URI"
docker tag horarios-uce:latest $FULL_IMAGE_URI

# 4. Push
Write-Host "[4/5] Subiendo a AWS ECR (Esto puede tardar)..."
docker push $FULL_IMAGE_URI
if ($LASTEXITCODE -ne 0) { Write-Error "Fallo en Push"; exit 1 }

# 5. Update Service
Write-Host "[5/5] Actualizando Servicio ECS (Desired Count = 1)..."
aws ecs update-service --cluster horarios-cluster --service horarios-service --force-new-deployment --desired-count 1
if ($LASTEXITCODE -ne 0) { Write-Error "Fallo al actualizar servicio"; exit 1 }

Write-Host ">>> !Despliegue Completado!" -ForegroundColor Green
Write-Host ">>> Verifica tu IP Publica en la consola de AWS ECS."
