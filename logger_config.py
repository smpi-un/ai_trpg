import logging
import os

def setup_logging():
    """
    環境変数 LOG_LEVEL に基づいてロギングを設定する。
    デフォルトは INFO レベル。
    """
    # 環境変数からログレベルを取得。指定がなければ 'INFO' を使用
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    # ルートロガーの基本設定
    logging.basicConfig(
        level=log_level,
        # ログのフォーマットを定義
        format='%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # ライブラリ（例: google-generativeai）のログが多すぎないように、
    # INFOレベル以上のものだけ表示する設定（デバッグモードではDEBUGも表示）
    if log_level == 'INFO':
        logging.getLogger("google.generativeai").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.INFO)

    logging.debug(f"ロギングレベルが '{log_level}' に設定されました")
