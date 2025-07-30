"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

CreatePetResponse モデル定義
"""

from __future__ import annotations

from pydantic import BaseModel
from ..pet import Pet

class CreatePetResponse(BaseModel):
    """新しいペットを登録 のレスポンス"""
    data: Pet  # Petオブジェクト
