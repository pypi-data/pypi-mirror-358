"""pets エンドポイント（同期版）"""

from __future__ import annotations
from typing import Any

from ..client import APIClient
from ..models import *


class PetsEndpoints:
    """petsエンドポイントクラス"""

    def __init__(self, client: APIClient) -> None:
        """初期化
        
        Args:
            client: APIクライアントインスタンス
        """
        self.client = client

    def get_pets(self, limit: int | None = None, tag: str | None = None) -> Any:
        """ペット一覧を取得

        登録されているすべてのペットの一覧を取得します
        """
        response = self.client.getpets(
            limit=limit,
            tag=tag,
        )
        
        # レスポンスを適切なモデルにキャスト
        return response

    def create_pet(self, data: dict[str, Any] | None = None) -> Any:
        """新しいペットを登録

        新しいペットを店舗に登録します
        """
        response = self.client.createpet(
            data=data
        )
        
        # レスポンスを適切なモデルにキャスト
        return response

    def get_pet_by_id(self, petId: int) -> Any:
        """特定のペットを取得

        ペットIDを指定して特定のペット情報を取得します
        """
        response = self.client.getpetbyid(
            petId=petId,
        )
        
        # レスポンスを適切なモデルにキャスト
        return response

    def update_pet(self, petId: int, data: dict[str, Any] | None = None) -> Any:
        """ペット情報を更新

        既存のペット情報を更新します
        """
        response = self.client.updatepet(
            petId=petId,
            data=data
        )
        
        # レスポンスを適切なモデルにキャスト
        return response

    def delete_pet(self, petId: int) -> Any:
        """ペットを削除

        指定されたペットを削除します
        """
        response = self.client.deletepet(
            petId=petId,
        )
        
        # レスポンスを適切なモデルにキャスト
        return response
