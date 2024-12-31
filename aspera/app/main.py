import uvicorn

from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.llama.engine import init_llama_index_settings
from app.settings import get_settings
from app.routers import document


@asynccontextmanager
async def lifespan(api_app: FastAPI):
    settings = get_settings()
    await init_llama_index_settings(settings)
    yield


app = FastAPI()

api_router = APIRouter()
api_router.include_router(document.router)
app.include_router(api_router, prefix="/api")

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello, Aspera!"}


def main():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
