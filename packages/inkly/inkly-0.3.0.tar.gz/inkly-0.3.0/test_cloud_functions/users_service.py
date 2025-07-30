"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

UsersService インターフェース
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict

# モデルのインポート
from .models.responses.get_users_response import GetUsersResponse
from .models.requests.create_user_request import CreateUserRequest
from .models.responses.create_user_response import CreateUserResponse

class UsersService(ABC):
    """usersサービスのインターフェース"""
    @abstractmethod
    def get_users(
        self,
    ) -> GetUsersResponse:
        """ユーザー一覧を取得

        登録されているユーザーの一覧を取得します
        
        Args:
            
        Returns:
            GetUsersResponse: レスポンスデータ
        """
        raise NotImplementedError
    @abstractmethod
    def create_user(
        self,
        request: CreateUserRequest,
    ) -> CreateUserResponse:
        """新しいユーザーを作成

        新しいユーザーアカウントを作成します
        
        Args:
            request: リクエストデータ
            
        Returns:
            CreateUserResponse: レスポンスデータ
        """
        raise NotImplementedError