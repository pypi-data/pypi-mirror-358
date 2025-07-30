"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

Tag モデル定義
"""

from __future__ import annotations

from pydantic import BaseModel

class Tag(BaseModel):
    """"""
    id: int | None = None  # タグID
    name: str | None = None  # タグ名
