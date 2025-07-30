"""Inkly CLI インターフェース"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click
import uvicorn
from rich.console import Console
from rich.logging import RichHandler

from .generator import (
    ClientGenerator,
    CodeGenerationError,
    FlaskServerGenerator,
    ServerGenerator,
)
from .parser import OpenAPIParseError, OpenAPIParser
from .serve import MockServer

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)

console = Console()
logger = logging.getLogger(__name__)


@click.version_option(version="0.1.0")
@click.group()
@click.option("--verbose", "-v", is_flag=True, help="詳細なログを表示")
def main(verbose: bool) -> None:
    """Inkly - OpenAPI クライアント & サーバコードジェネレータ

    OpenAPI 仕様書から Python クライアントおよびサーバのコードを自動生成します。
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("詳細ログモードが有効になりました")


@main.command()
@click.option(
    "--input",
    "-i",
    "input_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="OpenAPI 定義ファイル（.yaml/.json）",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    required=True,
    type=click.Path(path_type=Path),
    help="出力先ディレクトリ",
)
@click.option("--use-async", is_flag=True, help="非同期クライアントを生成する")
@click.option("--flat-structure", is_flag=True, help="単一ファイルに出力する")
def generate(
    input_file: Path, output_dir: Path, use_async: bool, flat_structure: bool
) -> None:
    """OpenAPI 定義からクライアントコードを生成する"""

    try:
        console.print(
            f"[bold blue]OpenAPI 仕様書を読み込み中: {input_file}[/bold blue]"
        )

        # パーサー初期化
        parser = OpenAPIParser(input_file)
        parser.parse()

        console.print("[green]✓[/green] OpenAPI 仕様書の読み込み完了")

        # ジェネレータ初期化
        generator = ClientGenerator(parser)

        console.print("[bold blue]クライアントコードを生成中...[/bold blue]")

        # コード生成
        generator.generate_to_path(
            output_dir, use_async=use_async, flat_structure=flat_structure
        )

        console.print(f"[green]✓[/green] クライアントコードの生成完了: {output_dir}")

        # 生成されたファイルの一覧表示
        if output_dir.exists():
            console.print("\n[bold]生成されたファイル:[/bold]")
            for file in output_dir.rglob("*.py"):
                console.print(f"  📄 {file.relative_to(output_dir)}")

    except OpenAPIParseError as e:
        console.print(f"[red]❌ OpenAPI パースエラー: {e}[/red]")
        logger.error("OpenAPI パースに失敗しました", exc_info=True)
        sys.exit(1)
    except CodeGenerationError as e:
        console.print(f"[red]❌ コード生成エラー: {e}[/red]")
        logger.error("コード生成に失敗しました", exc_info=True)
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ 予期しないエラー: {e}[/red]")
        logger.error("予期しないエラーが発生しました", exc_info=True)
        sys.exit(1)


@main.command()
@click.option(
    "--input",
    "-i",
    "input_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="OpenAPI 定義ファイル（.yaml/.json）",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    required=True,
    type=click.Path(path_type=Path),
    help="出力先ディレクトリ",
)
@click.option("--mock-response", is_flag=True, help="モックレスポンスを有効にする")
@click.option(
    "--framework",
    "-f",
    type=click.Choice(["fastapi", "flask"], case_sensitive=False),
    default="fastapi",
    help="サーバフレームワーク（デフォルト: fastapi）",
)
def generate_server(
    input_file: Path, output_dir: Path, mock_response: bool, framework: str
) -> None:
    """OpenAPI 定義からサーバコードを生成する"""

    try:
        console.print(
            f"[bold blue]OpenAPI 仕様書を読み込み中: {input_file}[/bold blue]"
        )

        # パーサー初期化
        parser = OpenAPIParser(input_file)
        parser.parse()

        console.print("[green]✓[/green] OpenAPI 仕様書の読み込み完了")

        # ジェネレータ初期化
        if framework.lower() == "flask":
            generator = FlaskServerGenerator(parser)
        else:
            generator = ServerGenerator(parser)

        console.print(
            f"[bold blue]{framework.upper()}サーバコードを生成中...[/bold blue]"
        )

        # コード生成
        generator.generate_to_path(output_dir, mock_response=mock_response)

        console.print(f"[green]✓[/green] サーバコードの生成完了: {output_dir}")

        # 生成されたファイルの一覧表示
        if output_dir.exists():
            console.print("\n[bold]生成されたファイル:[/bold]")
            for file in output_dir.rglob("*.py"):
                console.print(f"  📄 {file.relative_to(output_dir)}")

        console.print("\n[bold green]サーバを起動するには:[/bold green]")
        console.print(f"  cd {output_dir}")
        console.print("  python main.py")

    except OpenAPIParseError as e:
        console.print(f"[red]❌ OpenAPI パースエラー: {e}[/red]")
        logger.error("OpenAPI パースに失敗しました", exc_info=True)
        sys.exit(1)
    except CodeGenerationError as e:
        console.print(f"[red]❌ コード生成エラー: {e}[/red]")
        logger.error("コード生成に失敗しました", exc_info=True)
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ 予期しないエラー: {e}[/red]")
        logger.error("予期しないエラーが発生しました", exc_info=True)
        sys.exit(1)


@main.command()
@click.option(
    "--input",
    "-i",
    "input_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="OpenAPI 定義ファイル（.yaml/.json）",
)
@click.option("--host", default="0.0.0.0", help="サーバホスト（デフォルト: 0.0.0.0）")
@click.option("--port", default=8000, type=int, help="サーバポート（デフォルト: 8000）")
@click.option("--mock", is_flag=True, help="モックレスポンスを有効にする")
@click.option(
    "--reload", is_flag=True, help="ファイル変更時の自動リロードを有効にする（開発用）"
)
def serve(input_file: Path, host: str, port: int, mock: bool, reload: bool) -> None:
    """OpenAPI 定義から直接モックサーバを起動する"""

    try:
        console.print(
            f"[bold blue]OpenAPI 仕様書を読み込み中: {input_file}[/bold blue]"
        )

        # パーサー初期化
        parser = OpenAPIParser(input_file)
        parser.parse()

        console.print("[green]✓[/green] OpenAPI 仕様書の読み込み完了")
        console.print("[bold blue]モックサーバを起動中...[/bold blue]")

        # モックサーバ作成
        mock_server = MockServer(parser, enable_mock=mock)
        app = mock_server.create_app()

        console.print("[green]✓[/green] サーバが起動しました")
        console.print(f"[bold]URL: http://{host}:{port}[/bold]")
        console.print(f"[bold]API ドキュメント: http://{host}:{port}/docs[/bold]")

        if not mock:
            console.print(
                "[yellow]⚠️[/yellow] モックレスポンスが無効です。--mock フラグを使用してください"
            )

        # サーバ起動
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info" if not reload else "debug",
        )

    except OpenAPIParseError as e:
        console.print(f"[red]❌ OpenAPI パースエラー: {e}[/red]")
        logger.error("OpenAPI パースに失敗しました", exc_info=True)
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ 予期しないエラー: {e}[/red]")
        logger.error("予期しないエラーが発生しました", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
