"""Inkly - OpenAPI クライアント & サーバコードジェネレータ

OpenAPI 仕様書から型安全な Python クライアントおよび FastAPI サーバコードを自動生成します。
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Inkly Team"
__email__ = "info@inkly.dev"

# Core modules
from .generator import (
    ClientGenerator,
    CodeGenerationError,
    CodeGenerator,
    ServerGenerator,
)
from .parser import OpenAPIParseError, OpenAPIParser, OpenAPISchema
from .serve import MockServer, MockServerError

__all__ = [
    # Version info
    "__author__",
    "__email__",
    "__version__",
    # Generators
    "ClientGenerator",
    "CodeGenerationError",
    "CodeGenerator",
    # Server
    "MockServer",
    "MockServerError",
    # Parser
    "OpenAPIParseError",
    "OpenAPIParser",
    "OpenAPISchema",
    "ServerGenerator",
]
