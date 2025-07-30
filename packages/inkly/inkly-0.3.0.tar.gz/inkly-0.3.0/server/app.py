"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

Flask アプリケーション
"""

from __future__ import annotations

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORS設定

# ルートのインポート
from routes.pets import bp as pets_bp
from routes.users import bp as users_bp

# ブループリントの登録
app.register_blueprint(pets_bp, url_prefix="/api")
app.register_blueprint(users_bp, url_prefix="/api")

@app.route("/")
def health_check():
    """ヘルスチェック"""
    return jsonify({"status": "ok", "message": "Flask API Server is running"})

@app.route("/health")
def health():
    """ヘルスチェック"""
    return jsonify({"status": "healthy"})

@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラ"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """500エラーハンドラ"""
    return jsonify({"error": "Internal server error"}), 500