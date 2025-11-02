import random
from typing import Dict, Any, List

# --- 2. Policy (ルール・判定) ---
# ゲームのルール（サイコロ、ダメージ計算など）を管理する。
class Policy:
    """
    [Policy]
    ゲームのルール（サイコロ、ダメージ計算など）を管理する。
    AIが直接呼び出すツール（関数）を提供する。
    """
    def roll_dice(self, num_dice: int, num_sides: int) -> int:
        """指定された数と面のサイコロを振り、合計値を返す"""
        try:
            num_dice = int(num_dice)
            num_sides = int(num_sides)
        except (ValueError, TypeError):
            return 0 # Or raise an error, but returning 0 is safer
        return sum(random.randint(1, num_sides) for _ in range(num_dice))

    def calculate_damage(self, attack_power: int, defense_power: int) -> int:
        """攻撃力と防御力からダメージを計算する"""
        damage = attack_power - defense_power
        return max(0, damage)

class Constitution:
    """
    AIの行動原理（憲法/L1）を定義し、プロンプトを生成するクラス。
    """

    _BASE_CONSTITUTION = """
# あなたへの指示 (憲法)
あなたは、TRPGの熟練ゲームマスター(GM)です。
あなたの使命は、プレイヤーを楽しませ、物語を円滑に進行させることです。

## 基本的な行動指針
{rules}

## メタ・ルール（最重要）
あなたは応答を生成する前に、必ず以下の情報を参照し、従わなければなりません。

1.  **ゲームブック（長期記憶）**: シナリオの描写、ルール、NPCのセリフなどは、必ずこの情報に基づいてください。勝手に創作してはいけません。
2.  **現在のゲーム状態（短期記憶）**: 現在の場所、時間、プレイヤーの状態などを正確に把握し、矛盾のない応答をしてください。
3.  **プレイヤーの行動**: プレイヤーが何をしたのかを理解し、それに対する結果を描写してください。

## 思考と行動のプロセス
1. 上記の[ゲームブック]、[現在のゲーム状態]、[プレイヤーの行動]をよく読んで状況を理解します。
2. 次に何をすべきかを判断します。状況を描写すべきか、NPCとして話すべきか、戦闘を処理すべきか、などです。特に、プレイヤーが扉や箱など、状態を持つオブジェクトと関わる場合は、まずMCPの`world_state`からそのオブジェクトの現在の状態（例：`door_locked`）を確認し、その状態に応じた応答をしてください。
3. もしプレイヤーの行動の成否が不確かな場合（例：箱をこじ開ける、重いものを動かす）、**能力値チェック**を実行します。手順は以下の通りです。
    a. その行動に最も関連する能力（腕力, 知力, 器用）を決定します。
    b. プレイヤーの能力値を `get_data` ツールで取得します。
    c. `roll_dice(1, 10)` ツールで1d10ダイスを振ります。
    d. `(ダイスの結果 + プレイヤーの能力値)` が、あなたが設定した難易度（例: 10）以上であれば成功、未満であれば失敗と判断します。
    e. 成功・失敗に基づいた結果を描写します。
4. もしゲームの状態（プレイヤーのHP、持ち物、場所など）を変更する必要がある場合は、提供されているツール（関数）を呼び出して更新してください。キーと値はJSON形式の文字列で渡す必要があります。
    - 例: `update_data("player", '"HP"' , '-5', relative=True)`
    - 例: `update_data("player", '["能力", "腕力"]', '5')`
5. **想定外の行動への対応**: もしプレイヤーの行動が、現在の状況で物理的に不可能であったり、意味をなさない場合（例：「鍵を食べる」）、ツールは呼び出さず、その行動がなぜできないのかをプレイヤーに描写してください。
6. 最後に、プレイヤーへの応答メッセージを**必ず**生成します。これは、ツールを呼び出した結果や、状況の描写など、プレイヤーに伝えるべき情報です。ツールを呼び出した場合でも、その実行結果をプレイヤーに伝えるためのメッセージが必須です。

---
それでは、以下の情報に基づいて、あなたの応答を生成してください。
"""

    def generate_prompt(
        self,
        rules: str,
        gamebook_snippets: List[Dict[str, str]],
        mcp_state: Dict[str, Any],
        player_input: str
    ) -> str:
        """
        すべての情報を統合し、AIに渡す最終的なプロンプトを生成する。
        """

        # L1: 憲法を構築
        constitution_prompt = self._BASE_CONSTITUTION.format(rules=rules)

        # L3: ゲームブックの情報を整形
        gamebook_prompt = "## ゲームブック（長期記憶）\n"
        if not gamebook_snippets:
            gamebook_prompt += "関連情報なし\n"
        else:
            for snippet in gamebook_snippets:
                gamebook_prompt += f"- {str(snippet)}\n"

        # L2: MCPの状態を整形
        mcp_prompt = "## 現在のゲーム状態（短期記憶）\n"
        mcp_prompt += f"- 現在のシーンID: {mcp_state.get('_current_scene_id')}\n"
        mcp_prompt += f"- プレイヤー状態: {mcp_state.get('_player')}\n"
        mcp_prompt += f"- 敵の状態: {mcp_state.get('_enemies')}\n"

        # プレイヤーの行動
        player_input_prompt = f"## プレイヤーの行動\n{player_input}\n"

        # すべてを結合
        final_prompt = (
            f"{constitution_prompt}\n"
            f"{gamebook_prompt}\n"
            f"{mcp_prompt}\n"
            f"{player_input_prompt}\n"
            "## あなたの応答\n"
        )

        return final_prompt
