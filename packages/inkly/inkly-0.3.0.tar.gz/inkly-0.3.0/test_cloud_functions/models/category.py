"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

Category モデル定義
"""

from __future__ import annotations

from pydantic import BaseModel

class Category(BaseModel):
    """"""
    id: int | None = None  # カテゴリID
    name: str | None = None  # カテゴリ名
