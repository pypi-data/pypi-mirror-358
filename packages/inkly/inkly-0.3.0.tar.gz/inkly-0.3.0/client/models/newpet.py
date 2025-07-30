"""NewPet モデル定義"""

from __future__ import annotations

from pydantic import BaseModel
from .category import Category
from .tag import Tag


class NewPet(BaseModel):
    """"""
    name: str  # ペット名
    category: Category | None
    tags: list[Tag] | None
    status: str  # ペットのステータス
