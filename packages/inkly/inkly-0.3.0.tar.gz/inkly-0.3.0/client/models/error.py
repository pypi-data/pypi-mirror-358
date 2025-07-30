"""Error モデル定義"""

from __future__ import annotations

from pydantic import BaseModel


class Error(BaseModel):
    """"""
    code: int  # エラーコード
    message: str  # エラーメッセージ
