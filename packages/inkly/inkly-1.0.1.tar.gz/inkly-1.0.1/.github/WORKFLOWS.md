# GitHub Actions Workflows

このプロジェクトには2つの自動リリースワークフローが設定されています。

## ワークフロー概要

### 1. TestPyPI Release
- **ファイル**: `.github/workflows/testpypi-release.yml`
- **トリガー**: `main`ブランチへのpush
- **動作**: TestPyPIに自動リリース

### 2. PyPI Release  
- **ファイル**: `.github/workflows/pypi-release.yml`
- **トリガー**: `v*.*.*`形式のタグ作成
- **動作**: GitHub ReleaseとPyPIに自動リリース

## 必要なSecrets設定

以下のSecretsをGitHubリポジトリに設定してください：

- `TEST_PYPI_API_TOKEN`: TestPyPIのAPIトークン
- `PYPI_API_TOKEN`: PyPIのAPIトークン

## 使用方法

### TestPyPIリリース
```bash
git push origin main  # mainにpushすると自動リリース
```

### 本番リリース
```bash
git tag v1.0.0        # バージョンタグを作成
git push origin v1.0.0  # タグをpushすると自動リリース
``` 
