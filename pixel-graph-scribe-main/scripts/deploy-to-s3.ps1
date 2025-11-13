# PowerShell script to build and deploy frontend to S3

$S3_BUCKET = "diagram-maker-frontend-dev"
$REGION = "ap-southeast-2"

Write-Host "Starting deployment to S3..." -ForegroundColor Cyan

# Step 1: Build the application
Write-Host "Step 1: Building application..." -ForegroundColor Yellow
& "$PSScriptRoot\build.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Build failed. Deployment aborted." -ForegroundColor Red
    exit 1
}

# Step 2: Verify dist directory exists
if (-not (Test-Path "dist")) {
    Write-Host "Error: dist directory not found. Build may have failed." -ForegroundColor Red
    exit 1
}

# Step 3: Sync to S3
Write-Host "Step 2: Syncing to S3 bucket: $S3_BUCKET" -ForegroundColor Yellow
aws s3 sync dist/ "s3://$S3_BUCKET/" --region $REGION --delete

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to sync to S3" -ForegroundColor Red
    exit 1
}

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "Frontend is now available at: http://$S3_BUCKET.s3-website-$REGION.amazonaws.com" -ForegroundColor Cyan

