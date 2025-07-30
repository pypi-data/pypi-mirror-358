# Contributing to Inkly

Inklyへのコントリビューションをありがとうございます！このドキュメントでは、プロジェクトへの貢献方法について説明します。

## 開発環境のセットアップ

### 前提条件
- Python 3.12以上
- Git

### セットアップ手順

1. リポジトリをクローン
```bash
git clone https://github.com/your-username/inkly.git
cd inkly
```

2. 開発依存関係をインストール
```bash
# PowerShell (Windows推奨)
.\tasks.ps1 install-dev

# または GNU Make (Linux/macOS)
make dev-install
```

3. 開発環境の確認
```bash
# テスト実行
.\tasks.ps1 test

# リンターチェック
.\tasks.ps1 lint

# 型チェック
.\tasks.ps1 type-check
```

## 開発ワークフロー

### ブランチ戦略
- `main`: 安定版
- `develop`: 開発版
- `feature/*`: 新機能開発
- `fix/*`: バグ修正

### コミットメッセージ
```
type(scope): description

例:
feat(generator): add response model auto-generation
fix(parser): handle nested $ref resolution
docs(readme): update installation instructions
```

### プルリクエスト
1. フィーチャーブランチを作成
2. 変更を実装
3. テストを追加/更新
4. コード品質チェックを実行
5. プルリクエストを作成

## コード品質

### 必須チェック
```bash
# 全品質チェック実行
.\tasks.ps1 check

# または個別実行
.\tasks.ps1 format-check  # フォーマットチェック
.\tasks.ps1 lint         # リンターチェック
.\tasks.ps1 type-check   # 型チェック
.\tasks.ps1 test         # テスト実行
```

### コーディング規約
- Python 3.12+の現代的な記法を使用
- 型ヒントを必須とする
- docstringを必須とする
- ruffの設定に従う

## テスト

### テスト実行
```bash
# 全テスト実行
.\tasks.ps1 test

# 高速テスト（型チェックなし）
.\tasks.ps1 test-fast

# カバレッジ付きテスト
.\tasks.ps1 test-all
```

### テスト作成
- `tests/`ディレクトリに配置
- pytest形式で作成
- 新機能には必ずテストを追加

## リリース

### バージョニング
セマンティックバージョニングに従う：
- MAJOR: 破壊的変更
- MINOR: 新機能追加
- PATCH: バグ修正

### リリース手順
1. バージョン更新
2. CHANGELOG.md更新
3. テスト実行
4. タグ作成
5. PyPI公開

## 問題報告

### バグ報告
以下の情報を含めてください：
- Python バージョン
- OS情報
- 再現手順
- 期待される動作
- 実際の動作
- エラーメッセージ

### 機能要求
以下の情報を含めてください：
- 機能の説明
- 使用例
- 期待される動作
- 代替案

## コミュニティ

- GitHub Issues: バグ報告・機能要求
- GitHub Discussions: 質問・議論
- Pull Requests: コード貢献

## ライセンス

このプロジェクトにコントリビュートすることで、あなたの貢献がプロジェクトのライセンス下で公開されることに同意したものとみなします。 
