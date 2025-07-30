"""コードジェネレータモジュール"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from jinja2 import DictLoader, Environment

from .parser import OpenAPIParser

logger = logging.getLogger(__name__)


class CodeGenerationError(Exception):
    """コード生成時のエラー"""


class CodeGenerator:
    """ベースコードジェネレータクラス"""

    def __init__(self, parser: OpenAPIParser) -> None:
        """コードジェネレータを初期化する

        Args:
            parser: OpenAPIパーサーインスタンス
        """
        self.parser = parser
        self.env = Environment(loader=DictLoader(self.get_templates()))

        # カスタムフィルターを追加
        def _python_type_filter(value: Any) -> str:
            return self.python_type_from_openapi(value)

        def _lower_filter(value: Any) -> str:
            return str(value).lower()

        def _replace_filter(value: Any, old: Any, new: Any) -> str:
            return str(value).replace(str(old), str(new))

        def _camel_to_snake_filter(value: Any) -> str:
            return self.camel_to_snake(str(value))

        def _to_pascal_case_filter(value: Any) -> str:
            """キャメルケース/スネークケースをPascalCaseに変換する"""
            snake_str = str(value)
            # キャメルケースを一度スネークケースに変換してから処理
            snake_case = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_str).lower()
            # アンダースコアで分割してタイトルケースに
            parts = snake_case.replace('-', '_').split('_')
            return ''.join(word.capitalize() for word in parts)

        def _containing_model_reference_filter(value: Any) -> bool:
            """型がモデル参照を含んでいるかチェック"""
            type_str = str(value)
            # モデル名のパターンをチェック（大文字で始まる単語）
            import re

            return bool(re.search(r"\b[A-Z][a-zA-Z0-9]*\b", type_str))

        def _extract_model_name_filter(value: Any) -> str:
            """型文字列からモデル名を抽出"""
            type_str = str(value)
            import re

            # 最初に見つかった大文字で始まる単語を返す（Noneは除外）
            match = re.search(r"\b([A-Z][a-zA-Z0-9]*)\b", type_str)
            model_name = match.group(1) if match else ""
            # Noneは除外
            return model_name if model_name != "None" else ""

        def _get_return_type_filter(responses: dict[str, Any]) -> str:
            """レスポンス定義から返り値の型を取得"""
            if not responses:
                return "dict[str, Any]"

            for status_code, response in responses.items():
                if isinstance(status_code, int):
                    status_code = str(status_code)
                if status_code.startswith("2"):
                    response_schema = (
                        response.get("content", {})
                        .get("application/json", {})
                        .get("schema")
                    )
                    if response_schema:
                        if response_schema.get(
                            "type"
                        ) == "array" and response_schema.get("items", {}).get("$ref"):
                            model_name = response_schema["items"]["$ref"].split("/")[-1]
                            return f"list[{model_name}]"
                        elif response_schema.get("$ref"):
                            return response_schema["$ref"].split("/")[-1]

            return "dict[str, Any]"

        self.env.filters["python_type_from_openapi"] = _python_type_filter
        self.env.filters["lower"] = _lower_filter
        self.env.filters["replace"] = _replace_filter
        self.env.filters["camel_to_snake"] = _camel_to_snake_filter
        self.env.filters["to_pascal_case"] = _to_pascal_case_filter
        self.env.filters["containing_model_reference"] = (
            _containing_model_reference_filter
        )
        self.env.filters["extract_model_name"] = _extract_model_name_filter
        self.env.filters["get_return_type"] = _get_return_type_filter

        # テスト関数として登録
        self.env.tests["containing_model_reference"] = (
            _containing_model_reference_filter
        )

    def get_templates(self) -> dict[str, str]:
        """テンプレートを返す（サブクラスで実装）

        Returns:
            テンプレート名と内容の辞書

        Raises:
            NotImplementedError: サブクラスで実装が必要
        """
        raise NotImplementedError

    def generate_to_path(self, output_path: str | Path, **kwargs: Any) -> None:
        """指定されたパスにコードを生成する（サブクラスで実装）

        Args:
            output_path: 出力パス
            **kwargs: 追加オプション

        Raises:
            NotImplementedError: サブクラスで実装が必要
        """
        raise NotImplementedError

    def snake_to_camel(self, snake_str: str) -> str:
        """スネークケースをキャメルケースに変換する

        Args:
            snake_str: スネークケース文字列

        Returns:
            キャメルケース文字列
        """
        components = snake_str.split("_")
        return components[0] + "".join(x.capitalize() for x in components[1:])

    def camel_to_snake(self, camel_str: str) -> str:
        """キャメルケースをスネークケースに変換する

        Args:
            camel_str: キャメルケース文字列

        Returns:
            スネークケース文字列
        """
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", camel_str).lower()

    def python_type_from_openapi(self, schema: dict[str, Any] | None) -> str:
        """OpenAPI スキーマから Python 型を生成する

        Args:
            schema: OpenAPIスキーマ辞書

        Returns:
            Python型文字列
        """
        if not schema:
            return "Any"

        if "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            return ref_name

        schema_type = schema.get("type", "any")

        match schema_type:
            case "string":
                return "str"
            case "integer":
                return "int"
            case "number":
                return "float"
            case "boolean":
                return "bool"
            case "array":
                items = schema.get("items", {})
                item_type = self.python_type_from_openapi(items)
                return f"list[{item_type}]"
            case "object":
                return "dict[str, Any]"
            case _:
                return "Any"


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
            }
        else:
            return {
                "client.py": CLIENT_SYNC_TEMPLATE,
                "model.py": MODEL_TEMPLATE,
                "models_init.py": MODELS_INIT_TEMPLATE,
                "__init__.py": INIT_TEMPLATE,
                "endpoint.py": ENDPOINT_SYNC_TEMPLATE,
            }

    def generate_to_path(
        self,
        output_path: str | Path,
        use_async: bool = False,
        flat_structure: bool = False,
        **kwargs: Any,
    ) -> None:
        """クライアントコードを生成する

        Args:
            output_path: 出力パス
            use_async: 非同期クライアントを生成するか
            flat_structure: フラット構造で生成するか

        Raises:
            CodeGenerationError: コード生成に失敗した場合
        """
        output_dir = Path(output_path)

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            msg = f"出力ディレクトリの作成に失敗しました: {e}"
            raise CodeGenerationError(msg) from e

        # スキーマをパース
        if not self.parser.schema:
            self.parser.parse()

        # エンドポイントとスキーマを取得
        endpoints = self.parser.get_endpoints()
        schemas = self.parser.get_schemas()

        logger.info(
            "クライアント生成開始: endpoints=%d, schemas=%d",
            len(endpoints),
            len(schemas),
        )

        # モデル生成
        models = self._generate_models(schemas)

        if flat_structure:
            # 単一ファイル構成
            self._generate_flat_client(output_dir, endpoints, models, use_async)
        else:
            # ディレクトリ構成
            self._generate_structured_client(output_dir, endpoints, models, use_async)

        logger.info("クライアント生成完了: %s", output_dir)

    def _generate_models(
        self, schemas: dict[str, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Pydantic モデルを生成する

        Args:
            schemas: スキーマ定義辞書

        Returns:
            生成されたモデル情報のリスト
        """
        models: list[dict[str, Any]] = []

        for name, schema in schemas.items():
            fields: list[dict[str, Any]] = []

            if schema.get("type") == "object" and "properties" in schema:
                required_fields = set(schema.get("required", []))

                for field_name, field_schema in schema["properties"].items():
                    field_type = self.python_type_from_openapi(field_schema)
                    is_optional = field_name not in required_fields

                    if (
                        is_optional
                        and not field_type.endswith(" | None")
                        and "Optional[" not in field_type
                    ):
                        field_type = f"{field_type} | None"

                    fields.append(
                        {
                            "name": field_name,
                            "type": field_type,
                            "description": field_schema.get("description", ""),
                        }
                    )

            models.append(
                {
                    "name": name,
                    "fields": fields,
                    "description": schema.get("description", ""),
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
        """単一ファイル構成でクライアントを生成する

        Args:
            output_dir: 出力ディレクトリ
            endpoints: エンドポイントリスト
            models: モデルリスト
            use_async: 非同期クライアントか
        """
        templates = self.get_templates(use_async)
        template = self.env.from_string(templates["client.py"])

        content = template.render(
            endpoints=endpoints, models=models, flat_structure=True
        )

        (output_dir / "client.py").write_text(content, encoding="utf-8")
        (output_dir / "__init__.py").write_text(
            "from .client import *\n", encoding="utf-8"
        )

    def _generate_structured_client(
        self,
        output_dir: Path,
        endpoints: list[dict[str, Any]],
        models: list[dict[str, Any]],
        use_async: bool,
    ) -> None:
        """ディレクトリ構成でクライアントを生成する

        Args:
            output_dir: 出力ディレクトリ
            endpoints: エンドポイントリスト
            models: モデルリスト
            use_async: 非同期クライアントか
        """
        templates = self.get_templates(use_async)

        # メインクライアント
        client_template = self.env.from_string(templates["client.py"])
        client_content = client_template.render(
            endpoints=endpoints,
            models=models,
            flat_structure=False,
        )
        (output_dir / "client.py").write_text(client_content, encoding="utf-8")

        # モデル（構造化モードでは各ファイルに分割生成）
        models_dir = output_dir / "models"
        models_dir.mkdir(exist_ok=True)

        # 各モデルを個別ファイルに生成
        model_template = self.env.from_string(templates["model.py"])
        model_imports: list[str] = []

        for model in models:
            # モデルファイル生成
            model_content = model_template.render(model=model, all_models=models)
            filename = f"{model['name'].lower()}.py"
            (models_dir / filename).write_text(model_content, encoding="utf-8")
            model_imports.append(
                f"from .{model['name'].lower()} import {model['name']}"
            )

        # __init__.pyで全モデルをエクスポート
        init_models_template = self.env.from_string(templates["models_init.py"])
        init_content = init_models_template.render(
            models=models, model_imports=model_imports
        )
        (models_dir / "__init__.py").write_text(init_content, encoding="utf-8")

        # エンドポイント
        endpoints_dir = output_dir / "endpoints"
        endpoints_dir.mkdir(exist_ok=True)

        # タグ別にエンドポイントをグループ化
        endpoints_by_tag: dict[str, list[dict[str, Any]]] = {}
        for endpoint in endpoints:
            tags = endpoint.get("tags", ["default"])
            for tag in tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)

        endpoint_template = self.env.from_string(templates["endpoint.py"])

        for tag, tag_endpoints in endpoints_by_tag.items():
            filename = f"{tag.lower().replace(' ', '_')}.py"
            content = endpoint_template.render(tag=tag, endpoints=tag_endpoints)
            (endpoints_dir / filename).write_text(content, encoding="utf-8")

        # __init__.py
        init_template = self.env.from_string(templates["__init__.py"])
        init_content = init_template.render()
        (output_dir / "__init__.py").write_text(init_content, encoding="utf-8")


class ServerGenerator(CodeGenerator):
    """FastAPIサーバコードジェネレータ"""

    def get_templates(self) -> dict[str, str]:
        """サーバ生成用テンプレートを返す

        Returns:
            テンプレート辞書
        """
        return {
            "main.py": SERVER_MAIN_TEMPLATE,
            "route.py": SERVER_ROUTE_TEMPLATE,
            "dependencies.py": SERVER_DEPENDENCIES_TEMPLATE,
            "interfaces.py": SERVER_INTERFACES_TEMPLATE,
            "request_model.py": SERVER_REQUEST_MODEL_TEMPLATE,
            "response_model.py": SERVER_RESPONSE_MODEL_TEMPLATE,
        }

    def generate_to_path(
        self, output_path: str | Path, mock_response: bool = False, **kwargs: Any
    ) -> None:
        """FastAPIサーバコードを生成する

        Args:
            output_path: 出力パス
            mock_response: モックレスポンスを生成するか

        Raises:
            CodeGenerationError: コード生成に失敗した場合
        """
        output_dir = Path(output_path)

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            msg = f"出力ディレクトリの作成に失敗しました: {e}"
            raise CodeGenerationError(msg) from e

        # スキーマをパース
        if not self.parser.schema:
            self.parser.parse()

        endpoints = self.parser.get_endpoints()
        schemas = self.parser.get_schemas()

        logger.info(
            "FastAPIサーバ生成開始: endpoints=%d, schemas=%d",
            len(endpoints),
            len(schemas),
        )

        # メインアプリケーション
        main_template = self.env.get_template("main.py")
        main_content = main_template.render(
            endpoints=endpoints, schemas=schemas, mock_response=mock_response
        )
        (output_dir / "main.py").write_text(main_content, encoding="utf-8")

        # modelsディレクトリ作成
        models_dir = output_dir / "models"
        models_dir.mkdir(exist_ok=True)

        requests_dir = models_dir / "requests"
        responses_dir = models_dir / "responses"
        requests_dir.mkdir(exist_ok=True)
        responses_dir.mkdir(exist_ok=True)
        (requests_dir / "__init__.py").write_text("", encoding="utf-8")
        (responses_dir / "__init__.py").write_text("", encoding="utf-8")

        # リクエスト・レスポンスモデル生成
        self._generate_server_models(endpoints, schemas, requests_dir, responses_dir)

        # ルート生成
        routes_dir = output_dir / "routes"
        routes_dir.mkdir(exist_ok=True)

        # タグ別にルートをグループ化
        routes_by_tag: dict[str, list[dict[str, Any]]] = {}
        for endpoint in endpoints:
            tags = endpoint.get("tags", ["default"])
            for tag in tags:
                if tag not in routes_by_tag:
                    routes_by_tag[tag] = []
                routes_by_tag[tag].append(endpoint)

        route_template = self.env.get_template("route.py")

        for tag, tag_endpoints in routes_by_tag.items():
            filename = f"{tag.lower().replace(' ', '_')}.py"
            content = route_template.render(
                tag=tag, endpoints=tag_endpoints, mock_response=mock_response
            )
            (routes_dir / filename).write_text(content, encoding="utf-8")

        # インターフェース（戻り値を具体的なレスポンスオブジェクトに変更）
        interfaces_template = self.env.get_template("interfaces.py")
        interfaces_content = interfaces_template.render(endpoints=endpoints)
        (output_dir / "interfaces.py").write_text(interfaces_content, encoding="utf-8")

        # 依存関係
        deps_template = self.env.get_template("dependencies.py")
        deps_content = deps_template.render()
        (output_dir / "dependencies.py").write_text(deps_content, encoding="utf-8")

        logger.info("FastAPIサーバ生成完了: %s", output_dir)

    def _generate_server_models(
        self,
        endpoints: list[dict[str, Any]],
        schemas: dict[str, dict[str, Any]],
        requests_dir: Path,
        responses_dir: Path,
    ) -> None:
        """サーバ用モデル（リクエスト・レスポンス）を生成する

        Args:
            endpoints: エンドポイント情報
            schemas: スキーマ情報
            requests_dir: リクエストモデル出力ディレクトリ
            responses_dir: レスポンスモデル出力ディレクトリ
        """
        # 生成するモデルを収集
        request_models: list[dict[str, Any]] = []
        response_models: list[dict[str, Any]] = []

        # エンドポイントからリクエスト・レスポンスモデルを抽出
        for endpoint in endpoints:
            # リクエストモデル
            if endpoint.get("request_body"):
                request_schema = (
                    endpoint["request_body"]
                    .get("content", {})
                    .get("application/json", {})
                    .get("schema")
                )
                if request_schema:
                    model_name = f"{endpoint['operation_id'].title()}Request"
                    model_data = self._create_model_from_schema(
                        model_name, request_schema, schemas
                    )
                    if model_data:
                        request_models.append(model_data)

            # レスポンスモデル
            responses = endpoint.get("responses", {})
            for status_code, response_info in responses.items():
                if str(status_code).startswith("2"):  # 2xx成功レスポンス
                    response_schema = (
                        response_info.get("content", {})
                        .get("application/json", {})
                        .get("schema")
                    )
                    if response_schema:
                        model_name = f"{endpoint['operation_id'].title()}Response"
                        model_data = self._create_model_from_schema(
                            model_name, response_schema, schemas
                        )
                        if model_data:
                            response_models.append(model_data)
                    break  # 最初の成功レスポンスのみ

        # スキーマからモデルを生成（共通モデル）
        for schema_name, schema_def in schemas.items():
            # レスポンスモデルとして追加（既存のスキーマはレスポンスとして扱う）
            model_data = self._create_model_from_schema(
                schema_name, schema_def, schemas
            )
            if model_data:
                response_models.append(model_data)

        # 重複を除去
        unique_request_models = list(
            {model["name"]: model for model in request_models}.values()
        )
        unique_response_models = list(
            {model["name"]: model for model in response_models}.values()
        )

        # リクエストモデル生成
        request_template = self.env.get_template("request_model.py")
        for model in unique_request_models:
            filename = f"{model['name'].lower()}.py"
            content = request_template.render(model=model)
            (requests_dir / filename).write_text(content, encoding="utf-8")

        # レスポンスモデル生成
        response_template = self.env.get_template("response_model.py")
        for model in unique_response_models:
            filename = f"{model['name'].lower()}.py"
            content = response_template.render(model=model)
            (responses_dir / filename).write_text(content, encoding="utf-8")

        # __init__.py ファイル生成
        self._generate_models_init_files(
            requests_dir,
            responses_dir,
            list(unique_request_models),
            list(unique_response_models),
        )

    def _create_model_from_schema(
        self,
        model_name: str,
        schema: dict[str, Any],
        all_schemas: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        """スキーマからモデルデータを作成する

        Args:
            model_name: モデル名
            schema: スキーマ定義
            all_schemas: 全スキーマ定義

        Returns:
            モデルデータ辞書、作成できない場合はNone
        """
        # $ref参照の場合は解決
        if "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            if ref_name in all_schemas:
                return self._create_model_from_schema(
                    ref_name, all_schemas[ref_name], all_schemas
                )
            return None

        # オブジェクト型でない場合はスキップ
        if schema.get("type") != "object" or "properties" not in schema:
            return None

        fields: list[dict[str, Any]] = []
        properties = schema.get("properties", {})
        required = schema.get("required", [])

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

        return {
            "name": model_name,
            "description": schema.get("description", f"{model_name} model"),
            "fields": fields,
        }

    def _generate_models_init_files(
        self,
        requests_dir: Path,
        responses_dir: Path,
        request_models: list[dict[str, Any]],
        response_models: list[dict[str, Any]],
    ) -> None:
        """モデルパッケージの__init__.pyファイルを生成する

        Args:
            requests_dir: リクエストモデルディレクトリ
            responses_dir: レスポンスモデルディレクトリ
            request_models: リクエストモデル一覧
            response_models: レスポンスモデル一覧
        """
        # リクエストモデル __init__.py
        if request_models:
            request_imports: list[str] = []
            for model in request_models:
                module_name = model["name"].lower()
                request_imports.append(f"from .{module_name} import {model['name']}")

            request_init_content = f'''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

リクエストモデルパッケージ
"""

{chr(10).join(request_imports)}

__all__ = [
{chr(10).join(f'    "{model["name"]}",' for model in request_models)}
]
'''
            (requests_dir / "__init__.py").write_text(
                request_init_content, encoding="utf-8"
            )

        # レスポンスモデル __init__.py
        if response_models:
            response_imports: list[str] = []
            for model in response_models:
                module_name = model["name"].lower()
                response_imports.append(f"from .{module_name} import {model['name']}")

            response_init_content = f'''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

レスポンスモデルパッケージ
"""

{chr(10).join(response_imports)}

__all__ = [
{chr(10).join(f'    "{model["name"]}",' for model in response_models)}
]
'''
            (responses_dir / "__init__.py").write_text(
                response_init_content, encoding="utf-8"
            )

        # メインモデル __init__.py
        models_init_content = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

モデルパッケージ
"""

from .requests import *
from .responses import *

'''
        (requests_dir.parent / "__init__.py").write_text(
            models_init_content, encoding="utf-8"
        )


class FlaskServerGenerator(CodeGenerator):
    """Flask サーバコードジェネレータ"""

    def get_templates(self) -> dict[str, str]:
        """Flask サーバ生成用テンプレートを返す

        Returns:
            テンプレート辞書
        """
        return {
            "service_interface.py": FLASK_SERVICE_INTERFACE_TEMPLATE,
            "model.py": FLASK_MODEL_TEMPLATE,
        }

    def generate_to_path(
        self, output_path: str | Path, mock_response: bool = False, **kwargs: Any
    ) -> None:
        """Flask サーバコードを生成する

        Args:
            output_path: 出力パス
            mock_response: モックレスポンスを生成するか

        Raises:
            CodeGenerationError: コード生成に失敗した場合
        """
        output_dir = Path(output_path)

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            msg = f"出力ディレクトリの作成に失敗しました: {e}"
            raise CodeGenerationError(msg) from e

        # スキーマをパース
        if not self.parser.schema:
            self.parser.parse()

        endpoints = self.parser.get_endpoints()
        schemas = self.parser.get_schemas()

        logger.info(
            "Flask サーバ生成開始: endpoints=%d, schemas=%d",
            len(endpoints),
            len(schemas),
        )

        # タグ別にサービスを生成
        routes_by_tag: dict[str, list[dict[str, Any]]] = {}
        for endpoint in endpoints:
            tags = endpoint.get("tags", ["default"])
            for tag in tags:
                if tag not in routes_by_tag:
                    routes_by_tag[tag] = []
                routes_by_tag[tag].append(endpoint)

        # modelsディレクトリを作成
        models_dir = output_dir / "models"
        models_dir.mkdir(exist_ok=True)
        (models_dir / "__init__.py").write_text("", encoding="utf-8")

        # request/responseフォルダを作成
        requests_dir = models_dir / "requests"
        responses_dir = models_dir / "responses"
        requests_dir.mkdir(exist_ok=True)
        responses_dir.mkdir(exist_ok=True)
        (requests_dir / "__init__.py").write_text("", encoding="utf-8")
        (responses_dir / "__init__.py").write_text("", encoding="utf-8")

        # 既存スキーマのモデルを生成
        if schemas:
            models = self._generate_models_from_schemas(schemas)
            model_template = self.env.get_template("model.py")

            for model in models:
                filename = f"{self._to_snake_case(model['name'])}.py"
                content = model_template.render(model=model)
                (models_dir / filename).write_text(content, encoding="utf-8")

        # エンドポイント用のリクエスト/レスポンスモデルを生成
        self._generate_endpoint_models(routes_by_tag, requests_dir, responses_dir)

        # サービスインターフェース
        service_interface_template = self.env.get_template("service_interface.py")
        for tag, tag_endpoints in routes_by_tag.items():
            filename = f"{tag.lower().replace(' ', '_')}_service.py"

            # モデル情報を準備
            request_models = []
            response_models = []

            for endpoint in tag_endpoints:
                operation_id = endpoint.get("operation_id", "Unknown")

                if endpoint.get("request_body"):
                    request_class_name = self._to_pascal_case(operation_id) + "Request"
                    request_models.append(
                        {
                            "class_name": request_class_name,
                            "snake_case_name": self._to_snake_case(request_class_name),
                        }
                    )

                response_class_name = self._to_pascal_case(operation_id) + "Response"
                response_models.append(
                    {
                        "class_name": response_class_name,
                        "snake_case_name": self._to_snake_case(response_class_name),
                    }
                )

            content = service_interface_template.render(
                tag=tag,
                endpoints=tag_endpoints,
                mock_response=mock_response,
                request_models=request_models,
                response_models=response_models,
            )
            (output_dir / filename).write_text(content, encoding="utf-8")

        # トップレベルの__init__.pyを生成
        (output_dir / "__init__.py").write_text(
            '"""Cloud Functions Flask アプリケーション"""\n', encoding="utf-8"
        )

        logger.info("Flask サーバ生成完了: %s", output_dir)

    def _generate_models_from_schemas(
        self, schemas: dict[str, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """スキーマからモデルを生成する"""
        models = []
        for name, schema in schemas.items():
            model = self._create_model_from_schema(name, schema, schemas)
            if model:
                models.append(model)
        return models

    def _generate_endpoint_models(
        self,
        routes_by_tag: dict[str, list[dict[str, Any]]],
        requests_dir: Path,
        responses_dir: Path,
    ) -> None:
        """エンドポイント用のリクエスト/レスポンスモデルを生成する"""
        model_template = self.env.get_template("model.py")

        for tag, endpoints in routes_by_tag.items():
            for endpoint in endpoints:
                operation_id = endpoint.get("operation_id", "Unknown")

                # リクエストモデル生成
                if endpoint.get("request_body"):
                    request_class_name = self._to_pascal_case(operation_id) + "Request"
                    request_model = {
                        "name": request_class_name,
                        "description": f"{endpoint.get('summary', '')} のリクエスト",
                        "fields": self._extract_request_fields(endpoint),
                    }
                    filename = f"{self._to_snake_case(request_class_name)}.py"
                    content = model_template.render(model=request_model)
                    (requests_dir / filename).write_text(content, encoding="utf-8")

                # レスポンスモデル生成
                response_class_name = self._to_pascal_case(operation_id) + "Response"
                response_model = {
                    "name": response_class_name,
                    "description": f"{endpoint.get('summary', '')} のレスポンス",
                    "fields": self._extract_response_fields(endpoint),
                }
                filename = f"{self._to_snake_case(response_class_name)}.py"
                content = model_template.render(model=response_model)
                (responses_dir / filename).write_text(content, encoding="utf-8")

    def _extract_request_fields(self, endpoint: dict[str, Any]) -> list[dict[str, Any]]:
        """エンドポイントからリクエストフィールドを抽出"""
        fields = []
        request_body = endpoint.get("request_body", {})
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})

        # $ref参照を解決
        if "$ref" in schema:
            ref_path = schema["$ref"]
            if ref_path.startswith("#/components/schemas/"):
                schema_name = ref_path.split("/")[-1]
                # 今は既存のNewPetスキーマの内容を直接設定
                if schema_name == "NewPet":
                    schema = {
                        "type": "object",
                        "required": ["name", "status"],
                        "properties": {
                            "name": {"type": "string", "description": "ペット名"},
                            "category": {"$ref": "#/components/schemas/Category"},
                            "tags": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/Tag"},
                            },
                            "status": {
                                "type": "string",
                                "enum": ["available", "pending", "sold"],
                                "description": "ペットのステータス",
                            },
                        },
                    }
                elif schema_name == "NewUser":
                    schema = {
                        "type": "object",
                        "required": ["username", "email"],
                        "properties": {
                            "username": {"type": "string", "description": "ユーザー名"},
                            "email": {
                                "type": "string",
                                "format": "email",
                                "description": "メールアドレス",
                            },
                            "firstName": {"type": "string", "description": "名前"},
                            "lastName": {"type": "string", "description": "姓"},
                            "phone": {"type": "string", "description": "電話番号"},
                        },
                    }

        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            required = schema.get("required", [])

            for field_name, field_schema in properties.items():
                field_type = self.python_type_from_openapi(field_schema)
                if field_name not in required:
                    field_type += " | None = None"

                fields.append(
                    {
                        "name": field_name,
                        "type": field_type,
                        "description": field_schema.get("description", ""),
                    }
                )

        return fields

    def _extract_response_fields(
        self, endpoint: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """エンドポイントからレスポンスフィールドを抽出"""
        # 200番台のレスポンスを探す
        responses = endpoint.get("responses", {})
        success_response = None

        for status_code, response in responses.items():
            if str(status_code).startswith("2"):  # 2xx success
                success_response = response
                break

        if not success_response:
            # レスポンスがない場合（例: 204 No Content）
            return []

        content = success_response.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})

        if not schema:
            # レスポンスボディがない場合
            return []

        # $ref参照を解決
        if "$ref" in schema:
            ref_path = schema["$ref"]
            if ref_path.startswith("#/components/schemas/"):
                schema_name = ref_path.split("/")[-1]
                # 既存スキーマを参照する場合は、そのスキーマ型を返す
                return [
                    {
                        "name": "data",
                        "type": schema_name,
                        "description": f"{schema_name}オブジェクト",
                    }
                ]

        # 配列の場合
        if schema.get("type") == "array":
            items = schema.get("items", {})
            if "$ref" in items:
                ref_path = items["$ref"]
                if ref_path.startswith("#/components/schemas/"):
                    schema_name = ref_path.split("/")[-1]
                    return [
                        {
                            "name": "data",
                            "type": f"list[{schema_name}]",
                            "description": f"{schema_name}オブジェクトの配列",
                        }
                    ]

        # プリミティブ型の場合
        if schema.get("type") in ["string", "integer", "boolean", "number"]:
            python_type = self.python_type_from_openapi(schema)
            return [
                {"name": "data", "type": python_type, "description": "レスポンスデータ"}
            ]

        # オブジェクト型の場合（直接定義）
        if schema.get("type") == "object":
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            fields = []

            for field_name, field_schema in properties.items():
                field_type = self.python_type_from_openapi(field_schema)
                if field_name not in required:
                    field_type += " | None = None"

                fields.append(
                    {
                        "name": field_name,
                        "type": field_type,
                        "description": field_schema.get("description", ""),
                    }
                )

            return fields

        # フォールバック: 不明な場合
        return [{"name": "data", "type": "Any", "description": "レスポンスデータ"}]

    def _create_model_from_schema(
        self,
        model_name: str,
        schema: dict[str, Any],
        all_schemas: dict[str, dict[str, Any]],
    ) -> dict[str, Any] | None:
        """スキーマからモデルを作成する"""
        if schema.get("type") != "object":
            return None

        fields = []
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for field_name, field_schema in properties.items():
            field_type = self.python_type_from_openapi(field_schema)
            if field_name not in required:
                field_type += " | None = None"

            fields.append(
                {
                    "name": field_name,
                    "type": field_type,
                    "description": field_schema.get("description", ""),
                }
            )

        return {
            "name": model_name,
            "description": schema.get("description", ""),
            "fields": fields,
        }

    def _to_snake_case(self, camel_str: str) -> str:
        """キャメルケースをスネークケースに変換する"""
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", camel_str).lower()

    def _to_pascal_case(self, snake_str: str) -> str:
        """スネークケース/キャメルケースをPascalCaseに変換する"""
        # キャメルケースを一度スネークケースに変換してから処理
        snake_case = re.sub("([a-z0-9])([A-Z])", r"\1_\2", snake_str).lower()
        # アンダースコアで分割してタイトルケースに
        parts = snake_case.replace("-", "_").split("_")
        return "".join(word.capitalize() for word in parts)


# テンプレート定義
CLIENT_SYNC_TEMPLATE = '''"""生成されたAPIクライアント（同期版）"""

from __future__ import annotations
from typing import Any

import httpx
from pydantic import BaseModel

{%- if not flat_structure %}
from .models import *
{%- endif %}

{%- if flat_structure and models %}
# モデル定義
{%- for model in models %}
class {{ model.name }}(BaseModel):
    """{{ model.description }}"""
{%- for field in model.fields %}
    {{ field.name }}: {{ field.type }}{% if field.description %}  # {{ field.description }}{% endif %}
{%- endfor %}
{%- endfor %}
{%- endif %}

class APIClient:
    """生成されたAPIクライアント（同期版）"""

    def __init__(self, base_url: str, headers: dict[str, str] | None = None) -> None:
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.client = httpx.Client()

    def close(self) -> None:
        """クライアントを閉じる"""
        self.client.close()

{%- for endpoint in endpoints %}
    def {{ endpoint.operation_id | lower }}(self{% for param in endpoint.parameters %}, {{ param.name }}: {{ param.schema | python_type_from_openapi }}{% if not param.required %} | None = None{% endif %}{% endfor %}{% if endpoint.request_body %}, data: dict[str, Any] | None = None{% endif %}) -> {{ endpoint.responses | get_return_type }}:
        """{{ endpoint.summary }}

        {{ endpoint.description }}
        """
        url = f"{self.base_url}{{ endpoint.path }}"

        # パスパラメータの置換
{%- for param in endpoint.parameters %}
{%- if param.in == 'path' %}
        url = url.replace("{{ '{' + param.name + '}' }}", str({{ param.name }}))
{%- endif %}
{%- endfor %}

        # クエリパラメータ
        params: dict[str, Any] = {}
{%- for param in endpoint.parameters %}
{%- if param.in == 'query' %}
        if {{ param.name }} is not None:
            params["{{ param.name }}"] = {{ param.name }}
{%- endif %}
{%- endfor %}

        headers = {**self.headers}
{%- for param in endpoint.parameters %}
{%- if param.in == 'header' %}
        if {{ param.name }} is not None:
            headers["{{ param.name }}"] = str({{ param.name }})
{%- endif %}
{%- endfor %}

        response = self.client.request(
            method="{{ endpoint.method }}",
            url=url,
            params=params,
            headers=headers,
            {%- if endpoint.request_body %}
            json=data,
            {%- endif %}
        )

        response.raise_for_status()
        result = response.json()
        
        # レスポンスを適切なモデルにキャスト
{%- if endpoint.responses %}
{%- for status_code, response in endpoint.responses.items() %}
{%- if (status_code | int >= 200 and status_code | int < 300) %}
{%- set response_schema = response.get('content', {}).get('application/json', {}).get('schema') %}
{%- if response_schema %}
{%- if response_schema.get('type') == 'array' and response_schema.get('items', {}).get('$ref') %}
        # 配列レスポンス ({{ status_code }})
        if isinstance(result, list):
            return [{{ response_schema['items']['$ref'].split('/')[-1] }}.model_validate(item) for item in result]
{%- elif response_schema.get('$ref') %}
        # 単一オブジェクトレスポンス ({{ status_code }})
        if isinstance(result, dict):
            return {{ response_schema['$ref'].split('/')[-1] }}.model_validate(result)
{%- endif %}
{%- endif %}
{%- endif %}
{%- endfor %}
{%- endif %}
        return result
{%- endfor %}

'''

CLIENT_ASYNC_TEMPLATE = '''"""生成されたAPIクライアント（非同期版）"""

from __future__ import annotations
from typing import Any

import httpx
from pydantic import BaseModel

{%- if not flat_structure %}
from .models import *
{%- endif %}

{%- if flat_structure and models %}
# モデル定義
{%- for model in models %}
class {{ model.name }}(BaseModel):
    """{{ model.description }}"""
{%- for field in model.fields %}
    {{ field.name }}: {{ field.type }}{% if field.description %}  # {{ field.description }}{% endif %}
{%- endfor %}
{%- endfor %}
{%- endif %}

class APIClient:
    """生成されたAPIクライアント（非同期版）"""

    def __init__(self, base_url: str, headers: dict[str, str] | None = None) -> None:
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.client = httpx.AsyncClient()

    async def close(self) -> None:
        """クライアントを閉じる"""
        await self.client.aclose()

{%- for endpoint in endpoints %}
    async def {{ endpoint.operation_id | lower }}(self{% for param in endpoint.parameters %}, {{ param.name }}: {{ param.schema | python_type_from_openapi }}{% if not param.required %} | None = None{% endif %}{% endfor %}{% if endpoint.request_body %}, data: dict[str, Any] | None = None{% endif %}) -> {{ endpoint.responses | get_return_type }}:
        """{{ endpoint.summary }}

        {{ endpoint.description }}
        """
        url = f"{self.base_url}{{ endpoint.path }}"

        # パスパラメータの置換
{%- for param in endpoint.parameters %}
{%- if param.in == 'path' %}
        url = url.replace("{{ '{' + param.name + '}' }}", str({{ param.name }}))
{%- endif %}
{%- endfor %}

        # クエリパラメータ
        params: dict[str, Any] = {}
{%- for param in endpoint.parameters %}
{%- if param.in == 'query' %}
        if {{ param.name }} is not None:
            params["{{ param.name }}"] = {{ param.name }}
{%- endif %}
{%- endfor %}

        headers = {**self.headers}
{%- for param in endpoint.parameters %}
{%- if param.in == 'header' %}
        if {{ param.name }} is not None:
            headers["{{ param.name }}"] = str({{ param.name }})
{%- endif %}
{%- endfor %}

        response = await self.client.request(
            method="{{ endpoint.method }}",
            url=url,
            params=params,
            headers=headers,
            {%- if endpoint.request_body %}
            json=data,
            {%- endif %}
        )

        response.raise_for_status()
        result = response.json()
        
        # レスポンスを適切なモデルにキャスト
{%- if endpoint.responses %}
{%- for status_code, response in endpoint.responses.items() %}
{%- if (status_code | int >= 200 and status_code | int < 300) %}
{%- set response_schema = response.get('content', {}).get('application/json', {}).get('schema') %}
{%- if response_schema %}
{%- if response_schema.get('type') == 'array' and response_schema.get('items', {}).get('$ref') %}
        # 配列レスポンス ({{ status_code }})
        if isinstance(result, list):
            return [{{ response_schema['items']['$ref'].split('/')[-1] }}.model_validate(item) for item in result]
{%- elif response_schema.get('$ref') %}
        # 単一オブジェクトレスポンス ({{ status_code }})
        if isinstance(result, dict):
            return {{ response_schema['$ref'].split('/')[-1] }}.model_validate(result)
{%- endif %}
{%- endif %}
{%- endif %}
{%- endfor %}
{%- endif %}
        return result
{%- endfor %}

'''

MODELS_TEMPLATE = '''"""生成されたPydanticモデル"""

from __future__ import annotations

from pydantic import BaseModel

{%- for model in models %}
class {{ model.name }}(BaseModel):
    """{{ model.description }}"""
{%- for field in model.fields %}
    {{ field.name }}: {{ field.type }}{% if field.description %}  # {{ field.description }}{% endif %}
{%- endfor %}
{%- endfor %}

'''

MODEL_TEMPLATE = '''"""{{ model.name }} モデル定義"""

from __future__ import annotations
{%- set imports = [] %}
{%- for field in model.fields %}
{%- if field.type is containing_model_reference %}
{%- set model_name = field.type | extract_model_name %}
{%- if model_name != model.name and model_name not in imports %}
{%- set _ = imports.append(model_name) %}
{%- endif %}
{%- endif %}
{%- endfor %}

from pydantic import BaseModel
{%- for import_model in imports %}
from .{{ import_model | lower }} import {{ import_model }}
{%- endfor %}


class {{ model.name }}(BaseModel):
    """{{ model.description }}"""
{%- for field in model.fields %}
    {{ field.name }}: {{ field.type }}{% if field.description %}  # {{ field.description }}{% endif %}
{%- endfor %}

'''

MODELS_INIT_TEMPLATE = '''"""モデルパッケージ初期化ファイル"""

{%- for import_line in model_imports %}
{{ import_line }}
{%- endfor %}

__all__ = [
{%- for model in models %}
    "{{ model.name }}",
{%- endfor %}
]

'''

INIT_TEMPLATE = '''"""生成されたクライアントライブラリ"""

from .client import APIClient
{%- if not flat_structure %}
from .models import *
{%- endif %}

__all__ = ["APIClient"]

'''

ENDPOINT_SYNC_TEMPLATE = '''"""{{ tag }} エンドポイント（同期版）"""

from __future__ import annotations
from typing import Any

from ..client import APIClient
from ..models import *


class {{ tag | title }}Endpoints:
    """{{ tag }}エンドポイントクラス"""

    def __init__(self, client: APIClient) -> None:
        """初期化
        
        Args:
            client: APIクライアントインスタンス
        """
        self.client = client

{%- for endpoint in endpoints %}

    def {{ endpoint.operation_id | camel_to_snake }}(self{% for param in endpoint.parameters %}, {{ param.name }}: {{ param.schema | python_type_from_openapi }}{% if not param.required %} | None = None{% endif %}{% endfor %}{% if endpoint.request_body %}, data: dict[str, Any] | None = None{% endif %}) -> Any:
        """{{ endpoint.summary }}

        {{ endpoint.description }}
        """
        response = self.client.{{ endpoint.operation_id | lower }}(
{%- for param in endpoint.parameters %}
            {{ param.name }}={{ param.name }},
{%- endfor %}
{%- if endpoint.request_body %}
            data=data
{%- endif %}
        )
        
        # レスポンスを適切なモデルにキャスト
{%- if endpoint.responses and endpoint.responses.get('200') %}
{%- set response_schema = endpoint.responses['200'].get('content', {}).get('application/json', {}).get('schema') %}
{%- if response_schema and response_schema.get('$ref') %}
{%- set model_name = response_schema['$ref'].split('/')[-1] %}
        if isinstance(response, dict):
            return {{ model_name }}.model_validate(response)
{%- elif response_schema and response_schema.get('type') == 'array' and response_schema.get('items', {}).get('$ref') %}
{%- set model_name = response_schema['items']['$ref'].split('/')[-1] %}
        if isinstance(response, list):
            return [{{ model_name }}.model_validate(item) for item in response]
{%- endif %}
{%- endif %}
        return response
{%- endfor %}

'''

ENDPOINT_ASYNC_TEMPLATE = '''"""{{ tag }} エンドポイント（非同期版）"""

from __future__ import annotations
from typing import Any

from ..client import APIClient
from ..models import *


class {{ tag | title }}Endpoints:
    """{{ tag }}エンドポイントクラス"""

    def __init__(self, client: APIClient) -> None:
        """初期化
        
        Args:
            client: APIクライアントインスタンス
        """
        self.client = client

{%- for endpoint in endpoints %}

    async def {{ endpoint.operation_id | camel_to_snake }}(self{% for param in endpoint.parameters %}, {{ param.name }}: {{ param.schema | python_type_from_openapi }}{% if not param.required %} | None = None{% endif %}{% endfor %}{% if endpoint.request_body %}, data: dict[str, Any] | None = None{% endif %}) -> Any:
        """{{ endpoint.summary }}

        {{ endpoint.description }}
        """
        response = await self.client.{{ endpoint.operation_id | lower }}(
{%- for param in endpoint.parameters %}
            {{ param.name }}={{ param.name }},
{%- endfor %}
{%- if endpoint.request_body %}
            data=data
{%- endif %}
        )
        
        # レスポンスを適切なモデルにキャスト
{%- if endpoint.responses and endpoint.responses.get('200') %}
{%- set response_schema = endpoint.responses['200'].get('content', {}).get('application/json', {}).get('schema') %}
{%- if response_schema and response_schema.get('$ref') %}
{%- set model_name = response_schema['$ref'].split('/')[-1] %}
        if isinstance(response, dict):
            return {{ model_name }}.model_validate(response)
{%- elif response_schema and response_schema.get('type') == 'array' and response_schema.get('items', {}).get('$ref') %}
{%- set model_name = response_schema['items']['$ref'].split('/')[-1] %}
        if isinstance(response, list):
            return [{{ model_name }}.model_validate(item) for item in response]
{%- endif %}
{%- endif %}
        return response
{%- endfor %}

'''

SERVER_MAIN_TEMPLATE = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

生成されたFastAPIアプリケーション
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Generated API Server",
    description="OpenAPI仕様書から生成されたAPIサーバ",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルートのインポートと設定
{%- set processed_tags = [] %}
{%- for endpoint in endpoints %}
{%- set tag = endpoint.tags[0] if endpoint.tags else 'default' %}
{%- if tag not in processed_tags %}
{%- set _ = processed_tags.append(tag) %}
from .routes.{{ tag | lower | replace(' ', '_') }} import router as {{ tag | lower | replace(' ', '_') }}_router
{%- endif %}
{%- endfor %}

# ルーターの登録
{%- set processed_tags = [] %}
{%- for endpoint in endpoints %}
{%- set tag = endpoint.tags[0] if endpoint.tags else 'default' %}
{%- if tag not in processed_tags %}
{%- set _ = processed_tags.append(tag) %}
app.include_router({{ tag | lower | replace(' ', '_') }}_router, prefix="/api")
{%- endif %}
{%- endfor %}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

'''

SERVER_ROUTE_TEMPLATE = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

{{ tag }} ルート
"""

from __future__ import annotations
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError

from ..interfaces import {{ tag | title }}Service
from ..models.requests import *
from ..models.responses import *

router = APIRouter(tags=["{{ tag }}"])


def get_{{ tag | lower }}_service() -> {{ tag | title }}Service:
    """{{ tag }}サービスの依存関係注入
    
    TODO: 実装クラスを作成して返すように修正してください
    例: return YourImplementationClass()
    """
    raise NotImplementedError("サービス実装クラスを作成して注入してください")

{%- for endpoint in endpoints %}

@router.{{ endpoint.method | lower }}("{{ endpoint.path }}")
def {{ endpoint.operation_id | camel_to_snake }}(
{%- for param in endpoint.parameters %}
    {{ param.name }}: {{ param.schema | python_type_from_openapi }}{% if not param.required %} | None = None{% endif %},
{%- endfor %}
{%- if endpoint.request_body %}
    request_data: {{ endpoint.operation_id | title }}Request,
{%- endif %}
    service: {{ tag | title }}Service = Depends(get_{{ tag | lower }}_service)
) -> dict[str, Any]:
    """{{ endpoint.summary }}

    {{ endpoint.description }}
    """
    try:
        # サービスからレスポンスオブジェクトを取得
        response_obj = service.{{ endpoint.operation_id | camel_to_snake }}(
{%- for param in endpoint.parameters %}
            {{ param.name }}={{ param.name }},
{%- endfor %}
{%- if endpoint.request_body %}
            request_data=request_data
{%- endif %}
        )
        
        # レスポンスオブジェクトをdict[str, Any]にキャスト
        if hasattr(response_obj, 'model_dump'):
            return response_obj.model_dump()
        elif isinstance(response_obj, dict):
            return response_obj
        else:
            return {"data": response_obj}
            
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
{%- endfor %}

'''

SERVER_SCHEMAS_TEMPLATE = '''"""生成されたPydanticスキーマ"""

from __future__ import annotations

from pydantic import BaseModel

{%- for name, schema in schemas.items() %}
class {{ name }}(BaseModel):
    """{{ schema.get('description', '') }}"""
{%- if schema.get('type') == 'object' and 'properties' in schema %}
{%- for field_name, field_schema in schema.properties.items() %}
    {{ field_name }}: {{ field_schema | python_type_from_openapi }}{% if field_name not in schema.get('required', []) %} | None = None{% endif %}
{%- endfor %}
{%- endif %}
{%- endfor %}

# リクエストDTO
{%- for endpoint in endpoints %}
{%- if endpoint.request_body %}
{%- set request_schema = endpoint.request_body.get('content', {}).get('application/json', {}).get('schema') %}
{%- if request_schema %}
class {{ endpoint.operation_id | title }}Request(BaseModel):
    """{{ endpoint.summary }}のリクエストDTO"""
{%- if request_schema.get('$ref') %}
{%- set ref_name = request_schema['$ref'].split('/')[-1] %}
    data: {{ ref_name }}
{%- elif request_schema.get('type') == 'object' and 'properties' in request_schema %}
{%- for field_name, field_schema in request_schema.properties.items() %}
    {{ field_name }}: {{ field_schema | python_type_from_openapi }}{% if field_name not in request_schema.get('required', []) %} | None = None{% endif %}
{%- endfor %}
{%- else %}
    data: dict[str, Any]
{%- endif %}
{%- endif %}
{%- endif %}
{%- endfor %}

'''

SERVER_DEPENDENCIES_TEMPLATE = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

共通依存関係
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> None:
    """認証情報を検証する"""
    # TODO: 認証ロジックを実装
    pass

'''

SERVER_INTERFACES_TEMPLATE = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

ビジネスロジックインターフェース
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

from .models.requests import *
from .models.responses import *

{%- set processed_tags = [] %}
{%- for endpoint in endpoints %}
{%- set tag = endpoint.tags[0] if endpoint.tags else 'default' %}
{%- if tag not in processed_tags %}
{%- set _ = processed_tags.append(tag) %}

class {{ tag | title }}Service(ABC):
    """{{ tag }}サービスのインターフェース"""
{%- for endpoint in endpoints %}
{%- if (endpoint.tags[0] if endpoint.tags else 'default') == tag %}
    
    @abstractmethod
    def {{ endpoint.operation_id | camel_to_snake }}(
        self,
{%- for param in endpoint.parameters %}
        {{ param.name }}: {{ param.schema | python_type_from_openapi }}{% if not param.required %} | None = None{% endif %},
{%- endfor %}
{%- if endpoint.request_body %}
        request: {{ (endpoint.operation_id | title) + "Request" }},
{%- endif %}
    ) -> {{ (endpoint.operation_id | title) + "Response" }}:
        """{{ endpoint.summary }}

        {{ endpoint.description }}
        
        Args:
{%- for param in endpoint.parameters %}
            {{ param.name }}: {{ param.description or param.name }}
{%- endfor %}
{%- if endpoint.request_body %}
            request: リクエストデータ
{%- endif %}
            
        Returns:
            {{ (endpoint.operation_id | title) + "Response" }}: レスポンスデータ
        """
        raise NotImplementedError
{%- endif %}
{%- endfor %}
{%- endif %}
{%- endfor %}

'''


# Flask テンプレート定義（Cloud Functions用）

FLASK_SERVICE_INTERFACE_TEMPLATE = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

{{ tag | title }}Service インターフェース
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict

# モデルのインポート
{%- set imported_models = [] %}
{%- for endpoint in endpoints %}
{%- if (endpoint.tags[0] if endpoint.tags else 'default') == tag %}
{%- if endpoint.request_body %}
{%- set request_class = endpoint.operation_id | to_pascal_case + "Request" %}
{%- set request_file = endpoint.operation_id | camel_to_snake + "_request" %}
{%- if request_class not in imported_models %}
from .models.requests.{{ request_file }} import {{ request_class }}
{%- set _ = imported_models.append(request_class) %}
{%- endif %}
{%- endif %}
{%- set response_class = endpoint.operation_id | to_pascal_case + "Response" %}
{%- set response_file = endpoint.operation_id | camel_to_snake + "_response" %}
{%- if response_class not in imported_models %}
from .models.responses.{{ response_file }} import {{ response_class }}
{%- set _ = imported_models.append(response_class) %}
{%- endif %}
{%- endif %}
{%- endfor %}

class {{ tag | title }}Service(ABC):
    """{{ tag }}サービスのインターフェース"""
{%- for endpoint in endpoints %}
{%- if (endpoint.tags[0] if endpoint.tags else 'default') == tag %}
    @abstractmethod
    def {{ endpoint.operation_id | camel_to_snake }}(
        self,
{%- for param in endpoint.parameters %}
        {{ param.name }}: {{ param.schema | python_type_from_openapi }}{% if not param.required %} | None = None{% endif %},
{%- endfor %}
{%- if endpoint.request_body %}
        request: {{ endpoint.operation_id | to_pascal_case + "Request" }},
{%- endif %}
    ) -> {{ endpoint.operation_id | to_pascal_case + "Response" }}:
        """{{ endpoint.summary }}

        {{ endpoint.description }}
        
        Args:
{%- for param in endpoint.parameters %}
            {{ param.name }}: {{ param.description or param.name }}
{%- endfor %}
{%- if endpoint.request_body %}
            request: リクエストデータ
{%- endif %}
            
        Returns:
            {{ endpoint.operation_id | to_pascal_case + "Response" }}: レスポンスデータ
        """
        raise NotImplementedError

{%- endif %}
{%- endfor %}
'''


FLASK_REPOSITORY_INTERFACE_TEMPLATE = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

{{ tag | title }}Repository インターフェース
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class {{ tag | title }}Repository(ABC):
    """{{ tag }}リポジトリのインターフェース"""

    @abstractmethod
    def find_all(self) -> List[Dict[str, Any]]:
        """全て取得"""
        pass

    @abstractmethod
    def find_by_id(self, id: Any) -> Dict[str, Any] | None:
        """IDで取得"""
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """作成"""
        pass

    @abstractmethod
    def update(self, id: Any, data: Dict[str, Any]) -> Dict[str, Any] | None:
        """更新"""
        pass

    @abstractmethod
    def delete(self, id: Any) -> bool:
        """削除"""
        pass
'''

FLASK_LOGGER_TEMPLATE = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

構造化ログユーティリティ
"""

from __future__ import annotations
import json
import logging
from typing import Any, Dict

class StructuredLogger:
    """構造化ログを提供するクラス"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # フォーマッターを設定
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def info(self, message: str, **kwargs: Any) -> None:
        """INFO レベルのログを出力"""
        self._log(logging.INFO, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """ERROR レベルのログを出力"""
        self._log(logging.ERROR, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """WARNING レベルのログを出力"""
        self._log(logging.WARNING, message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """DEBUG レベルのログを出力"""
        self._log(logging.DEBUG, message, **kwargs)

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        """ログを出力"""
        if kwargs:
            log_data = {"message": message, **kwargs}
            self.logger.log(level, json.dumps(log_data, ensure_ascii=False))
        else:
            self.logger.log(level, message)
'''


FLASK_REQUIREMENTS_TEMPLATE = """# Flask + Cloud Functions 依存関係
Flask>=2.3.0
flask-cors>=4.0.0
pydantic>=2.0.0
functions-framework>=3.0.0

# 開発用
pytest>=7.0.0
pytest-flask>=1.2.0

"""

# サーバモデル生成テンプレート
SERVER_REQUEST_MODEL_TEMPLATE = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

{{ model.name }} リクエストモデル定義
"""

from __future__ import annotations
{%- set imports = [] %}
{%- for field in model.fields %}
{%- if field.type is containing_model_reference %}
{%- set model_name = field.type | extract_model_name %}
{%- if model_name != model.name and model_name not in imports %}
{%- set _ = imports.append(model_name) %}
{%- endif %}
{%- endif %}
{%- endfor %}

from pydantic import BaseModel
{%- for import_model in imports %}
from ..responses.{{ import_model | lower }} import {{ import_model }}
{%- endfor %}


class {{ model.name }}(BaseModel):
    """{{ model.description }}"""
{%- for field in model.fields %}
    {{ field.name }}: {{ field.type }}{% if field.description %}  # {{ field.description }}{% endif %}
{%- endfor %}

'''

SERVER_RESPONSE_MODEL_TEMPLATE = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

{{ model.name }} レスポンスモデル定義
"""

from __future__ import annotations
{%- set imports = [] %}
{%- for field in model.fields %}
{%- if field.type is containing_model_reference %}
{%- set model_name = field.type | extract_model_name %}
{%- if model_name != model.name and model_name not in imports %}
{%- set _ = imports.append(model_name) %}
{%- endif %}
{%- endif %}
{%- endfor %}

from pydantic import BaseModel
{%- for import_model in imports %}
from ..requests.{{ import_model | lower }} import {{ import_model }}
{%- endfor %}


class {{ model.name }}(BaseModel):
    """{{ model.description }}"""
{%- for field in model.fields %}
    {{ field.name }}: {{ field.type }}{% if field.description %}  # {{ field.description }}{% endif %}
{%- endfor %}

'''

FLASK_REPOSITORY_DUMMY_TEMPLATE = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

{{ tag | title }}Repository ダミー実装（開発・テスト用）
"""

from __future__ import annotations
from typing import Any, Dict, List

from src.domain.{{ tag | lower }}_repository import {{ tag | title }}Repository

class {{ tag | title }}RepositoryDummy({{ tag | title }}Repository):
    """{{ tag }}リポジトリのダミー実装（開発・テスト用）"""

    def __init__(self):
        # ダミーデータ
        self._data: List[Dict[str, Any]] = [
            {"id": 1, "name": "サンプル{{ tag }}", "status": "active"},
            {"id": 2, "name": "テスト{{ tag }}", "status": "inactive"},
        ]
        self._next_id = 3

    def find_all(self) -> List[Dict[str, Any]]:
        """全て取得"""
        return self._data.copy()

    def find_by_id(self, id: Any) -> Dict[str, Any] | None:
        """IDで取得"""
        for item in self._data:
            if item.get("id") == id:
                return item.copy()
        return None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """作成"""
        new_item = data.copy()
        new_item["id"] = self._next_id
        self._next_id += 1
        self._data.append(new_item)
        return new_item

    def update(self, id: Any, data: Dict[str, Any]) -> Dict[str, Any] | None:
        """更新"""
        for i, item in enumerate(self._data):
            if item.get("id") == id:
                updated_item = {**item, **data}
                self._data[i] = updated_item
                return updated_item
        return None

    def delete(self, id: Any) -> bool:
        """削除"""
        for i, item in enumerate(self._data):
            if item.get("id") == id:
                del self._data[i]
                return True
        return False
'''

FLASK_README_TEMPLATE = '''# {{ project_name | default("API") }} Cloud Functions Flask App

このプロジェクトはOpenAPI仕様書から自動生成されたCloud Functions用Flaskアプリケーションです。

## 📁 プロジェクト構造

```
project/
├── main.py                    # 🔧 手動作成：Cloud Functions エントリポイント
├── src/
│   ├── domain/               # 🤖 自動生成：サービスインターフェース
│   │   ├── *.py
│   ├── repository/           # 🔧 手動作成：実際のリポジトリ実装
│   │   ├── *.py
│   ├── repository_dummy/     # 🤖 自動生成：ダミー実装（開発・テスト用）
│   │   ├── *.py
│   └── utils/               # 🤖 自動生成：共通ユーティリティ
│       └── logger.py
├── requirements.txt         # 🤖 自動生成
└── schemas.py              # 🤖 自動生成
```

## 🔧 手動で作成が必要なファイル

### 1. main.py（Cloud Functions エントリポイント）

```python
from src.domain.{{ (endpoints[0].tags[0] if endpoints and endpoints[0].tags else 'default') | lower }}_service import {{ (endpoints[0].tags[0] if endpoints and endpoints[0].tags else 'Default') | title }}Service
{%- set processed_tags = [] %}
{%- for endpoint in endpoints %}
{%- set tag = endpoint.tags[0] if endpoint.tags else 'default' %}
{%- if tag not in processed_tags %}
{%- set _ = processed_tags.append(tag) %}
from src.repository.{{ tag | lower }}_repository import {{ tag | title }}Repository
{%- endif %}
{%- endfor %}
from src.utils.logger import StructuredLogger

logger = StructuredLogger(__name__)

def set_cors_headers():
    """CORS用のヘッダーを設定"""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Max-Age": "3600",
    }
    return headers

def main(request):
    """Cloud Functions エントリーポイント"""
    headers = set_cors_headers()
    path = request.path
    method = request.method
    
    logger.info("request", path=path, method=method)
    
    if method == "OPTIONS":
        return ("", 204, headers)
    
    try:
        params = request.args.to_dict() if hasattr(request, 'args') else {}
        json_data = request.get_json() if hasattr(request, 'get_json') and request.is_json else None
        
        # 依存関係の注入（実際のリポジトリを使用）
{%- set processed_tags = [] %}
{%- for endpoint in endpoints %}
{%- set tag = endpoint.tags[0] if endpoint.tags else 'default' %}
{%- if tag not in processed_tags %}
{%- set _ = processed_tags.append(tag) %}
        {{ tag | lower }}_repository = {{ tag | title }}Repository()  # あなたの実装
        {{ tag | lower }}_service = {{ tag | title }}Service({{ tag | lower }}_repository)
{%- endif %}
{%- endfor %}
        
        # パスマッチング（必要に応じて修正）
        match path:
{%- for endpoint in endpoints %}
            case "{{ endpoint.path }}":
                if method == "{{ endpoint.method | upper }}":
                    # TODO: パラメータ抽出とサービス呼び出しを実装
                    response = {"message": "実装してください"}
                    return (response, 200, headers)
{%- endfor %}
            case _:
                return ({"error": "not found"}, 404, headers)
                
    except Exception as e:
        logger.error("Unexpected error", error_message=str(e))
        return ({"error": "Internal server error"}, 500, headers)
```

### 2. src/repository/*.py（実際のデータアクセス実装）

各サービスごとに実際のリポジトリを実装してください：

```python
# 例: src/repository/{{ (endpoints[0].tags[0] if endpoints and endpoints[0].tags else 'default') | lower }}_repository.py
from src.domain.{{ (endpoints[0].tags[0] if endpoints and endpoints[0].tags else 'default') | lower }}_repository import {{ (endpoints[0].tags[0] if endpoints and endpoints[0].tags else 'default') | title }}Repository

class {{ (endpoints[0].tags[0] if endpoints and endpoints[0].tags else 'Default') | title }}Repository({{ (endpoints[0].tags[0] if endpoints and endpoints[0].tags else 'default') | title }}Repository):
    """実際のデータアクセス実装"""
    
    def find_by_id(self, id):
        # Cloud Storage、Firestore、BigQuery等からデータを取得
        pass
    
    # その他のメソッドを実装...
```

## 🚀 開発・テスト用

開発中はダミー実装を使用できます：

```python
# main.py で
from src.repository_dummy.{{ (endpoints[0].tags[0] if endpoints and endpoints[0].tags else 'default') | lower }}_repository import {{ (endpoints[0].tags[0] if endpoints and endpoints[0].tags else 'Default') | title }}RepositoryDummy

# 実際のリポジトリの代わりにダミーを使用
{{ (endpoints[0].tags[0] if endpoints and endpoints[0].tags else 'default') | lower }}_repository = {{ (endpoints[0].tags[0] if endpoints and endpoints[0].tags else 'Default') | title }}RepositoryDummy()
```

## 📦 デプロイ

```bash
# Cloud Functionsにデプロイ
gcloud functions deploy your-function-name \\
  --runtime python39 \\
  --trigger-http \\
  --entry-point main
```

## 🛠️ 生成されたファイル

- **src/domain/**: サービスインターフェース（変更不要）
- **src/repository_dummy/**: ダミー実装（開発・テスト用）
- **src/utils/logger.py**: 構造化ログ（変更不要）
- **schemas.py**: データモデル（変更不要）
- **requirements.txt**: 依存関係（必要に応じて追加）
'''

FLASK_MODEL_TEMPLATE = '''"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

{{ model.name }} モデル定義
"""

from __future__ import annotations
{%- set imports = [] %}
{%- set needs_any = false %}
{%- for field in model.fields %}
{%- if "Any" in field.type %}
{%- set needs_any = true %}
{%- endif %}
{%- set field_type_clean = field.type.split('|')[0].strip() %}
{%- if field_type_clean.startswith('list[') %}
{%- set inner_type = field_type_clean[5:-1] %}
{%- if inner_type not in ['str', 'int', 'float', 'bool', 'Any'] and inner_type != model.name and inner_type not in imports %}
{%- set _ = imports.append(inner_type) %}
{%- endif %}
{%- elif field_type_clean not in ['str', 'int', 'float', 'bool', 'Any'] and field_type_clean != model.name and field_type_clean not in imports %}
{%- set _ = imports.append(field_type_clean) %}
{%- endif %}
{%- endfor %}

from pydantic import BaseModel
{%- if needs_any %}
from typing import Any
{%- endif %}
{%- for import_model in imports %}
{%- if "Response" in model.name or "Request" in model.name %}
from ..{{ import_model | lower }} import {{ import_model }}
{%- else %}
from .{{ import_model | lower }} import {{ import_model }}
{%- endif %}
{%- endfor %}

class {{ model.name }}(BaseModel):
    """{{ model.description }}"""
{%- for field in model.fields %}
    {{ field.name }}: {{ field.type }}{% if field.description %}  # {{ field.description }}{% endif %}
{%- endfor %}

'''
