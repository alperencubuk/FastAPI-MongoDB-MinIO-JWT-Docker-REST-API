from asyncio import create_task
from os import getenv
from shutil import rmtree

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from source.app.storages.utils import create_minio_storage
from source.app.users.utils import create_admin_user
from source.core.health import minio_health, mongodb_health
from source.core.routers import api_router
from source.core.schemas import HealthModel

app = FastAPI(title=getenv("APP_TITLE"))

app.include_router(api_router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await create_admin_user()
    await create_minio_storage()


@app.get("/", response_model=HealthModel, tags=["health"])
async def health_check():
    mongodb_task = create_task(mongodb_health())
    minio_task = create_task(minio_health())
    mongodb = await mongodb_task
    minio = await minio_task
    return {"api": True, "mongodb": mongodb, "minio": minio}


@app.on_event("shutdown")
async def shutdown_event():
    rmtree(getenv("TEMP_FOLDER"), ignore_errors=True)
