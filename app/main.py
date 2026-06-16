from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.db.database import Base, engine
from app.api import user, auth, project, daily_work
from app.api import leave_request
from app.api import leave_approval
from app.api import notification
from app.api import medical_certificate
from app.api import audit_log                        # ← Step 8

# Import ALL models so SQLAlchemy creates tables
from app.model import user_project
from app.model import leave_request   as lr_model
from app.model import leave_approval  as la_model
from app.model import medical_certificate as mc_model
from app.model import notification    as notif_model
from app.model import audit_log       as al_model    # ← Step 8

from app.core.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(title="EmpDiary API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Routers ────────────────────────────────────────────────────
app.include_router(auth.router,               prefix="/auth",          tags=["Auth"])
app.include_router(user.router,               prefix="/users",         tags=["Users"])
app.include_router(project.router,            prefix="/projects",      tags=["Projects"])
app.include_router(daily_work.router,         prefix="/daily-work",    tags=["Tasks"])
app.include_router(leave_request.router,      prefix="/leave",         tags=["Leave"])
app.include_router(leave_approval.router,     prefix="/leave",         tags=["Leave Approval"])
app.include_router(medical_certificate.router, prefix="/leave",        tags=["Medical"])
app.include_router(notification.router,       prefix="/notifications", tags=["Notifications"])
app.include_router(audit_log.router,          prefix="/audit",         tags=["Audit"])