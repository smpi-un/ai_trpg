import logging
import google.generativeai as genai

# --- 3. Controller (AI MCP) ---
# AI (Gemini) を使って思考するController。
class AI_ControllerMCP:
    """
    [Controller]
    本物のAI (Gemini) を使って思考するController。
    """
    def __init__(self, model_mcp, policy_mcp, api_key):
        logging.debug("[MCP Init: AI Controller (Gemini) が起動しました]")
        self.model = model_mcp
        self.policy = policy_mcp
        genai.configure(api_key=api_key)

        self.tools = [
            self.model.get_data, self.model.update_data, self.model.get_scene,
            self.model.set_current_scene, self.model.manage_enemy, self.model.manage_item,
            self.policy.roll_dice, self.policy.calculate_damage,
        ]
        
        self.ai_model = genai.GenerativeModel(
            model_name='gemini-flash-latest',
            tools=self.tools,
        )

        self.chat_session = self.ai_model.start_chat(
            enable_automatic_function_calling=True
        )

    def think(self, user_input):
        """
        [Controller]
        AI(GM)の思考プロセス。
        """
        logging.debug(f"[Controller (Thinking): ユーザー入力 '{user_input}' をAIに送信します]")
        scene_id = self.model.get_data("player", "現在地") or self.model._current_scene_id
        current_scene = self.model.get_scene(scene_id)
        player_hp = self.model.get_data("player", "HP")

        prompt = f"""
        あなたはTRPGのゲームマスターです。
        [現在の状況]
        シーン: {scene_id} ({current_scene['text']})
        プレイヤーHP: {player_hp}
        [ユーザーの行動]
        {user_input}
        上記に基づき、適切なツール（MCP）を呼び出してゲームを進行してください。
        実行後、プレイヤーへの応答メッセージを生成してください。
        """
        try:
            response = self.chat_session.send_message(prompt)
            final_text = response.text
            logging.debug(f"[Controller (AI Response)]: {final_text}")
            return [{"text": final_text}]
        except Exception as e:
            logging.error(f"[Controller Error]: AIの思考中にエラー: {e}", exc_info=True)
            return [{"text": "（AIが混乱しているようだ...）"}]