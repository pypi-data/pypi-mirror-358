"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

NewPet モデル定義
"""

from __future__ import annotations

from pydantic import BaseModel
from .category import Category
from .tag import Tag

class NewPet(BaseModel):
    """"""
    name: str  # ペット名
    category: Category | None = None
    tags: list[Tag] | None = None
    status: str  # ペットのステータス
