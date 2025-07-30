"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

UpdatePetResponse モデル定義
"""

from __future__ import annotations

from pydantic import BaseModel
from ..pet import Pet

class UpdatePetResponse(BaseModel):
    """ペット情報を更新 のレスポンス"""
    data: Pet  # Petオブジェクト
