"""ビジネスロジックインターフェース"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from .schemas import *

class PetsService(ABC):
    """petsサービスのインターフェース"""
    
    @abstractmethod
    def get_pets(
        self,
        limit: int | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """ペット一覧を取得

        登録されているすべてのペットの一覧を取得します
        """
        pass
    
    @abstractmethod
    def create_pet(
        self,
        request_data: CreatepetRequest,
    ) -> dict[str, Any]:
        """新しいペットを登録

        新しいペットを店舗に登録します
        """
        pass
    
    @abstractmethod
    def get_pet_by_id(
        self,
        petId: int,
    ) -> dict[str, Any]:
        """特定のペットを取得

        ペットIDを指定して特定のペット情報を取得します
        """
        pass
    
    @abstractmethod
    def update_pet(
        self,
        petId: int,
        request_data: UpdatepetRequest,
    ) -> dict[str, Any]:
        """ペット情報を更新

        既存のペット情報を更新します
        """
        pass
    
    @abstractmethod
    def delete_pet(
        self,
        petId: int,
    ) -> dict[str, Any]:
        """ペットを削除

        指定されたペットを削除します
        """
        pass

class UsersService(ABC):
    """usersサービスのインターフェース"""
    
    @abstractmethod
    def get_users(
        self,
    ) -> dict[str, Any]:
        """ユーザー一覧を取得

        登録されているユーザーの一覧を取得します
        """
        pass
    
    @abstractmethod
    def create_user(
        self,
        request_data: CreateuserRequest,
    ) -> dict[str, Any]:
        """新しいユーザーを作成

        新しいユーザーアカウントを作成します
        """
        pass
