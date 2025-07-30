"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

CreateUserRequest モデル定義
"""

from __future__ import annotations

from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    """新しいユーザーを作成 のリクエスト"""
    username: str  # ユーザー名
    email: str  # メールアドレス
    firstName: str | None = None  # 名前
    lastName: str | None = None  # 姓
    phone: str | None = None  # 電話番号
