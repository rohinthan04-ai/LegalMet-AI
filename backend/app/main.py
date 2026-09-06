from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.database import engine, get_db
from app.routers import inspectors, auth, inspections
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Legal Metrology Inspection System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

app.include_router(inspectors.router)
app.include_router(auth.router)
app.include_router(inspections.router)


@app.get("/")
def root():
    return {
        "message": "Legal Metrology Backend is running"
    }


@app.get("/db-test")
def database_test(db: Session = Depends(get_db)):
    return {
        "message": "Database session created successfully"
    }