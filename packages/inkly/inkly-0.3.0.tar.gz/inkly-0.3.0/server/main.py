"""
このファイルは自動生成されたファイルです。
直接編集しないでください。変更は元のOpenAPI仕様書で行ってください。

Flask アプリケーション エントリーポイント
"""

from __future__ import annotations

from app import app

def main(request):
    """Cloud Functions エントリーポイント
    
    Args:
        request: Flask Request オブジェクト
        
    Returns:
        Flask Response
    """
    with app.app_context():
        return app.full_dispatch_request()

# ローカル実行用
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)