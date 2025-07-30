"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

CreatePetRequest モデル定義
"""

from __future__ import annotations

from pydantic import BaseModel
from ..category import Category
from ..tag import Tag

class CreatePetRequest(BaseModel):
    """新しいペットを登録 のリクエスト"""
    name: str  # ペット名
    category: Category | None = None
    tags: list[Tag] | None = None
    status: str  # ペットのステータス
