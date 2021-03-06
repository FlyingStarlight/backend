import os
import uvicorn
import sentry_sdk
from fastapi import FastAPI, Depends
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.routers.auth import auth_router
from app.api.api_v1.routers.users import users_router
from app.api.api_v1.routers.servers import servers_router
from app.api.api_v1.routers.ports import ports_router
from app.api.api_v1.routers.forward_rule import forward_rule_router
from app.core import config
from app.db.session import SessionLocal
from app.core import config
from app.core.auth import get_current_active_user
from app.tasks import celery_app


app = FastAPI(
    title=config.PROJECT_NAME, docs_url="/api/docs", openapi_url="/api"
)
origins = ["*", "localhost:3000", "192.168.1.181:8000", "https://monitor.2cn.io"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sentry_sdk.init(dsn="https://ad50b72443114ca783a4f2aa3d06fba6@o176406.ingest.sentry.io/5520928")
@app.middleware("http")
async def sentry_exception(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        if config.ENABLE_SENTRY:
            with sentry_sdk.push_scope() as scope:
                scope.set_context("request", request)
                scope.user = {
                    "ip_address": request.client.host
                }
                sentry_sdk.capture_exception(e)
        raise e


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    request.state.db.close()
    return response


@app.get("/api/v1")
async def root():
    return {"message": "Hello World"}


@app.get("/api/v1/task")
async def run_task():
    celery_app.send_task("app.tasks.traffic.traffic_runner")
    return {"message": "ok"}


# Routers
app.include_router(
    users_router,
    prefix="/api/v1",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)],
)
app.include_router(
    servers_router,
    prefix="/api/v1",
    tags=["servers"],
    dependencies=[Depends(get_current_active_user)],
)
app.include_router(
    ports_router,
    prefix="/api/v1",
    tags=["ports"],
    dependencies=[Depends(get_current_active_user)],
)
app.include_router(
    forward_rule_router,
    prefix="/api/v1",
    tags=["forward rule"],
    dependencies=[Depends(get_current_active_user)],
)
app.include_router(auth_router, prefix="/api", tags=["auth"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8888)
