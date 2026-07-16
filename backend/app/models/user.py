from datetime import datetime, timezone

from beanie import Document, Indexed
from pydantic import EmailStr
from typing import Annotated


class User(Document):
    name: str
    email: Annotated[EmailStr, Indexed(unique=True)]
    hashed_password: str
    created_at: datetime = datetime.now(timezone.utc)

    class Settings:
        name = "users"
