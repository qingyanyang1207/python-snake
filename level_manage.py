import os
import json
from typing import List, Dict, Optional,Tuple

# 关卡数据结构模板
LEVEL_TEMPLATE = {
    "level_id": "",
    "name": "",
    "score_target": 0,
    "time_limit": 0,
    "speed": 10,
    "obstacles": [],
    "is_custom": False
}


class LevelManager:
    def __init__(self):
        self.level_file = "levels.json"  # 关卡数据存储文件
        self.init_builtin_levels()  # 初始化内置关卡

    def init_builtin_levels(self):
        """初始化5个内置关卡（首次运行时创建）"""
        if not os.path.exists(self.level_file):
            builtin_levels = [
                # 关卡1：基础入门（无障碍物）
                {
                    "level_id": "level_1",
                    "name": "新手教程",
                    "score_target": 200,
                    "time_limit": 60,
                    "speed": 8,
                    "obstacles": [],
                    "is_custom": False
                },
                # 关卡2：简单障碍
                {
                    "level_id": "level_2",
                    "name": "初级挑战",
                    "score_target": 350,
                    "time_limit": 70,
                    "speed": 9,
                    "obstacles": [(200, 200, 40, 40), (400, 300, 40, 40), (600, 150, 40, 40)],
                    "is_custom": False
                },
                # 关卡3：中等障碍
                {
                    "level_id": "level_3",
                    "name": "中级挑战",
                    "score_target": 500,
                    "time_limit": 80,
                    "speed": 10,
                    "obstacles": [
                        (150, 150, 40, 40), (350, 250, 40, 40), (550, 350, 40, 40),
                        (250, 350, 40, 40), (450, 150, 40, 40)
                    ],
                    "is_custom": False
                },
                # 关卡4：高难度障碍
                {
                    "level_id": "level_4",
                    "name": "高级挑战",
                    "score_target": 700,
                    "time_limit": 90,
                    "speed": 11,
                    "obstacles": [
                        (100, 100, 40, 40), (200, 300, 40, 40), (300, 500, 40, 40),
                        (400, 200, 40, 40), (500, 400, 40, 40), (600, 100, 40, 40)
                    ],
                    "is_custom": False
                },
                # 关卡5：极限挑战
                {
                    "level_id": "level_5",
                    "name": "终极挑战",
                    "score_target": 1000,
                    "time_limit": 120,
                    "speed": 12,
                    "obstacles": [
                        (100, 200, 40, 40), (180, 350, 40, 40), (260, 100, 40, 40),
                        (340, 450, 40, 40), (420, 200, 40, 40), (500, 350, 40, 40),
                        (580, 100, 40, 40), (660, 450, 40, 40)
                    ],
                    "is_custom": False
                }
            ]
            self.save_levels(builtin_levels)

    def get_all_levels(self) -> List[Dict]:
        """获取所有关卡（内置+自定义）"""
        try:
            with open(self.level_file, "r", encoding="utf-8") as f:
                levels = json.load(f)
            # 按ID排序（内置关卡在前，自定义在后）
            levels.sort(key=lambda x: (x["is_custom"], x["level_id"]))
            return levels
        except Exception as e:
            print(f"读取关卡失败: {e}")
            return []

    def get_level_by_id(self, level_id: str) -> Optional[Dict]:
        """根据ID获取单个关卡信息"""
        levels = self.get_all_levels()
        for level in levels:
            if level["level_id"] == level_id:
                return level
        return None

    def save_levels(self, levels: List[Dict]):
        """保存关卡列表到本地文件"""
        try:
            with open(self.level_file, "w", encoding="utf-8") as f:
                json.dump(levels, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存关卡失败: {e}")

    def add_custom_level(self, level_data: Dict) -> bool:
        """添加自定义关卡（自动生成唯一ID）"""
        levels = self.get_all_levels()
        # 生成自定义关卡ID（custom_1, custom_2...）
        custom_ids = [int(l["level_id"].split("_")[1]) for l in levels if l["is_custom"]]
        new_id = f"custom_{max(custom_ids) + 1 if custom_ids else 1}"

        # 补全关卡数据
        custom_level = LEVEL_TEMPLATE.copy()
        custom_level.update({
            "level_id": new_id,
            "is_custom": True,
            **level_data  # 覆盖用户自定义的字段
        })

        # 验证必要字段
        required_fields = ["name", "score_target", "time_limit", "speed", "obstacles"]
        if not all(field in custom_level for field in required_fields):
            return False

        levels.append(custom_level)
        self.save_levels(levels)
        return True

    def save_level_score(self, level_id: str, score: int, time_used: int):
        """保存关卡通关分数（独立文件，不与排行榜混淆）"""
        score_file = "level_scores.json"
        scores = {}

        # 读取已有分数
        if os.path.exists(score_file):
            try:
                with open(score_file, "r", encoding="utf-8") as f:
                    scores = json.load(f)
            except:
                scores = {}

        # 更新当前关卡分数（只保留最佳成绩：分数更高，或分数相同时间更短）
        if level_id in scores:
            old_score, old_time = scores[level_id]
            if score > old_score or (score == old_score and time_used < old_time):
                scores[level_id] = (score, time_used)
        else:
            scores[level_id] = (score, time_used)

        # 保存分数
        try:
            with open(score_file, "w", encoding="utf-8") as f:
                json.dump(scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存关卡分数失败: {e}")

    def get_level_score(self, level_id: str) -> Optional[Tuple[int, int]]:
        """获取关卡最佳分数（分数, 时间）"""
        score_file = "level_scores.json"
        if not os.path.exists(score_file):
            return None
        try:
            with open(score_file, "r", encoding="utf-8") as f:
                scores = json.load(f)
            return scores.get(level_id)
        except Exception as e:
            print(f"读取关卡分数失败: {e}")
            return None