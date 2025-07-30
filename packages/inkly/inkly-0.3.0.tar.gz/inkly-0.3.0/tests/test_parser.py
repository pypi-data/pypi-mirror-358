"""OpenAPIパーサーのテスト"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import pytest
import yaml

from inkly.parser import OpenAPIParseError, OpenAPIParser


@pytest.fixture
def sample_openapi() -> dict[str, Any]:
    """サンプルOpenAPI定義"""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0", "description": "テスト用API"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "getUsers",
                    "summary": "ユーザー一覧取得",
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/User"},
                                    }
                                }
                            },
                        }
                    },
                }
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "required": ["id", "name"],
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                    },
                }
            }
        },
    }


@pytest.fixture
def temp_yaml_file(sample_openapi: dict[str, Any]) -> Path:
    """一時的なYAMLファイルを作成"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(sample_openapi, f)
        return Path(f.name)


class TestOpenAPIParser:
    """OpenAPIパーサーのテストクラス"""

    def test_parse_yaml_file(self, temp_yaml_file: Path) -> None:
        """YAML ファイルのパーステスト"""
        parser = OpenAPIParser(temp_yaml_file)
        schema = parser.parse()

        assert schema.openapi == "3.0.0"
        assert schema.info["title"] == "Test API"
        assert "/users" in schema.paths

        # 後処理
        temp_yaml_file.unlink()

    def test_get_endpoints(self, temp_yaml_file: Path) -> None:
        """エンドポイント取得テスト"""
        parser = OpenAPIParser(temp_yaml_file)
        parser.parse()

        endpoints = parser.get_endpoints()

        assert len(endpoints) == 1

        endpoint = endpoints[0]
        assert endpoint["path"] == "/users"
        assert endpoint["method"] == "GET"
        assert endpoint["operation_id"] == "getUsers"
        assert endpoint["summary"] == "ユーザー一覧取得"

        # 後処理
        temp_yaml_file.unlink()

    def test_get_schemas(self, temp_yaml_file: Path) -> None:
        """スキーマ取得テスト"""
        parser = OpenAPIParser(temp_yaml_file)
        parser.parse()

        schemas = parser.get_schemas()

        assert "User" in schemas

        user_schema = schemas["User"]
        assert user_schema["type"] == "object"
        assert set(user_schema["required"]) == {"id", "name"}
        assert "id" in user_schema["properties"]
        assert "name" in user_schema["properties"]
        assert "email" in user_schema["properties"]

        # 後処理
        temp_yaml_file.unlink()

    def test_resolve_ref(self, temp_yaml_file: Path) -> None:
        """参照解決テスト"""
        parser = OpenAPIParser(temp_yaml_file)
        parser.parse()

        resolved = parser.resolve_ref("#/components/schemas/User")

        assert resolved["type"] == "object"
        assert "id" in resolved["properties"]

        # 後処理
        temp_yaml_file.unlink()

    def test_parse_nonexistent_file(self) -> None:
        """存在しないファイルのパーステスト"""
        parser = OpenAPIParser("nonexistent.yaml")

        with pytest.raises(OpenAPIParseError, match="OpenAPI 仕様書が見つかりません"):
            parser.parse()

    def test_parse_invalid_openapi(self) -> None:
        """無効なOpenAPI定義のテスト"""
        invalid_spec = {"invalid": "spec"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(invalid_spec, f)
            temp_file = Path(f.name)

        try:
            parser = OpenAPIParser(temp_file)
            with pytest.raises(
                OpenAPIParseError, match="OpenAPI バージョンが指定されていません"
            ):
                parser.parse()
        finally:
            temp_file.unlink()

    def test_get_endpoints_without_parse(self, temp_yaml_file: Path) -> None:
        """パース前のエンドポイント取得テスト"""
        parser = OpenAPIParser(temp_yaml_file)

        with pytest.raises(OpenAPIParseError, match="スキーマがパースされていません"):
            parser.get_endpoints()

        # 後処理
        temp_yaml_file.unlink()

    def test_operation_id_generation(self) -> None:
        """operation_id 自動生成テスト"""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/users/{id}": {
                    "get": {
                        "summary": "Get user",
                        "responses": {"200": {"description": "OK"}},
                    }
                }
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(spec, f)
            temp_file = Path(f.name)

        try:
            parser = OpenAPIParser(temp_file)
            parser.parse()
            endpoints = parser.get_endpoints()

            assert len(endpoints) == 1
            assert endpoints[0]["operation_id"] == "get_users_id"
        finally:
            temp_file.unlink()
