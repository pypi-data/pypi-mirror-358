"""生成されたAPIクライアント（同期版）"""

from __future__ import annotations
from typing import Any

import httpx
from pydantic import BaseModel
from .models import *

class APIClient:
    """生成されたAPIクライアント（同期版）"""

    def __init__(self, base_url: str, headers: dict[str, str] | None = None) -> None:
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.client = httpx.Client()

    def close(self) -> None:
        """クライアントを閉じる"""
        self.client.close()
    def getpets(self, limit: int | None = None, tag: str | None = None) -> list[Pet]:
        """ペット一覧を取得

        登録されているすべてのペットの一覧を取得します
        """
        url = f"{self.base_url}/pets"

        # パスパラメータの置換

        # クエリパラメータ
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if tag is not None:
            params["tag"] = tag

        headers = {**self.headers}

        response = self.client.request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
        )

        response.raise_for_status()
        result = response.json()
        
        # レスポンスを適切なモデルにキャスト
        # 配列レスポンス (200)
        if isinstance(result, list):
            return [Pet.model_validate(item) for item in result]
        return result
    def createpet(self, data: dict[str, Any] | None = None) -> Pet:
        """新しいペットを登録

        新しいペットを店舗に登録します
        """
        url = f"{self.base_url}/pets"

        # パスパラメータの置換

        # クエリパラメータ
        params: dict[str, Any] = {}

        headers = {**self.headers}

        response = self.client.request(
            method="POST",
            url=url,
            params=params,
            headers=headers,
            json=data,
        )

        response.raise_for_status()
        result = response.json()
        
        # レスポンスを適切なモデルにキャスト
        # 単一オブジェクトレスポンス (201)
        if isinstance(result, dict):
            return Pet.model_validate(result)
        return result
    def getpetbyid(self, petId: int) -> Pet:
        """特定のペットを取得

        ペットIDを指定して特定のペット情報を取得します
        """
        url = f"{self.base_url}/pets/{petId}"

        # パスパラメータの置換
        url = url.replace("{petId}", str(petId))

        # クエリパラメータ
        params: dict[str, Any] = {}

        headers = {**self.headers}

        response = self.client.request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
        )

        response.raise_for_status()
        result = response.json()
        
        # レスポンスを適切なモデルにキャスト
        # 単一オブジェクトレスポンス (200)
        if isinstance(result, dict):
            return Pet.model_validate(result)
        return result
    def updatepet(self, petId: int, data: dict[str, Any] | None = None) -> Pet:
        """ペット情報を更新

        既存のペット情報を更新します
        """
        url = f"{self.base_url}/pets/{petId}"

        # パスパラメータの置換
        url = url.replace("{petId}", str(petId))

        # クエリパラメータ
        params: dict[str, Any] = {}

        headers = {**self.headers}

        response = self.client.request(
            method="PUT",
            url=url,
            params=params,
            headers=headers,
            json=data,
        )

        response.raise_for_status()
        result = response.json()
        
        # レスポンスを適切なモデルにキャスト
        # 単一オブジェクトレスポンス (200)
        if isinstance(result, dict):
            return Pet.model_validate(result)
        return result
    def deletepet(self, petId: int) -> dict[str, Any]:
        """ペットを削除

        指定されたペットを削除します
        """
        url = f"{self.base_url}/pets/{petId}"

        # パスパラメータの置換
        url = url.replace("{petId}", str(petId))

        # クエリパラメータ
        params: dict[str, Any] = {}

        headers = {**self.headers}

        response = self.client.request(
            method="DELETE",
            url=url,
            params=params,
            headers=headers,
        )

        response.raise_for_status()
        result = response.json()
        
        # レスポンスを適切なモデルにキャスト
        return result
    def getusers(self) -> list[User]:
        """ユーザー一覧を取得

        登録されているユーザーの一覧を取得します
        """
        url = f"{self.base_url}/users"

        # パスパラメータの置換

        # クエリパラメータ
        params: dict[str, Any] = {}

        headers = {**self.headers}

        response = self.client.request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
        )

        response.raise_for_status()
        result = response.json()
        
        # レスポンスを適切なモデルにキャスト
        # 配列レスポンス (200)
        if isinstance(result, list):
            return [User.model_validate(item) for item in result]
        return result
    def createuser(self, data: dict[str, Any] | None = None) -> User:
        """新しいユーザーを作成

        新しいユーザーアカウントを作成します
        """
        url = f"{self.base_url}/users"

        # パスパラメータの置換

        # クエリパラメータ
        params: dict[str, Any] = {}

        headers = {**self.headers}

        response = self.client.request(
            method="POST",
            url=url,
            params=params,
            headers=headers,
            json=data,
        )

        response.raise_for_status()
        result = response.json()
        
        # レスポンスを適切なモデルにキャスト
        # 単一オブジェクトレスポンス (201)
        if isinstance(result, dict):
            return User.model_validate(result)
        return result
