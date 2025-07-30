"""OpenAPI 仕様書をパースするモジュール"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

logger = logging.getLogger(__name__)


class OpenAPISchema(BaseModel):
    """OpenAPI スキーマの型安全な表現"""

    model_config = ConfigDict(extra="allow")

    openapi: str
    info: dict[str, Any]
    paths: dict[str, dict[str, Any]]
    components: dict[str, Any] | None = None
    servers: list[dict[str, Any]] | None = None


class OpenAPIParseError(Exception):
    """OpenAPI パース時のエラー"""


class OpenAPIParser:
    """OpenAPI 仕様書をパースして利用可能な形に変換するクラス"""

    def __init__(self, spec_path: str | Path) -> None:
        """パーサーを初期化する

        Args:
            spec_path: OpenAPI仕様書のパス
        """
        self.spec_path = Path(spec_path)
        self.schema: OpenAPISchema | None = None

    def parse(self) -> OpenAPISchema:
        """OpenAPI 仕様書をパースする

        Returns:
            パースされたOpenAPIスキーマ

        Raises:
            OpenAPIParseError: パースに失敗した場合
        """
        if not self.spec_path.exists():
            msg = f"OpenAPI 仕様書が見つかりません: {self.spec_path}"
            raise OpenAPIParseError(msg)

        try:
            # ファイル形式を判定して読み込み
            content = self.spec_path.read_text(encoding="utf-8")

            if self.spec_path.suffix.lower() in {".yaml", ".yml"}:
                data = yaml.safe_load(content)
            elif self.spec_path.suffix.lower() == ".json":
                data = json.loads(content)
            else:
                msg = f"サポートされていないファイル形式: {self.spec_path.suffix}"
                raise OpenAPIParseError(msg)

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            msg = f"ファイルの読み込みに失敗しました: {e}"
            raise OpenAPIParseError(msg) from e

        # 基本的な検証
        if not data.get("openapi"):
            raise OpenAPIParseError("OpenAPI バージョンが指定されていません")

        if not data.get("paths"):
            raise OpenAPIParseError("paths が定義されていません")

        try:
            self.schema = OpenAPISchema(**data)
        except ValidationError as e:
            msg = f"OpenAPI スキーマの検証に失敗しました: {e}"
            raise OpenAPIParseError(msg) from e

        logger.info("OpenAPI 仕様書のパースが完了しました: %s", self.spec_path)
        return self.schema

    def get_endpoints(self) -> list[dict[str, Any]]:
        """すべてのエンドポイント情報を取得する

        Returns:
            エンドポイント情報のリスト

        Raises:
            OpenAPIParseError: スキーマがパースされていない場合
        """
        if not self.schema:
            raise OpenAPIParseError(
                "スキーマがパースされていません。parse() を先に実行してください"
            )

        endpoints: list[dict[str, Any]] = []

        for path, path_item in self.schema.paths.items():
            for method, operation in path_item.items():
                if method.lower() in {
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "head",
                    "options",
                }:
                    # operation_idを安全に生成
                    operation_id = operation.get(
                        "operationId", self._generate_operation_id(method, path)
                    )

                    endpoint = {
                        "path": path,
                        "method": method.upper(),
                        "operation_id": operation_id,
                        "summary": operation.get("summary", ""),
                        "description": operation.get("description", ""),
                        "parameters": operation.get("parameters", []),
                        "request_body": operation.get("requestBody"),
                        "responses": operation.get("responses", {}),
                        "tags": operation.get("tags", []),
                    }
                    endpoints.append(endpoint)

        return endpoints

    def get_schemas(self) -> dict[str, dict[str, Any]]:
        """スキーマ定義を取得する

        Returns:
            スキーマ定義の辞書

        Raises:
            OpenAPIParseError: スキーマがパースされていない場合
        """
        if not self.schema:
            raise OpenAPIParseError(
                "スキーマがパースされていません。parse() を先に実行してください"
            )

        if not self.schema.components:
            return {}

        return self.schema.components.get("schemas", {})

    def resolve_ref(self, ref: str) -> dict[str, Any]:
        """$ref を解決する

        Args:
            ref: 参照パス（例: #/components/schemas/User）

        Returns:
            解決されたスキーマ

        Raises:
            OpenAPIParseError: 参照の解決に失敗した場合
        """
        if not ref.startswith("#/"):
            msg = f"サポートされていない参照形式: {ref}"
            raise OpenAPIParseError(msg)

        if not self.schema:
            raise OpenAPIParseError("スキーマがパースされていません")

        # #/components/schemas/User -> ['components', 'schemas', 'User']
        path_parts = ref[2:].split("/")

        data: Any = self.schema.model_dump()
        try:
            for part in path_parts:
                data = data[part]
        except KeyError as e:
            msg = f"参照が見つかりません: {ref}"
            raise OpenAPIParseError(msg) from e

        return data

    def _generate_operation_id(self, method: str, path: str) -> str:
        """operation_idを自動生成する

        Args:
            method: HTTPメソッド
            path: エンドポイントパス

        Returns:
            生成されたoperation_id
        """
        # パスパラメータを除去してoperation_idを生成
        clean_path = path.replace("/", "_").replace("{", "").replace("}", "")
        return f"{method.lower()}{clean_path}"
