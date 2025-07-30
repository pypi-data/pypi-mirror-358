"""FastAPIサーバーコードジェネレータ"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .base import CodeGenerationError, CodeGenerator
from .templates import (
    FLASK_ENUM_TEMPLATE,
    SERVER_DEPENDENCIES_TEMPLATE,
    SERVER_INTERFACES_TEMPLATE,
    SERVER_MAIN_TEMPLATE,
    SERVER_REQUEST_MODEL_TEMPLATE,
    SERVER_RESPONSE_MODEL_TEMPLATE,
    SERVER_ROUTE_TEMPLATE,
)

logger = logging.getLogger(__name__)


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
            "enum.py": FLASK_ENUM_TEMPLATE,
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

        logger.info("FastAPIサーバ生成完了: %s", output_dir)
