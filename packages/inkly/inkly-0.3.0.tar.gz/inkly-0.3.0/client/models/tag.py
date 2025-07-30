"""Tag モデル定義"""

from __future__ import annotations

from pydantic import BaseModel
from .none import None


class Tag(BaseModel):
    """"""
    id: int | None  # タグID
    name: str | None  # タグ名
