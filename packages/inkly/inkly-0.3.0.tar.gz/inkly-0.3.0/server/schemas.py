"""生成されたPydanticスキーマ"""

from __future__ import annotations

from pydantic import BaseModel
class Pet(BaseModel):
    """"""
    id: int
    name: str
    category: Category | None = None
    tags: list[Tag] | None = None
    status: str
class NewPet(BaseModel):
    """"""
    name: str
    category: Category | None = None
    tags: list[Tag] | None = None
    status: str
class Category(BaseModel):
    """"""
    id: int | None = None
    name: str | None = None
class Tag(BaseModel):
    """"""
    id: int | None = None
    name: str | None = None
class User(BaseModel):
    """"""
    id: int
    username: str
    email: str
    firstName: str | None = None
    lastName: str | None = None
    phone: str | None = None
class NewUser(BaseModel):
    """"""
    username: str
    email: str
    firstName: str | None = None
    lastName: str | None = None
    phone: str | None = None
class Error(BaseModel):
    """"""
    code: int
    message: str

# リクエストDTO
