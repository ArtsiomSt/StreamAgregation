from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from auth.routers import auth_router
from config import Settings
from db import twitch_db
from twitch.routers import twitch_router

app = FastAPI()
app.include_router(twitch_router, tags=["twitch"])
app.include_router(auth_router, tags=["auth"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    settings = Settings()
    await twitch_db.connect_to_database(path=settings.mongo_url, db_name=settings.twitch_db_name)


@app.on_event("shutdown")
async def shutdown():
    await twitch_db.close_database_connection()


@app.exception_handler(Exception)
async def handle_python_exceptions(request, exc):
    """
    Exception handler that catches all Python exceptions and returns them as HTTPExceptions.
    """

    detail = str(exc)
    status_code = 500
    headers = {}
    if isinstance(exc, HTTPException):
        return
    return JSONResponse({"exception": detail}, status_code=status_code, headers=headers)


@app.get("/")
def main():
    return {"message": "success"}
