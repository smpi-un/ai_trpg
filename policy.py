import logging
import random

# --- 2. Policy (ルールMCP) ---
# ゲームのルール（ダイスロール、計算式）を管理する。
class PolicyMCP:
    """
    [Policy]
    ゲームのルール（ダイス、計算）を実行する。
    状態は持たず、計算のみを行う。
    """
    def __init__(self):
        logging.debug("[MCP Init: Policy (Rules) が起動しました]")

    def roll_dice(self, sides=6, num=1):
        """[MCP:Policy] ダイスロールを実行するツール"""
        try:
            safe_sides = int(sides)
            safe_num = int(num)
        except (ValueError, TypeError):
            safe_sides, safe_num = 6, 1
        roll_result = sum(random.randint(1, safe_sides) for _ in range(safe_num))
        logging.debug(f"[Tool Call (Policy): roll_dice(sides={safe_sides}, num={safe_num}) -> {roll_result}]")
        return roll_result

    def calculate_damage(self, base_attack):
        """[MCP:Policy] ダメージ計算を実行するツール"""
        bonus = self.roll_dice(3) - 1 
        damage = base_attack + bonus
        logging.debug(f"[Tool Call (Policy): calculate_damage(base_attack={base_attack}) -> {damage}]")
        return damage
