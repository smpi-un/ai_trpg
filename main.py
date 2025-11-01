import logging
import os
from engine import GameEngine
from logger_config import setup_logging

# --- 実行 ---
if __name__ == "__main__":
    # ロギングを設定
    setup_logging()

    # 環境変数からAPIキーを取得
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        logging.error("エラー: 環境変数 'GOOGLE_API_KEY' が設定されていません。")
        logging.error("シェルの設定ファイル（.bashrc や .zshrc など）に export GOOGLE_API_KEY='あなたのAPIキー' を追加してください。")
        exit(1) 
    
    logging.info("--- TRPGゲームを開始します ---")
    try:
        engine = GameEngine(api_key)
        engine.start()
    except ImportError as e:
        logging.error(f"エラー: 必要なモジュールが見つかりません。({e})")
        logging.error("pip install -r requirements.txt を実行して、ライブラリをインストールしてください。")
    except Exception as e:
        logging.error(f"ゲームの起動に失敗しました: {e}", exc_info=True)
    finally:
        logging.info("--- ゲーム終了 ---")