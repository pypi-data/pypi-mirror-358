"""users エンドポイント（同期版）"""

from __future__ import annotations
from typing import Any

from ..client import APIClient
from ..models import *


class UsersEndpoints:
    """usersエンドポイントクラス"""

    def __init__(self, client: APIClient) -> None:
        """初期化
        
        Args:
            client: APIクライアントインスタンス
        """
        self.client = client

    def get_users(self) -> Any:
        """ユーザー一覧を取得

        登録されているユーザーの一覧を取得します
        """
        response = self.client.getusers(
        )
        
        # レスポンスを適切なモデルにキャスト
        return response

    def create_user(self, data: dict[str, Any] | None = None) -> Any:
        """新しいユーザーを作成

        新しいユーザーアカウントを作成します
        """
        response = self.client.createuser(
            data=data
        )
        
        # レスポンスを適切なモデルにキャスト
        return response
