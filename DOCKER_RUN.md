# Running the Docker Container

## Prerequisites
- Docker installed and running
- AWS credentials configured (for Bedrock access)
- `.env` file with required environment variables (optional, can also pass via `-e` flags)

## Build the Docker Image

```bash
docker build --platform linux/amd64 -t diagram-maker:latest .
```

Or with a specific tag:
```bash
docker build --platform linux/amd64 -t diagram-maker:v1.0.0 .
```

## Run the Container

### Basic Run (with .env file)

**Bash/Linux/Mac:**
```bash
docker run -d \
  --name diagram-maker \
  -p 8001:8001 \
  --env-file .env \
  diagram-maker:latest
```

**PowerShell (Windows):**
```powershell
docker run -d `
  --name diagram-maker `
  -p 8001:8001 `
  --env-file .env `
  diagram-maker:latest
```

**Or as a single line:**
```powershell
docker run -d --name diagram-maker -p 8001:8001 --env-file .env diagram-maker:latest
```

### Run with Environment Variables (without .env file)

**Bash/Linux/Mac:**
```bash
docker run -d \
  --name diagram-maker \
  -p 8001:8001 \
  -e AWS_ACCESS_KEY_ID=your_access_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key \
  -e AWS_DEFAULT_REGION=ap-southeast-2 \
  -e S3_BUCKET_NAME=your-bucket-name \
  diagram-maker:latest
```

**PowerShell (Windows):**
```powershell
docker run -d `
  --name diagram-maker `
  -p 8001:8001 `
  -e AWS_ACCESS_KEY_ID=your_access_key `
  -e AWS_SECRET_ACCESS_KEY=your_secret_key `
  -e AWS_DEFAULT_REGION=ap-southeast-2 `
  -e S3_BUCKET_NAME=your-bucket-name `
  diagram-maker:latest
```

**Or as a single line:**
```powershell
docker run -d --name diagram-maker -p 8001:8001 -e AWS_ACCESS_KEY_ID=your_access_key -e AWS_SECRET_ACCESS_KEY=your_secret_key -e AWS_DEFAULT_REGION=ap-southeast-2 -e S3_BUCKET_NAME=your-bucket-name diagram-maker:latest
```

### Run with Volume Mount (for persistent vector store)

**Bash/Linux/Mac:**
```bash
docker run -d \
  --name diagram-maker \
  -p 8001:8001 \
  -v $(pwd)/vector_store:/app/vector_store \
  --env-file .env \
  diagram-maker:latest
```

**PowerShell (Windows):**
```powershell
docker run -d `
  --name diagram-maker `
  -p 8001:8001 `
  -v ${PWD}/vector_store:/app/vector_store `
  --env-file .env `
  diagram-maker:latest
```

**Or as a single line:**
```powershell
docker run -d --name diagram-maker -p 8001:8001 -v ${PWD}/vector_store:/app/vector_store --env-file .env diagram-maker:latest
```

### Run in Interactive Mode (for debugging)

**Bash/Linux/Mac:**
```bash
docker run -it \
  --name diagram-maker \
  -p 8001:8001 \
  --env-file .env \
  diagram-maker:latest
```

**PowerShell (Windows):**
```powershell
docker run -it `
  --name diagram-maker `
  -p 8001:8001 `
  --env-file .env `
  diagram-maker:latest
```

**Or as a single line:**
```powershell
docker run -it --name diagram-maker -p 8001:8001 --env-file .env diagram-maker:latest
```

## Required Environment Variables

- `S3_BUCKET_NAME` (required) - S3 bucket name for document storage
- `AWS_ACCESS_KEY_ID` - AWS access key (or use IAM role)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key (or use IAM role)
- `AWS_DEFAULT_REGION` or `BEDROCK_REGION` - AWS region (default: ap-southeast-2)

Optional:
- `BEDROCK_MODEL_ID` - Bedrock model ID (default: amazon.nova-lite-v1:0)
- `BEDROCK_EMBEDDING_MODEL_ID` - Embedding model ID (default: amazon.titan-embed-text-v2:0)
- `VECTOR_STORE_PATH` - Path for vector store persistence (default: ./vector_store)

## Verify Container is Running

**Bash/Linux/Mac/PowerShell:**
```bash
# Check container status
docker ps

# Check logs
docker logs diagram-maker

# Check health endpoint (PowerShell)
Invoke-WebRequest -Uri http://localhost:8001/api/v1/health

# Check health endpoint (Bash/Linux/Mac)
curl http://localhost:8001/api/v1/health
```

## Stop and Remove Container

```bash
# Stop container
docker stop diagram-maker

# Remove container
docker rm diagram-maker

# Stop and remove in one command
docker rm -f diagram-maker
```

## Access the API

Once running, the API will be available at:
- Health check: http://localhost:8001/api/v1/health
- API docs: http://localhost:8001/docs
- OpenAPI spec: http://localhost:8001/openapi.json

