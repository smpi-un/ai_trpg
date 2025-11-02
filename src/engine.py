import logging
from model import MCP
from controller import AI_ControllerMCP
from view import ConsoleView

class GameEngine:
    def __init__(self, api_key: str):
        self.model = MCP()
        self.controller = AI_ControllerMCP(self.model, api_key)
        self.view = ConsoleView()
        self.game_over = False

    def start(self):
        self.view.show_message("\n--- TRPGゲームへようこそ ---")
        
        # Character Creation
        creation_message = self.controller.create_character()
        self.view.show_message(creation_message)

        # Initial message from AI
        ai_response = self.controller.think("キャラクター作成が完了しました。ゲームを開始してください。最初の状況を描写してください。")
        self.view.show_message(ai_response)

        while not self.game_over:
            try:
                # Show player status
                player_hp = self.model.get_data("player", "HP")
                player_items = self.model.get_data("player", "アイテム")
                self.view.show_message(f"\n《あなた: HP={player_hp}, アイテム={player_items}》")

                # Get player input
                user_input = self.view.get_user_input()
                if user_input.lower() in ["exit", "quit"]:
                    self.view.show_message("ゲームを終了します。")
                    break

                # Get AI response
                ai_response = self.controller.think(user_input)
                self.view.show_message(ai_response)

                # Check for game over conditions (the AI should set the scene_id via function call)
                current_scene = self.model.get_scene_id()
                if current_scene in ["end", "dead", "escape", "treasure"]:
                    self.view.show_message("--- ゲーム終了 ---")
                    self.game_over = True

            except (EOFError, KeyboardInterrupt):
                self.view.show_message("\nゲームを中断します。")
                break
            except Exception as e:
                logging.error(f"[Engine Error]: メインループでエラー: {e}", exc_info=True)
                self.view.show_message("エラーが発生しました。詳細はログを確認してください。")
                break
