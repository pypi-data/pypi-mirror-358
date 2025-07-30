"""モックサーバ機能"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .parser import OpenAPIParser

logger = logging.getLogger(__name__)


class MockServerError(Exception):
    """モックサーバ関連のエラー"""


class MockServer:
    """OpenAPI定義からモックサーバを生成するクラス"""

    def __init__(self, parser: OpenAPIParser, enable_mock: bool = True) -> None:
        """モックサーバを初期化する

        Args:
            parser: OpenAPIパーサーインスタンス
            enable_mock: モックレスポンスを有効にするか
        """
        self.parser = parser
        self.enable_mock = enable_mock

        if not self.parser.schema:
            try:
                self.parser.parse()
            except Exception as e:
                msg = f"OpenAPI仕様書のパースに失敗しました: {e}"
                raise MockServerError(msg) from e

    def create_app(self) -> FastAPI:
        """FastAPIアプリケーションを作成する

        Returns:
            設定済みのFastAPIアプリケーション

        Raises:
            MockServerError: アプリケーション作成に失敗した場合
        """
        if not self.parser.schema:
            raise MockServerError("OpenAPIスキーマがロードされていません")

        # アプリケーション情報を取得
        info = self.parser.schema.info

        app = FastAPI(
            title=info.get("title", "Generated Mock API"),
            description=info.get("description", "OpenAPI仕様書から生成されたモックAPI"),
            version=info.get("version", "1.0.0"),
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
        )

        # CORS設定
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        try:
            # エンドポイントを動的に追加
            self._add_endpoints(app)

            # ヘルスチェックエンドポイント
            @app.get("/health")
            def health_check() -> dict[str, str]:
                """ヘルスチェックエンドポイント"""
                return {"status": "healthy", "server": "inkly-mock"}

            # 情報エンドポイント
            @app.get("/info")
            def server_info() -> dict[str, Any]:
                """サーバ情報エンドポイント"""
                return {
                    "title": info.get("title", "Unknown"),
                    "version": info.get("version", "1.0.0"),
                    "mock_enabled": self.enable_mock,
                    "endpoints_count": len(self.parser.get_endpoints()),
                }

            logger.info("モックサーバアプリケーションの作成が完了しました")
            return app

        except Exception as e:
            msg = f"FastAPIアプリケーションの作成に失敗しました: {e}"
            raise MockServerError(msg) from e

    def _add_endpoints(self, app: FastAPI) -> None:
        """エンドポイントを動的に追加する

        Args:
            app: FastAPIアプリケーションインスタンス

        Raises:
            MockServerError: エンドポイント追加に失敗した場合
        """
        try:
            endpoints = self.parser.get_endpoints()

            for endpoint in endpoints:
                path = endpoint["path"]
                method = endpoint["method"].lower()
                operation_id = endpoint["operation_id"]
                summary = endpoint.get("summary", "")
                description = endpoint.get("description", "")

                # パスパラメータを抽出
                path_params = self._extract_path_params(path)

                # レスポンス例を生成
                mock_response = self._generate_mock_response(endpoint)

                # 動的にハンドラ関数を作成
                handler = self._create_handler(
                    operation_id, summary, description, mock_response, path_params
                )

                # エンドポイントをアプリに追加
                app.add_api_route(
                    path=path,
                    endpoint=handler,
                    methods=[method.upper()],
                    summary=summary,
                    description=description,
                    name=operation_id,
                )

                logger.debug(
                    "エンドポイントを追加しました: %s %s", method.upper(), path
                )

            logger.info(
                "すべてのエンドポイントの追加が完了しました: %d個", len(endpoints)
            )

        except Exception as e:
            msg = f"エンドポイントの追加に失敗しました: {e}"
            raise MockServerError(msg) from e

    def _extract_path_params(self, path: str) -> list[str]:
        """パスからパラメータ名を抽出する

        Args:
            path: OpenAPIパス（例: /users/{user_id}/posts/{post_id}）

        Returns:
            パラメータ名のリスト
        """
        import re

        return re.findall(r"\{([^}]+)\}", path)

    def _generate_mock_response(self, endpoint: dict[str, Any]) -> dict[str, Any]:
        """エンドポイントのモックレスポンスを生成する

        Args:
            endpoint: エンドポイント情報

        Returns:
            モックレスポンス辞書
        """
        if not self.enable_mock:
            return {"message": "モックレスポンスは無効です"}

        responses = endpoint.get("responses", {})

        # 200番台のレスポンスを優先的に探す
        for status_code in sorted(responses.keys()):
            if str(status_code).startswith("2"):
                response = responses[status_code]
                content = response.get("content", {})

                # application/json のレスポンスがあれば使用
                if "application/json" in content:
                    json_content = content["application/json"]

                    # example があれば使用
                    if "example" in json_content:
                        return json_content["example"]

                    # schema からサンプルを生成
                    if "schema" in json_content:
                        return self._generate_sample_from_schema(json_content["schema"])

        # デフォルトレスポンス
        method = endpoint.get("method", "GET").upper()
        default_responses: dict[str, dict[str, Any]] = {
            "POST": {"message": "Created successfully", "id": 1},
            "PUT": {"message": "Updated successfully"},
            "DELETE": {"message": "Deleted successfully"},
        }
        return default_responses.get(method, {"message": "Success", "data": []})

    def _generate_sample_from_schema(self, schema: dict[str, Any]) -> Any:
        """スキーマからサンプルデータを生成する

        Args:
            schema: OpenAPIスキーマ

        Returns:
            生成されたサンプルデータ
        """
        if "$ref" in schema:
            # 参照の場合は簡易的なレスポンス
            return {"id": 1, "name": "sample"}

        schema_type = schema.get("type", "object")

        match schema_type:
            case "string":
                return schema.get("example", "sample string")
            case "integer":
                return schema.get("example", 42)
            case "number":
                return schema.get("example", 3.14)
            case "boolean":
                return schema.get("example", True)
            case "array":
                items = schema.get("items", {})
                sample_item = self._generate_sample_from_schema(items)
                return [sample_item]
            case "object":
                properties = schema.get("properties", {})
                result = {}
                for prop_name, prop_schema in properties.items():
                    result[prop_name] = self._generate_sample_from_schema(prop_schema)
                return result
            case _:
                return None

    def _create_handler(
        self,
        operation_id: str,
        summary: str,
        description: str,
        mock_response: dict[str, Any],
        path_params: list[str],
    ) -> Any:
        """エンドポイントハンドラ関数を動的に作成する

        Args:
            operation_id: オペレーションID
            summary: エンドポイントの概要
            description: エンドポイントの説明
            mock_response: モックレスポンス
            path_params: パスパラメータのリスト

        Returns:
            ハンドラ関数
        """

        def handler(**kwargs: Any) -> JSONResponse:
            """動的に生成されたエンドポイントハンドラ"""
            try:
                # パスパラメータをログに記録
                if path_params and kwargs:
                    logger.debug("パスパラメータ受信: %s", kwargs)

                # モックレスポンスを返す
                return JSONResponse(content=mock_response)

            except Exception as e:
                logger.error("ハンドラでエラーが発生しました: %s", e, exc_info=True)
                raise HTTPException(status_code=500, detail=f"内部サーバエラー: {e}")

        # 関数のメタデータを設定
        handler.__name__ = operation_id
        handler.__doc__ = f"{summary}\n\n{description}" if description else summary

        return handler
