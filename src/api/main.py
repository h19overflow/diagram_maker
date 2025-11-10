from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from src.configs import APIConfig
import uvicorn
from src.api.uploads.upload_request import router as upload_router
from src.api.chat.chat_request import router as chat_router
from src.api.diagrams.diagram_request import router as diagram_router

configs = APIConfig()
origins = configs.API_CORS_ORIGINS

app = FastAPI(
    title="Pixel Art API", description="API for the Pixel Art system"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/v1/config")
async def get_config():
    return {"config": configs.model_dump()}


app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(diagram_router)

if __name__ == "__main__":
    uvicorn.run(app, host=configs.API_HOST, port=configs.API_PORT)
