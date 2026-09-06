from pydantic import BaseModel, EmailStr


class InspectorCreate(BaseModel):
    name: str
    email: EmailStr
    password: str