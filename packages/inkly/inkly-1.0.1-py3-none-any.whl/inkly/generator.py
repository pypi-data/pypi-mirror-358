"""コードジェネレータモジュール

旧バージョンとの互換性のため維持されています。
新しい実装は generators パッケージを参照してください。
"""

# 後方互換性のために既存のインポートを維持
from .generators import (
    ClientGenerator,
    CodeGenerationError,
    CodeGenerator,
    FlaskServerGenerator,
    ServerGenerator,
)

__all__ = [
    "CodeGenerationError",
    "CodeGenerator",
    "ClientGenerator",
    "ServerGenerator",
    "FlaskServerGenerator",
]
