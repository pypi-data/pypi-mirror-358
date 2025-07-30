"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

GetUsersResponse モデル定義
"""

from __future__ import annotations

from pydantic import BaseModel
from ..user import User

class GetUsersResponse(BaseModel):
    """ユーザー一覧を取得 のレスポンス"""
    data: list[User]  # Userオブジェクトの配列
