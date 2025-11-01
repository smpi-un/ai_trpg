import logging

# --- 1. Model (データベースMCP) ---
# ゲームの状態（ステータス、アイテム、シナリオ）を管理する。
class DatabaseMCP:
    """
    [Model] 
    ゲームのデータベースとメモリを管理する。
    すべての状態はここに集約される。
    """
    def __init__(self):
        logging.debug("[MCP Init: Model (Database) が起動しました]")
        self._player = {"HP": 10, "ATK": 3, "アイテム": ["やくそう"], "状態": "正常"}
        self._enemies = {} # 戦闘中の敵を管理
        self._current_scene_id = "start"
        
        self._enemy_templates = {
            "goblin": {"name": "ゴブリン", "HP": 5, "ATK": 2}
        }
        
        self._game_book = {
            "start": {
                "text": "あなたは暗い洞窟の入り口に立っている。\n奥からは獣のようなうなり声が聞こえる。",
                "options": ["すすむ", "あたりをみる", "アイテム"]
            },
            "look_around": {
                "text": "入り口の周りにはコケが生えている。特に変わったものはない。",
                "options": ["すすむ"]
            },
            "encounter_goblin": {
                "text": "一歩足を踏み入れると、目の前にゴブリンが現れた！",
                "trigger": "start_battle:goblin"
            },
            "battle_turn": {
                "text": "ゴブリンはこちらを睨んでいる。",
                "options": ["たたかう", "アイテム", "にげる"]
            },
            "victory": {
                "text": "ゴブリンを倒した！奥に宝箱が見える。",
                "options": ["あける"]
            },
            "treasure": {
                "text": "宝箱を開けた。中には「どうのつるぎ」(ATK+2) が入っていた！\nあなたは洞窟を後にした。",
                "trigger": "get_item:どうのつるぎ"
            },
            "escape": {"text": "あなたはゴブリンから逃げ出した...", "options": ["end"]},
            "dead": {"text": "あなたはゴブリンに倒されてしまった...", "options": ["end"]}
        }

    def get_data(self, target, key):
        """[MCP:Model] データを取得するツール"""
        logging.debug(f"[Tool Call (Model): get_data(target={target}, key={key}) を実行]")
        if target == "player":
            return self._player.get(key)
        if target in self._enemies:
            return self._enemies[target].get(key)
        return None

    def update_data(self, target, key, value, relative=False):
        """[MCP:Model] データを更新するツール"""
        logging.debug(f"[Tool Call (Model): update_data(target={target}, key={key}, value={value}, relative={relative}) を実行]")
        target_obj = None
        if target == "player":
            target_obj = self._player
        elif target in self._enemies:
            target_obj = self._enemies[target]
        
        if target_obj:
            if relative:
                target_obj[key] = target_obj.get(key, 0) + value
            else:
                target_obj[key] = value
            return f"{target}の{key}が{target_obj[key]}になった"
        return f"対象{target}が見つからない"

    def get_scene(self, scene_id=None):
        """[MCP:Model] ゲームブック（シナリオ）をめくるツール"""
        if scene_id is None:
            scene_id = self._current_scene_id
        logging.debug(f"[Tool Call (Model): get_scene(scene_id={scene_id}) を実行]")
        return self._game_book.get(scene_id)

    def set_current_scene(self, scene_id):
        """[MCP:Model] 現在のシーンIDを設定するツール"""
        logging.debug(f"[Tool Call (Model): set_current_scene(scene_id={scene_id}) を実行]")
        self._current_scene_id = scene_id
        return self.get_scene(scene_id)

    def manage_enemy(self, action, enemy_id, data=None):
        """[MCP:Model] 敵のデータを管理するツール"""
        logging.debug(f"[Tool Call (Model): manage_enemy(action={action}, enemy_id={enemy_id}) を実行]")
        if action == "create":
            template = self._enemy_templates.get(enemy_id)
            if template:
                self._enemies[enemy_id] = template.copy() 
                return f"{template['name']}をデータベースに作成した"
        elif action == "delete":
            if enemy_id in self._enemies:
                del self._enemies[enemy_id]
                return f"{enemy_id}をデータベースから削除した"
        return f"敵{enemy_id}に対する{action}操作に失敗"
        
    def manage_item(self, target, action, item_name):
        """[MCP:Model] アイテムを管理するツール"""
        logging.debug(f"[Tool Call (Model): manage_item(target={target}, action={action}, item_name={item_name}) を実行]")
        if target == "player":
            items = self._player["アイテム"]
            if action == "add":
                items.append(item_name)
                return f"{item_name} を手に入れた"
            elif action == "remove":
                if item_name in items:
                    items.remove(item_name)
                    return f"{item_name} を使用した"
                else:
                    return f"{item_name} を持っていない"
        return "アイテム操作失敗"
