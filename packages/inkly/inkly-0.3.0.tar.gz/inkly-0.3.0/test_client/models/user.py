"""User モデル定義"""

from __future__ import annotations

from pydantic import BaseModel
from . import 


class User(BaseModel):
    """"""
    id: int  # ユーザーID
    username: str  # ユーザー名
    email: str  # メールアドレス
    firstName: str | None  # 名前
    lastName: str | None  # 姓
    phone: str | None  # 電話番号
