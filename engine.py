import logging
from model import DatabaseMCP
from policy import PolicyMCP
from controller import AI_ControllerMCP
from view import ConsoleView

# --- 5. Game Engine (メインループ) ---
# MCP群を起動し、ゲームを進行する
class GameEngine:
    def __init__(self, api_key):
        self.model = DatabaseMCP()
        self.policy = PolicyMCP()
        self.controller = AI_ControllerMCP(self.model, self.policy, api_key)
        self.view = ConsoleView() # Viewをインスタンス化
        self.game_over = False

    def run_plan(self, plan):
        """Controllerが生成したプランを順番に実行する"""
        for step in plan:
            if self.game_over: break
            if "text" in step:
                self.view.show_message(step["text"]) # View経由で表示
            elif "mcp" in step:
                # この部分はAI Function Callingで自動化されたため、現在は未使用
                pass

    def show_current_state(self):
        """現在の状況を表示する"""
        if self.game_over: return

        scene_id = self.model._current_scene_id 
        scene = self.model.get_scene(scene_id)
        
        hp = self.model.get_data("player", "HP")
        items = self.model.get_data("player", "アイテム")
        active_enemies = self.model._enemies
        
        # Viewに状態を渡して表示
        self.view.show_game_state(scene, hp, items, active_enemies)

    def start(self):
        print("\n--- MCP分離型 TRPG: 起動シーケンス完了 ---")
        self.show_current_state()

        plan = self.controller.think("")
        self.run_plan(plan)
        
        if self.model._current_scene_id in ["end", "dead", "escape", "treasure"]:
            self.game_over = True

        if not self.game_over:
             self.show_current_state()

        while not self.game_over:
            try:
                user_input = self.view.get_user_input() # View経由で入力
                if user_input.lower() in ["exit", "quit"]:
                    break
                
                plan = self.controller.think(user_input)
                self.run_plan(plan)

                if self.model._current_scene_id in ["end", "dead", "escape", "treasure"]:
                    self.game_over = True

                if not self.game_over:
                    self.show_current_state()

            except (EOFError, KeyboardInterrupt):
                break
            except Exception as e:
                logging.error(f"[Engine Error]: メインループでエラー: {e}", exc_info=True)