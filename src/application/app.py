from auth.routers import auth_router
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from twitch.routers import twitch_router

from .tasks import divide

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
    pass


@app.on_event("shutdown")
async def shutdown():
    pass


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


@app.get('/task')
async def task_end():
    task = divide.delay(1, 2)
    print(task.state)
