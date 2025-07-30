"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

GetPetsResponse モデル定義
"""

from __future__ import annotations

from pydantic import BaseModel
from ..pet import Pet

class GetPetsResponse(BaseModel):
    """ペット一覧を取得 のレスポンス"""
    data: list[Pet]  # Petオブジェクトの配列
