from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.inspector import Inspector
from app.schemas.auth import LoginRequest
from app.core.security import verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    inspector = db.query(Inspector).filter(
        Inspector.email == login_data.email
    ).first()

    if not inspector:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        login_data.password,
        inspector.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(inspector.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "inspector_id": inspector.id,
        "name": inspector.name,
        "email": inspector.email
    }