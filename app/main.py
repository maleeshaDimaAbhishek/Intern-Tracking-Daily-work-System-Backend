from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session
from app.core import auth
from app.db.database import Base, SessionLocal,engine
from app.api import user
from app.api import auth
from app.api import project
from app.api import daily_work
from app.model import user_project
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EmpDiary API",version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)
app.include_router(project.router, prefix="/projects", tags=["Projects"])
app.include_router(daily_work.router, prefix="/daily-work", tags=["Tasks"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(user.router,prefix="/users",tags=["Users"]) 
