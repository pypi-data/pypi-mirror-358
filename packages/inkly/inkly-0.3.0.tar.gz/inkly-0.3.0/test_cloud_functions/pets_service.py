"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

PetsService インターフェース
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict

# モデルのインポート
from .models.responses.get_pets_response import GetPetsResponse
from .models.requests.create_pet_request import CreatePetRequest
from .models.responses.create_pet_response import CreatePetResponse
from .models.responses.get_pet_by_id_response import GetPetByIdResponse
from .models.requests.update_pet_request import UpdatePetRequest
from .models.responses.update_pet_response import UpdatePetResponse
from .models.responses.delete_pet_response import DeletePetResponse

class PetsService(ABC):
    """petsサービスのインターフェース"""
    @abstractmethod
    def get_pets(
        self,
        limit: int | None = None,
        tag: str | None = None,
    ) -> GetPetsResponse:
        """ペット一覧を取得

        登録されているすべてのペットの一覧を取得します
        
        Args:
            limit: 取得件数の上限
            tag: フィルタリング用のタグ
            
        Returns:
            GetPetsResponse: レスポンスデータ
        """
        raise NotImplementedError
    @abstractmethod
    def create_pet(
        self,
        request: CreatePetRequest,
    ) -> CreatePetResponse:
        """新しいペットを登録

        新しいペットを店舗に登録します
        
        Args:
            request: リクエストデータ
            
        Returns:
            CreatePetResponse: レスポンスデータ
        """
        raise NotImplementedError
    @abstractmethod
    def get_pet_by_id(
        self,
        petId: int,
    ) -> GetPetByIdResponse:
        """特定のペットを取得

        ペットIDを指定して特定のペット情報を取得します
        
        Args:
            petId: ペットID
            
        Returns:
            GetPetByIdResponse: レスポンスデータ
        """
        raise NotImplementedError
    @abstractmethod
    def update_pet(
        self,
        petId: int,
        request: UpdatePetRequest,
    ) -> UpdatePetResponse:
        """ペット情報を更新

        既存のペット情報を更新します
        
        Args:
            petId: ペットID
            request: リクエストデータ
            
        Returns:
            UpdatePetResponse: レスポンスデータ
        """
        raise NotImplementedError
    @abstractmethod
    def delete_pet(
        self,
        petId: int,
    ) -> DeletePetResponse:
        """ペットを削除

        指定されたペットを削除します
        
        Args:
            petId: ペットID
            
        Returns:
            DeletePetResponse: レスポンスデータ
        """
        raise NotImplementedError