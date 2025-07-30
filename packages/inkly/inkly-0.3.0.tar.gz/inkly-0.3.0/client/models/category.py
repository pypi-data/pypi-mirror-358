"""Category モデル定義"""

from __future__ import annotations

from pydantic import BaseModel


class Category(BaseModel):
    """"""
    id: int | None  # カテゴリID
    name: str | None  # カテゴリ名
