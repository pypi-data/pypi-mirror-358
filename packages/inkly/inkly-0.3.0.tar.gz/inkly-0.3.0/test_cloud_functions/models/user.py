"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

User モデル定義
"""

from __future__ import annotations

from pydantic import BaseModel

class User(BaseModel):
    """"""
    id: int  # ユーザーID
    username: str  # ユーザー名
    email: str  # メールアドレス
    firstName: str | None = None  # 名前
    lastName: str | None = None  # 姓
    phone: str | None = None  # 電話番号
