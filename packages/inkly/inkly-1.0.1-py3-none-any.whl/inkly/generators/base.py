"""コードジェネレータ基底クラス"""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from jinja2 import DictLoader, Environment


class CodeGenerationError(Exception):
    """コード生成エラー"""


class CodeGenerator(ABC):
    """コードジェネレータ基底クラス"""

    def __init__(self, parser: Any) -> None:
        self.parser = parser

        # Jinja2環境を設定
        self.env = Environment(
            loader=DictLoader(self.get_templates()),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # フィルタ追加
        def _python_type_filter(value: Any) -> str:
            return self.python_type_from_openapi(value)

        def _lower_filter(value: Any) -> str:
            return str(value).lower()

        def _replace_filter(value: Any, old: Any, new: Any) -> str:
            return str(value).replace(str(old), str(new))

        def _camel_to_snake_filter(value: Any) -> str:
            return self.camel_to_snake(str(value))

        def _to_pascal_case_filter(value: Any) -> str:
            snake_case = self.camel_to_snake(str(value))
            parts = snake_case.replace("-", "_").split("_")
            return "".join(word.capitalize() for word in parts)

        # 型情報をチェックするフィルタ
        def _containing_model_reference_filter(value: Any) -> bool:
            """型がモデル参照を含んでいるかチェック"""
            type_str = str(value)
            # モデル名のパターンをチェック(大文字で始まる単語)
            import re

            # 最初に見つかった大文字で始まる単語を返す(Noneは除外)
            match = re.search(r"\b([A-Z][a-zA-Z0-9]*)\b", type_str)
            model_name = match.group(1) if match else ""
            return bool(model_name and model_name != "None")

        def _extract_model_name_filter(value: Any) -> str:
            """型文字列からモデル名を抽出"""
            import re

            # 最初に見つかった大文字で始まる単語を返す(Noneは除外)
            match = re.search(r"\b([A-Z][a-zA-Z0-9]*)\b", str(value))
            model_name = match.group(1) if match else ""
            return model_name if model_name != "None" else ""

        def _get_return_type_filter(responses: dict[str, Any]) -> str:
            """レスポンス情報から戻り値の型を決定する"""
            # 200番台のレスポンスを探す
            success_response = None
            for status_code, response in responses.items():
                if str(status_code).startswith("2"):  # 2xx success
                    success_response = response
                    break

            if not success_response:
                return "None"

            content = success_response.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema", {})

            if not schema:
                return "None"

            # $ref参照を解決
            if "$ref" in schema:
                ref_path = schema["$ref"]
                if ref_path.startswith("#/components/schemas/"):
                    schema_name = ref_path.split("/")[-1]
                    return schema_name

            # 配列の場合
            if schema.get("type") == "array":
                items = schema.get("items", {})
                if "$ref" in items:
                    ref_path = items["$ref"]
                    if ref_path.startswith("#/components/schemas/"):
                        schema_name = ref_path.split("/")[-1]
                        return f"list[{schema_name}]"

            # プリミティブ型の場合
            if schema.get("type") in ["string", "integer", "boolean", "number"]:
                python_type = self.python_type_from_openapi(schema)
                return python_type

            return "dict[str, Any]"

        self.env.filters["python_type"] = _python_type_filter
        self.env.filters["lower"] = _lower_filter
        self.env.filters["replace"] = _replace_filter
        self.env.filters["camel_to_snake"] = _camel_to_snake_filter
        self.env.filters["to_pascal_case"] = _to_pascal_case_filter
        self.env.filters["containing_model_reference"] = (
            _containing_model_reference_filter
        )
        self.env.filters["extract_model_name"] = _extract_model_name_filter
        self.env.filters["get_return_type"] = _get_return_type_filter

    @abstractmethod
    def get_templates(self) -> dict[str, str]:
        """テンプレートを返す(サブクラスで実装)

        Returns:
            テンプレート辞書
        """

    @abstractmethod
    def generate_to_path(self, output_path: str | Path, **kwargs: Any) -> None:
        """指定されたパスにコードを生成する(サブクラスで実装)

        Args:
            output_path: 出力パス
            **kwargs: その他のオプション
        """

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
        # 連続する大文字（例：XMLParser）も適切に処理
        s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', camel_str)
        # 小文字+数字の後に大文字（例：version2A → version2_A）
        s2 = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s1)
        return s2.lower()

    def python_type_from_openapi(
        self, schema: dict[str, Any] | None, field_name: str = ""
    ) -> str:
        """OpenAPI スキーマから Python 型を生成する

        Args:
            schema: OpenAPIスキーマ辞書
            field_name: フィールド名（enum名生成用）

        Returns:
            Python型文字列
        """
        if not schema:
            return "Any"

        if "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            return ref_name

        # enumがある場合は、専用のEnumクラス名を返す
        if "enum" in schema:
            # フィールド名からEnum名を生成
            if field_name:
                # snake_case から PascalCase に変換
                enum_name = "".join(word.capitalize() for word in field_name.split("_"))
                return f"{enum_name}Enum"
            else:
                return "GeneratedEnum"

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

    def _get_basic_type(self, schema_type: str) -> str:
        """基本型をPython型に変換する

        Args:
            schema_type: OpenAPI型

        Returns:
            Python型文字列
        """
        match schema_type:
            case "string":
                return "str"
            case "integer":
                return "int"
            case "number":
                return "float"
            case "boolean":
                return "bool"
            case _:
                return "Any"
