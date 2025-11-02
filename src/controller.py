import logging
import google.generativeai as genai
from model import MCP
from policy import Policy, Constitution
from gamebook import GameBook

# --- 3. Controller (AI MCP) ---
# AI (Gemini) を使って思考するController。
class AI_ControllerMCP:
    """
    [Controller]
    本物のAI (Gemini) を使って思考するController。
    """
    def __init__(self, model_mcp: MCP, api_key: str):
        logging.debug("[MCP Init: AI Controller (Gemini) が起動しました]")
        self.model = model_mcp
        self.policy = Policy()
        self.constitution = Constitution()
        self.gamebook = GameBook()
        genai.configure(api_key=api_key)

        self.tools = [
            self.model.get_data,
            self.model.update_data,
            self.model.get_scene_id,
            self.model.set_current_scene,
            self.model.manage_enemy,
            self.model.manage_item,
            self.policy.roll_dice,
            self.policy.calculate_damage,
        ]
        
        self.ai_model = genai.GenerativeModel(
            model_name='gemini-flash-latest',
            tools=self.tools,
        )

        self.chat_session = self.ai_model.start_chat(
            enable_automatic_function_calling=True
        )

    def create_character(self) -> str:
        """
        ゲーム開始時にプレイヤーのキャラクターを作成する。
        """
        logging.debug("[Controller (Character Creation)]: キャラクター作成を開始します]")
        prompt = """
        あなたはゲームマスターです。プレイヤーの分身となるキャラクターを作成してください。
        キャラクターの能力値は「腕力」「知力」「器用」の３つです。
        
        思考プロセス：
        1. まず、プレイヤーにキャラクター作成が開始されることを伝えます。
        2. 次に、能力値「腕力」のために `roll_dice(1, 6)` を呼び出します。
        3. `update_data("player", '["能力", "腕力"]', f'{roll_diceの結果}')` を呼び出して、能力値を設定します。キーと値はJSON文字列である必要があることに注意してください。
        4. 「知力」「器用」についても同様に、ダイスロールと能力値設定を繰り返します。
        5. 最後に、決定した全ての能力値をプレイヤーに分かりやすく提示し、物語の導入を開始するよう促してください。
        """
        try:
            response = self.chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            logging.error(f"[Controller Error]: キャラクター作成中にエラー: {e}", exc_info=True)
            return "キャラクター作成中にエラーが発生しました。"

    def think(self, user_input: str) -> str:
        """
        [Controller]
        AI(GM)の思考プロセス。
        L1, L2, L3の情報を統合してプロンプトを生成し、AIに送信する。
        """
        logging.debug(f"[Controller (Thinking): ユーザー入力 '{user_input}' を受け付けました]")

        # L2: MCPから現在の状態を取得
        mcp_state = {
            '_current_scene_id': self.model.get_scene_id(),
            '_player': self.model.get_data("player"),
            '_enemies': self.model.get_data("enemies")
        }

        # L3: ゲームブックからルールと関連情報を取得
        rules = self.gamebook.get_rules()
        scene_id = mcp_state['_current_scene_id']
        
        gamebook_snippets = []
        # 現在のシーンの情報を最優先で取得
        current_scene_text = self.gamebook.get_scene_by_id(scene_id)
        if current_scene_text:
            gamebook_snippets.append(f"現在のシーン「{scene_id}」の情報:\n{current_scene_text}")

        # ユーザーの入力に基づいて補助的な情報を検索
        if user_input:
            search_results = self.gamebook.search(user_input)
            if search_results:
                gamebook_snippets.append(f"入力「{user_input}」に関連する可能性のある情報:\n" + "\n".join(search_results))

        # L1: 憲法に基づいてプロンプトを生成
        prompt = self.constitution.generate_prompt(
            rules=rules,
            gamebook_snippets=gamebook_snippets,
            mcp_state=mcp_state,
            player_input=user_input
        )

        logging.debug(f"[Controller (Generated Prompt)]: {prompt}")

        try:
            response = self.chat_session.send_message(prompt)
            try:
                final_text = response.text
            except ValueError:
                final_text = "（AIは行動しましたが、何も言わなかったようです。もう一度行動を指示してください。）"
                logging.warning("[Controller Warning]: AI response did not contain a text part.")
            
            logging.debug(f"[Controller (AI Response)]: {final_text}")
            return final_text
        except Exception as e:
            logging.error(f"[Controller Error]: AIの思考中にエラー: {e}", exc_info=True)
            return "（AIが混乱しているようだ...）"