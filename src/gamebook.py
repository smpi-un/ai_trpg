import os
import re
from typing import Dict, List, Any

class GameBook:
    """
    ゲームブック（.mdファイル）を管理するクラス。
    静的なゲームデータ（L3）を担当する。
    """
    def __init__(self, directory: str = "gamebook"):
        self.directory = directory
        self.rules: str = ""
        self.scenario_raw_content: str = ""
        self.scenes: Dict[str, str] = {}
        self._load_data()

    def _load_data(self):
        """
        ディレクトリからルールとシナリオを読み込み、解析する。
        """
        rule_path = os.path.join(self.directory, "rule.md")
        if os.path.exists(rule_path):
            with open(rule_path, "r", encoding="utf-8") as f:
                self.rules = f.read()

        scenario_path = os.path.join(self.directory, "scenario.md")
        if os.path.exists(scenario_path):
            with open(scenario_path, "r", encoding="utf-8") as f:
                self.scenario_raw_content = f.read()
                self.scenes = self._parse_scenes(self.scenario_raw_content)

    def _parse_scenes(self, content: str) -> Dict[str, str]:
        """
        シナリオのMarkdownコンテンツからシーン構成のみを解析し、
        シーンIDをキーとする辞書を返す。
        例: {"[start]": "描写テキスト...", "[扉を調べる]": "描写テキスト..."}
        """
        scenes_dict = {}
        in_scene_section = False
        current_scene_id = None
        current_scene_content = []

        for line in content.splitlines():
            # 「シーン構成」セクションに入ったかどうかを判定
            if re.match(r"^##\s*4\.\s*シーン構成", line):
                in_scene_section = True
                continue
            # 他のH2見出しに来たらセクション終了
            if re.match(r"^##", line):
                in_scene_section = False
                continue

            if not in_scene_section:
                continue

            # 新しいシーンID（リスト項目）を検出
            scene_match = re.match(r"^\*\s*\*\*(\[[a-zA-Z0-9_-]+\])\*\*:", line)
            if scene_match:
                # 前のシーンの内容を保存
                if current_scene_id and current_scene_content:
                    scenes_dict[current_scene_id] = "\n".join(current_scene_content).strip()
                
                # 新しいシーンの開始
                current_scene_id = scene_match.group(1)
                current_scene_content = [line]
            elif current_scene_id:
                # シーンIDが検出された後の行を内容として追加
                current_scene_content.append(line)

        # 最後のシーンを保存
        if current_scene_id and current_scene_content:
            scenes_dict[current_scene_id] = "\n".join(current_scene_content).strip()

        return scenes_dict

    def get_rules(self) -> str:
        """
        ゲームの基本ルール（憲法の一部）を返す。
        """
        return self.rules

    def get_scene_by_id(self, scene_id: str) -> str | None:
        """
        指定されたシーンIDのテキストを返す。
        """
        return self.scenes.get(f"[{scene_id}]")

    def search(self, keyword: str) -> List[str]:
        """
        シナリオ全体からキーワードを含む行を検索する（補助用）。
        """
        results = []
        for line in self.scenario_raw_content.splitlines():
            if keyword in line:
                results.append(line.strip())
        return results

if __name__ == '__main__':
    # テスト用
    gamebook = GameBook()
    print("--- Rules ---")
    print(gamebook.get_rules()[:100])
    print("\n--- Parsed Scenes ---")
    import json
    print(json.dumps(gamebook.scenes, indent=2, ensure_ascii=False))
    print("\n--- Get Scene [start] ---")
    print(gamebook.get_scene_by_id("start"))
