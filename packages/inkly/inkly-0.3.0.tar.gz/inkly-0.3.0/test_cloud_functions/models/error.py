"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

Error モデル定義
"""

from __future__ import annotations

from pydantic import BaseModel

class Error(BaseModel):
    """"""
    code: int  # エラーコード
    message: str  # エラーメッセージ
