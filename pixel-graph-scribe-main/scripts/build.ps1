# PowerShell script to build the frontend application

Write-Host "Building frontend application..." -ForegroundColor Cyan

# Step 1: Install dependencies if node_modules doesn't exist
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Step 2: Run the build
Write-Host "Running npm run build..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Build failed" -ForegroundColor Red
    exit 1
}

# Step 3: Copy index.html to 404.html for S3 static website hosting
Write-Host "Creating 404.html for S3 static website hosting..." -ForegroundColor Yellow
if (Test-Path "dist/index.html") {
    Copy-Item -Path "dist/index.html" -Destination "dist/404.html" -Force
    Write-Host "Successfully created 404.html" -ForegroundColor Green
} else {
    Write-Host "Warning: dist/index.html not found" -ForegroundColor Yellow
}

Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "Output directory: dist/" -ForegroundColor Cyan

