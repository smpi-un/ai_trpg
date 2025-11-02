import logging
import json
from typing import List, Union

# --- 1. Model (データベースMCP) ---
# ゲームの状態（ステータス、アイテム、シナリオ）を管理する。
class MCP:
    """
    [Model] 
    ゲームのデータベースとメモリを管理する。
    すべての状態はここに集約される。
    """
    def __init__(self):
        logging.debug("[MCP Init: Model (Database) が起動しました]")
        self._player = {"HP": 10, "ATK": 3, "アイテム": [], "状態": "正常", "能力": {"腕力": 0, "知力": 0, "器用": 0}}
        self._enemies = {} # 戦闘中の敵を管理
        self._world_state = {"door_locked": True} # 世界の状態を管理
        self._current_scene_id = "start"
        
        self._enemy_templates = {
            "goblin": {"name": "ゴブリン", "HP": 5, "ATK": 2}
        }

    def get_data(self, target: str, key: str = None):
        """[MCP:Model] データを取得するツール"""
        logging.debug(f"[Tool Call (Model): get_data(target={target}, key={key}) を実行]")
        if target == "player":
            return self._player if key is None else self._player.get(key)
        if target == "world":
            return self._world_state if key is None else self._world_state.get(key)
        if target == "enemies":
            return self._enemies if key is None else self._enemies.get(key)
        if target in self._enemies: # For a specific enemy
            return self._enemies[target] if key is None else self._enemies[target].get(key)
        return None

    def update_data(self, target: str, key_json: str, value_json: str, relative: bool = False):
        """[MCP:Model] データを更新する。keyとvalueはJSON文字列で渡す。単一のキーは"key"、ネストしたキーは["key1", "key2"]のように表現する。"""
        logging.debug(f"[Tool Call (Model): update_data(target={target}, key_json={key_json}, value_json={value_json}, relative={relative}) を実行]")
        
        try:
            key = json.loads(key_json)
            value = json.loads(value_json)
        except json.JSONDecodeError as e:
            return f"JSONの解析に失敗しました: {e}"

        target_obj = None
        if target == "player":
            target_obj = self._player
        elif target == "world":
            target_obj = self._world_state
        elif target in self._enemies:
            target_obj = self._enemies[target]
        
        if not target_obj:
            return f"対象{target}が見つからない"

        # ネストしたキーを処理
        if isinstance(key, list):
            final_key = key[-1]
            nav_obj = target_obj
            for k in key[:-1]:
                if k not in nav_obj or not isinstance(nav_obj[k], dict):
                    nav_obj[k] = {}
                nav_obj = nav_obj[k]
            target_obj = nav_obj
            key = final_key
        else:
            key = str(key) # Ensure key is a string

        # 値を更新
        if relative:
            current_value = target_obj.get(key, 0)
            if isinstance(current_value, (int, float)) and isinstance(value, (int, float)):
                target_obj[key] = current_value + value
            else:
                target_obj[key] = value
        else:
            target_obj[key] = value
            
        return f"{target}の{key}が{target_obj.get(key)}になった"

    def get_scene_id(self):
        """[MCP:Model] 現在のシーンIDを取得する"""
        logging.debug(f"[Tool Call (Model): get_scene_id() を実行]")
        return self._current_scene_id

    def set_current_scene(self, scene_id):
        """[MCP:Model] 現在のシーンIDを設定するツール"""
        logging.debug(f"[Tool Call (Model): set_current_scene(scene_id={scene_id}) を実行]")
        self._current_scene_id = scene_id
        return f"現在のシーンが {scene_id} に設定されました。"

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
