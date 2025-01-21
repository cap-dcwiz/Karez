# models.py
from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

class Point(BaseModel):
    name: str = Field(..., example="chiller-01_chilledwaterreturntemperature")
    value: float = Field(..., example=3333.0)
    timestamp: str = Field(..., example="2025-02-23T15:20:30")