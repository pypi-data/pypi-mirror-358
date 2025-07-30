"""クライアントコードジェネレータ"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .base import CodeGenerator
from .templates import (
    CLIENT_ASYNC_TEMPLATE,
    CLIENT_SYNC_TEMPLATE,
    ENDPOINT_ASYNC_TEMPLATE,
    ENDPOINT_SYNC_TEMPLATE,
    MODEL_TEMPLATE,
    MOCK_SERVER_TEMPLATE,
)

logger = logging.getLogger(__name__)

# テンプレート定義
MODELS_INIT_TEMPLATE = '''"""モデル関連のパッケージ初期化ファイル"""

{%- for model in models %}
from .{{ model.name | lower }} import {{ model.name }}
{%- endfor %}

__all__ = [
{%- for model in models %}
    "{{ model.name }}",
{%- endfor %}
]
'''

INIT_TEMPLATE = '''"""生成されたAPIクライアント"""

from .client import APIClient

__all__ = ["APIClient"]
'''


class ClientGenerator(CodeGenerator):
    """クライアントコードジェネレータ"""

    def get_templates(self, use_async: bool = False) -> dict[str, str]:
        """クライアント生成用テンプレートを返す

        Args:
            use_async: 非同期クライアントかどうか

        Returns:
            テンプレート辞書
        """
        if use_async:
            return {
                "client.py": CLIENT_ASYNC_TEMPLATE,
                "model.py": MODEL_TEMPLATE,
                "models_init.py": MODELS_INIT_TEMPLATE,
                "__init__.py": INIT_TEMPLATE,
                "endpoint.py": ENDPOINT_ASYNC_TEMPLATE,
                "mock_server.py": MOCK_SERVER_TEMPLATE,
            }
        else:
            return {
                "client.py": CLIENT_SYNC_TEMPLATE,
                "model.py": MODEL_TEMPLATE,
                "models_init.py": MODELS_INIT_TEMPLATE,
                "__init__.py": INIT_TEMPLATE,
                "endpoint.py": ENDPOINT_SYNC_TEMPLATE,
                "mock_server.py": MOCK_SERVER_TEMPLATE,
            }

    def generate_to_path(
        self,
        output_path: str | Path,
        use_async: bool = False,
        flat_structure: bool = False,
        mock_server: bool = False,
        **kwargs: Any,
    ) -> None:
        """クライアントコードを生成する

        Args:
            output_path: 出力パス
            use_async: 非同期クライアントを生成するかどうか
            flat_structure: フラット構造にするかどうか
            mock_server: モックサーバーも生成するかどうか
            **kwargs: その他のオプション
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # エンドポイント情報を抽出
            endpoints = self.parser.get_endpoints()
            logger.info(f"抽出されたエンドポイント数: {len(endpoints)}")

            # モデル情報を抽出
            schemas = self.parser.get_schemas()
            models = self._generate_models(schemas)

            if flat_structure:
                self._generate_flat_client(output_dir, endpoints, models, use_async)
            else:
                self._generate_structured_client(
                    output_dir, endpoints, models, use_async
                )

            # Mock serverも生成する場合
            if mock_server:
                self._generate_mock_server(output_dir, endpoints, models, use_async)

            logger.info(f"クライアントコードを生成しました: {output_dir}")

        except Exception as e:
            logger.error(f"クライアントコード生成中にエラーが発生しました: {e}")
            raise

    def _generate_models(
        self, schemas: dict[str, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """スキーマからモデルを生成する

        Args:
            schemas: OpenAPIスキーマ辞書

        Returns:
            モデル情報のリスト
        """
        models: list[dict[str, Any]] = []
        for schema_name, schema_data in schemas.items():
            if schema_data.get("type") == "object":
                properties = schema_data.get("properties", {})
                required = schema_data.get("required", [])

                fields: list[dict[str, str]] = []
                for field_name, field_schema in properties.items():
                    field_type = self.python_type_from_openapi(field_schema)
                    if field_name not in required:
                        field_type = f"{field_type} | None = None"

                    fields.append(
                        {
                            "name": field_name,
                            "type": field_type,
                            "description": field_schema.get("description", ""),
                        }
                    )

                models.append(
                    {
                        "name": schema_name,
                        "description": schema_data.get(
                            "description", f"{schema_name}モデル"
                        ),
                        "fields": fields,
                    }
                )

        return models

    def _generate_flat_client(
        self,
        output_dir: Path,
        endpoints: list[dict[str, Any]],
        models: list[dict[str, Any]],
        use_async: bool,
    ) -> None:
        """フラット構造のクライアントを生成する"""
        # 単一ファイルクライアント生成
        client_template = self.env.get_template("client.py")
        client_code = client_template.render(
            endpoints=endpoints,
            models=models,
            flat_structure=True,
        )

        (output_dir / "client.py").write_text(client_code, encoding="utf-8")

    def _generate_structured_client(
        self,
        output_dir: Path,
        endpoints: list[dict[str, Any]],
        models: list[dict[str, Any]],
        use_async: bool,
    ) -> None:
        """構造化されたクライアントを生成する"""
        # メインクライアントファイル
        client_template = self.env.get_template("client.py")
        client_code = client_template.render(
            endpoints=endpoints,
            models=models,
            flat_structure=False,
        )

        (output_dir / "client.py").write_text(client_code, encoding="utf-8")

        # __init__.py
        init_template = self.env.get_template("__init__.py")
        init_code = init_template.render()

        (output_dir / "__init__.py").write_text(init_code, encoding="utf-8")

        # モデルディレクトリとファイル
        models_dir = output_dir / "models"
        models_dir.mkdir(exist_ok=True)

        # 各モデルファイルを生成
        model_template = self.env.get_template("model.py")
        for model in models:
            model_code = model_template.render(model=model)
            model_file = models_dir / f"{model['name'].lower()}.py"
            model_file.write_text(model_code, encoding="utf-8")

        # models/__init__.py
        models_init_template = self.env.get_template("models_init.py")
        models_init_code = models_init_template.render(models=models)
        (models_dir / "__init__.py").write_text(models_init_code, encoding="utf-8")

        # タグごとのエンドポイントファイル生成
        endpoints_by_tag: dict[str, list[dict[str, Any]]] = {}
        for endpoint in endpoints:
            for tag in endpoint.get("tags", ["default"]):
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)

        endpoints_dir = output_dir / "endpoints"
        endpoints_dir.mkdir(exist_ok=True)

        endpoint_template = self.env.get_template("endpoint.py")
        for tag, tag_endpoints in endpoints_by_tag.items():
            endpoint_code = endpoint_template.render(
                tag=tag,
                endpoints=tag_endpoints,
            )
            endpoint_file = endpoints_dir / f"{tag.lower()}.py"
            endpoint_file.write_text(endpoint_code, encoding="utf-8")

    def _generate_mock_server(
        self,
        output_dir: Path,
        endpoints: list[dict[str, Any]],
        models: list[dict[str, Any]],
        use_async: bool,
    ) -> None:
        """モックサーバーを生成する"""
        mock_dir = output_dir / "mock_server"
        mock_dir.mkdir(exist_ok=True)

        # Mock server本体
        mock_template = self.env.get_template("mock_server.py")
        mock_code = mock_template.render(
            endpoints=endpoints,
            models=models,
            version="1.0.0",
        )
        (mock_dir / "server.py").write_text(mock_code, encoding="utf-8")

        # 起動スクリプト
        run_script = '''"""Mock Server 起動スクリプト"""

from .server import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
'''
        (mock_dir / "run.py").write_text(run_script, encoding="utf-8")

        # requirements.txt
        requirements = """flask>=2.3.0
flask-cors>=4.0.0
"""
        (mock_dir / "requirements.txt").write_text(requirements, encoding="utf-8")

        # __init__.py
        (mock_dir / "__init__.py").write_text(
            '"""Mock Server Package"""', encoding="utf-8"
        )
