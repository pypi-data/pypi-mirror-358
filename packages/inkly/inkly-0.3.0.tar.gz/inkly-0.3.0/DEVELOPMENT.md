# Development Guide

このドキュメントでは、Inklyの内部構造と開発に関する詳細な情報を提供します。

## アーキテクチャ

### 全体構成
```
inkly/
├── __init__.py          # パッケージエントリーポイント
├── parser.py            # OpenAPI仕様書パーサー
├── generator.py         # コード生成エンジン
├── cli.py              # CLIインターフェース
└── serve.py            # モックサーバー
```

### データフロー
1. **Parse**: OpenAPI仕様書 → 内部データ構造
2. **Generate**: 内部データ構造 → Pythonコード
3. **Output**: ファイルシステムへの出力

## 主要コンポーネント

### 1. Parser (parser.py)

#### OpenAPIParser
OpenAPI仕様書を解析し、内部データ構造に変換します。

```python
parser = OpenAPIParser("path/to/openapi.yaml")
endpoints = parser.get_endpoints()
schemas = parser.get_schemas()
```

**主要機能:**
- YAML/JSON形式のOpenAPI仕様書読み込み
- $ref参照の解決
- エンドポイント情報の抽出
- スキーマ定義の抽出

### 2. Generator (generator.py)

#### ClientGenerator
型安全なPythonクライアントコードを生成します。

```python
generator = ClientGenerator(parser)
code = generator.generate_client(
    use_async=True,
    flat_structure=False
)
```

**生成される構造:**
```
client/
├── __init__.py
├── client.py           # メインクライアントクラス
├── models/             # Pydanticモデル
│   ├── __init__.py
│   ├── pet.py
│   └── user.py
└── endpoints/          # エンドポイント実装
    ├── pets.py
    └── users.py
```

#### ServerGenerator
FastAPIベースのサーバースキャフォールドを生成します。

```python
generator = ServerGenerator(parser)
generator.generate_server(
    output_dir="server",
    mock_response=True
)
```

**生成される構造:**
```
server/
├── main.py             # FastAPIアプリケーション
├── dependencies.py     # 共通依存関係
├── interfaces.py       # ビジネスロジックインターフェース
├── implementations.py  # インターフェース実装
├── routes/             # APIルート
│   ├── pets.py
│   └── users.py
└── models/             # データモデル
    ├── requests/       # リクエストモデル
    └── responses/      # レスポンスモデル
```

### 3. CLI (cli.py)

#### コマンド
- `generate`: クライアントコード生成
- `generate-server`: サーバーコード生成
- `serve`: モックサーバー起動

#### 使用例
```bash
# クライアント生成
inkly generate examples/petstore.yaml client/ --use-async

# サーバー生成
inkly generate-server examples/petstore.yaml server/ --mock-response

# モックサーバー起動
inkly serve examples/petstore.yaml --port 8080
```

### 4. MockServer (serve.py)

動的にFastAPIアプリケーションを構築し、OpenAPI仕様に基づいてモックレスポンスを返します。

## テンプレートシステム

### Jinja2テンプレート
コード生成にはJinja2テンプレートエンジンを使用します。

#### カスタムフィルター
- `python_type_from_openapi`: OpenAPI型 → Python型変換
- `to_snake_case`: キャメルケース → スネークケース変換
- `to_camel_case`: スネークケース → キャメルケース変換

#### テンプレート分離
- 同期/非同期クライアント用に別々のテンプレート
- 保守性とコードの明確性を向上

## 型システム

### Python 3.12+対応
- `from __future__ import annotations`使用
- 現代的な型アノテーション（`dict[str, Any]`等）
- Union型の代わりに`|`演算子使用

### 型安全性
- 全ての関数に型ヒント必須
- pyrightによる厳密な型チェック
- Pydanticによる実行時型検証

## エラーハンドリング

### カスタム例外
```python
class OpenAPIParseError(Exception): ...
class CodeGenerationError(Exception): ...
class MockServerError(Exception): ...
```

### ログシステム
- 構造化ログ（logging + rich）
- レベル別ログ出力
- 美しいコンソール出力

## テスト戦略

### テスト構成
```
tests/
├── __init__.py
├── test_parser.py      # パーサーテスト
├── test_generator.py   # ジェネレーターテスト
├── test_cli.py         # CLIテスト
└── fixtures/           # テスト用データ
```

### テスト実行
```bash
# 全テスト実行
pytest

# カバレッジ付き
pytest --cov=inkly

# 特定テスト実行
pytest tests/test_parser.py::test_parse_openapi_yaml
```

## Flask版サーバー生成

### 実装方針
FastAPI版と同様の構造で、Flaskベースのサーバーコードを生成します。

```bash
# Flask版サーバー生成
inkly generate-server examples/petstore.yaml server/ --framework flask
```

### 生成される構造
```
server/
├── app.py              # Flaskアプリケーション
├── blueprints/         # Blueprintベースルート
├── models/             # データモデル
└── utils.py            # ユーティリティ
```

## パフォーマンス最適化

### 並列処理
- ファイル生成の並列化
- 大きなOpenAPI仕様書の効率的処理

### メモリ効率
- ストリーミング処理
- 大きなファイルの分割生成

## デバッグ

### ログレベル設定
```python
import logging
logging.getLogger('inkly').setLevel(logging.DEBUG)
```

### デバッグ出力
```bash
# 詳細ログ付きで実行
RUNIC_DEBUG=1 inkly generate examples/petstore.yaml client/
```

## 拡張性

### プラグインシステム
将来的には以下の拡張を予定：
- カスタムジェネレータープラグイン
- 追加フレームワーク対応
- カスタムテンプレート

### API設計
- 明確なインターフェース分離
- 拡張可能なアーキテクチャ
- プラグイン対応の準備

## ベストプラクティス

### コード生成
1. テンプレートの分離
2. 型安全性の確保
3. エラーハンドリングの徹底
4. テストカバレッジの維持

### 保守性
1. 明確な責任分離
2. 適切な抽象化レベル
3. 包括的なドキュメント
4. 継続的なリファクタリング 
