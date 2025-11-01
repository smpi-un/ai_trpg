import time

# --- 4. View (コンソール表示) ---
# ユーザーへの表示と入力を担当する
class ConsoleView:
    """
    [View]
    コンソールへの表示とユーザーからの入力を担当する。
    """
    def show_message(self, text):
        """汎用的なメッセージを表示する"""
        print(text)
        time.sleep(0.5)

    def show_game_state(self, scene, player_hp, player_items, active_enemies):
        """現在のゲーム状況を整形して表示する"""
        print("\n" + "="*30)
        print(scene["text"])
        print("="*30)
        
        print(f"《あなた: HP={player_hp}, アイテム={player_items}》")
        
        for enemy_id, enemy_data in active_enemies.items():
            enemy_name = enemy_data.get("name", enemy_id)
            enemy_hp = enemy_data.get("HP")
            print(f"《敵: {enemy_name} (HP={enemy_hp})》")

        if scene.get("options"):
             print(f"[行動例: {', '.join(scene.get('options', []))}]")

    def get_user_input(self):
        """ユーザーの行動を受け付ける"""
        return input("\nあなたの行動: ")
