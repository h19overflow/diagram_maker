# PowerShell script to build and push Docker image to AWS ECR

$ECR_REGISTRY = "575734508049.dkr.ecr.ap-southeast-2.amazonaws.com"
$ECR_REPO = "dev-diagram-maker-ecr-repo"
$IMAGE_TAG = "latest"
$REGION = "ap-southeast-2"

# Step 1: Authenticate Docker to ECR
Write-Host "Authenticating to ECR..."
$loginPassword = aws ecr get-login-password --region $REGION
$loginPassword | docker login --username AWS --password-stdin $ECR_REGISTRY

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to authenticate to ECR" -ForegroundColor Red
    exit 1
}

# Step 2: Build the Docker image
Write-Host "Building Docker image..."
docker build -t diagram-maker:$IMAGE_TAG .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker build failed" -ForegroundColor Red
    exit 1
}

# Step 3: Tag the image for ECR
Write-Host "Tagging image for ECR..."
docker tag diagram-maker:$IMAGE_TAG "$ECR_REGISTRY/$ECR_REPO`:$IMAGE_TAG"

# Step 4: Push the image to ECR
Write-Host "Pushing image to ECR..."
docker push "$ECR_REGISTRY/$ECR_REPO`:$IMAGE_TAG"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to push image to ECR" -ForegroundColor Red
    exit 1
}

Write-Host "Success! Image pushed to $ECR_REGISTRY/$ECR_REPO`:$IMAGE_TAG" -ForegroundColor Green

