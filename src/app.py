from fastapi import FastAPI
from src.dashboard import dashboard_router
from src.auth import auth_router
from src.schedule import schedule_router

app = FastAPI()

app.include_router(dashboard_router)
app.include_router(auth_router)
app.include_router(schedule_router)