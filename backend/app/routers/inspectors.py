from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.inspector import Inspector
from app.schemas.inspector import InspectorCreate
from app.core.security import hash_password
from app.core.security import verify_access_token

router = APIRouter(
    prefix="/inspectors",
    tags=["Inspectors"]
)


@router.post("/")
def create_inspector(
    inspector: InspectorCreate,
    db: Session = Depends(get_db)
):
    new_inspector = Inspector(
        name=inspector.name,
        email=inspector.email,
        password_hash=hash_password(inspector.password)
    )

    db.add(new_inspector)
    db.commit()
    db.refresh(new_inspector)

    return {
        "id": new_inspector.id,
        "name": new_inspector.name,
        "email": new_inspector.email
    }

@router.get("/me")
def get_current_inspector(
    inspector_id: int = Depends(verify_access_token)
):
    return {
        "message": "Authentication successful",
        "inspector_id": inspector_id
    }