# achievements.py - 修复数据读取和进度计算问题
import json
import os
from datetime import datetime
from score_manage import get_rankings  # 导入排行榜数据读取


class AchievementSystem:
    def __init__(self):
        self.achievements_file = "achievements.json"
        self.achievements = self.load_achievements()

        # 成就定义
        self.achievement_definitions = {
            # 游戏进度类
            "first_blood": {
                "name": "初出茅庐",
                "desc": "完成第一局游戏",
                "icon": "🎮",
                "type": "progress",
                "condition": lambda stats: stats.get("games_played", 0) >= 1
            },
            "survivor": {
                "name": "生存专家",
                "desc": "单局生存时间超过3分钟",
                "icon": "⏱️",
                "type": "skill",
                "condition": lambda stats: stats.get("best_survival_time", 0) >= 180
            },
            "food_master": {
                "name": "美食家",
                "desc": "单局吃到50个食物",
                "icon": "🍎",
                "type": "skill",
                "condition": lambda stats: stats.get("max_food_in_game", 0) >= 50
            },
            "speed_demon": {
                "name": "速度之星",
                "desc": "每秒食物效率超过2.0",
                "icon": "⚡",
                "type": "skill",
                "condition": lambda stats: stats.get("best_food_efficiency", 0) >= 2.0
            },

            # 分数里程碑
            "centurion": {
                "name": "百分达人",
                "desc": "单局得分超过100分",
                "icon": "💯",
                "type": "milestone",
                "condition": lambda stats: stats.get("best_score", 0) >= 100
            },
            "five_hundred": {
                "name": "五百俱乐部",
                "desc": "单局得分超过500分",
                "icon": "🎯",
                "type": "milestone",
                "condition": lambda stats: stats.get("best_score", 0) >= 500
            },
            "thousand_club": {
                "name": "千分王者",
                "desc": "单局得分超过1000分",
                "icon": "👑",
                "type": "milestone",
                "condition": lambda stats: stats.get("best_score", 0) >= 1000
            },

            # 特殊挑战
            "perfectionist": {
                "name": "完美主义者",
                "desc": "连续3局分数增长",
                "icon": "📈",
                "type": "challenge",
                "condition": lambda stats: stats.get("consecutive_growth", 0) >= 3
            },
            "marathon": {
                "name": "马拉松选手",
                "desc": "单次游戏时长超过10分钟",
                "icon": "🏃",
                "type": "endurance",
                "condition": lambda stats: stats.get("longest_session", 0) >= 600
            },

            # 趣味成就
            "early_bird": {
                "name": "早起鸟儿",
                "desc": "在早上6-9点之间玩游戏",
                "icon": "🌅",
                "type": "fun",
                "condition": lambda stats: stats.get("played_morning", False)
            },
            "night_owl": {
                "name": "夜猫子",
                "desc": "在晚上10点后玩游戏",
                "icon": "🌙",
                "type": "fun",
                "condition": lambda stats: stats.get("played_night", False)
            }
        }

    def load_achievements(self):
        """加载成就数据"""
        if os.path.exists(self.achievements_file):
            try:
                with open(self.achievements_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载成就文件失败: {e}")
                return {"unlocked": {}, "stats": {}}
        return {"unlocked": {}, "stats": {}}

    def save_achievements(self):
        """保存成就数据"""
        try:
            with open(self.achievements_file, 'w', encoding='utf-8') as f:
                json.dump(self.achievements, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存成就数据失败: {e}")

    def load_game_data_from_scores(self):
        """从 scores.txt 加载游戏数据并更新统计"""
        rankings = get_rankings()
        if not rankings:
            print("无游戏记录数据")
            return

        stats = self.achievements.setdefault("stats", {})

        # 重置基础统计（从文件重新计算）
        stats["games_played"] = len(rankings)
        stats["total_score"] = 0
        stats["total_time"] = 0
        stats["best_score"] = 0
        stats["best_survival_time"] = 0
        stats["max_food_in_game"] = 0
        stats["best_food_efficiency"] = 0
        stats["longest_session"] = 0
        stats["played_morning"] = False
        stats["played_night"] = False

        scores_list = []
        times_list = []

        for score_data in rankings:
            try:
                score = int(score_data[0])
                time_seconds = int(score_data[1])
                date_str = score_data[2]

                # 累计统计
                stats["total_score"] += score
                stats["total_time"] += time_seconds

                # 最佳分数
                if score > stats["best_score"]:
                    stats["best_score"] = score

                # 最佳生存时间
                if time_seconds > stats["best_survival_time"]:
                    stats["best_survival_time"] = time_seconds

                # 食物数量计算
                food_count = max(0, (score - time_seconds) // 50)
                if food_count > stats["max_food_in_game"]:
                    stats["max_food_in_game"] = food_count

                # 食物效率
                if time_seconds > 0:
                    efficiency = food_count / time_seconds
                    if efficiency > stats["best_food_efficiency"]:
                        stats["best_food_efficiency"] = efficiency

                # 时间相关成就
                try:
                    # 解析日期时间
                    if " " in date_str:  # 确保是完整的时间格式
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        hour = date_obj.hour

                        if 6 <= hour < 9:
                            stats["played_morning"] = True
                        if hour >= 22 or hour < 4:
                            stats["played_night"] = True
                except Exception as e:
                    print(f"解析日期失败: {e}, 日期: {date_str}")

                # 记录分数和时间用于连续增长计算
                scores_list.append(score)
                times_list.append(time_seconds)

            except (ValueError, IndexError) as e:
                print(f"解析游戏数据失败: {e}, 数据: {score_data}")
                continue

        # 计算连续增长
        stats["consecutive_growth"] = self.calculate_consecutive_growth(scores_list)

        # 最长会话时间（使用最长游戏时间作为代理）
        if times_list:
            stats["longest_session"] = max(times_list)

        print(f"从 scores.txt 加载了 {len(rankings)} 条游戏记录")
        print(f"最佳分数: {stats['best_score']}")
        print(f"最佳生存时间: {stats['best_survival_time']}秒")
        print(f"最大食物数量: {stats['max_food_in_game']}")
        print(f"最佳食物效率: {stats['best_food_efficiency']:.2f}")

        # 检查并解锁成就
        self.check_achievements()

    def calculate_consecutive_growth(self, scores):
        """计算连续分数增长次数"""
        if len(scores) < 2:
            return 0

        max_streak = 0
        current_streak = 0

        for i in range(1, len(scores)):
            if scores[i] > scores[i - 1]:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0

        return max_streak

    def update_stats(self, game_data):
        """更新游戏统计信息（实时游戏时调用）"""
        stats = self.achievements.setdefault("stats", {})

        # 基础统计
        stats["games_played"] = stats.get("games_played", 0) + 1
        stats["total_score"] = stats.get("total_score", 0) + game_data.get("score", 0)
        stats["total_time"] = stats.get("total_time", 0) + game_data.get("time", 0)

        # 最佳记录
        current_score = game_data.get("score", 0)
        if current_score > stats.get("best_score", 0):
            stats["best_score"] = current_score

        current_time = game_data.get("time", 0)
        if current_time > stats.get("best_survival_time", 0):
            stats["best_survival_time"] = current_time

        # 食物统计
        food_count = max(0, (current_score - current_time) // 50)
        if food_count > stats.get("max_food_in_game", 0):
            stats["max_food_in_game"] = food_count

        # 效率统计
        if current_time > 0:
            efficiency = food_count / current_time
            if efficiency > stats.get("best_food_efficiency", 0):
                stats["best_food_efficiency"] = efficiency

        # 时间相关成就
        current_hour = datetime.now().hour
        if 6 <= current_hour < 9:
            stats["played_morning"] = True
        if current_hour >= 22 or current_hour < 4:
            stats["played_night"] = True

        # 会话时长
        session_time = game_data.get("session_duration", 0)
        if session_time > stats.get("longest_session", 0):
            stats["longest_session"] = session_time

        self.check_achievements()
        self.save_achievements()

    def check_achievements(self):
        """检查并解锁成就"""
        stats = self.achievements.setdefault("stats", {})
        unlocked = self.achievements.setdefault("unlocked", {})

        new_achievements = []

        for achievement_id, definition in self.achievement_definitions.items():
            if achievement_id not in unlocked:
                try:
                    if definition["condition"](stats):
                        # 解锁成就
                        unlocked[achievement_id] = {
                            "unlocked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "name": definition["name"],
                            "desc": definition["desc"],
                            "icon": definition["icon"]
                        }
                        new_achievements.append(achievement_id)
                        print(f"🎉 成就解锁: {definition['name']} - {definition['desc']}")
                except Exception as e:
                    print(f"检查成就 {achievement_id} 时出错: {e}")

        if new_achievements:
            self.save_achievements()

        return new_achievements

    def get_unlocked_achievements(self):
        """获取已解锁的成就"""
        return self.achievements.get("unlocked", {})

    def get_progress(self, achievement_id):
        """获取成就进度"""
        if achievement_id in self.achievements.get("unlocked", {}):
            return 100  # 已解锁

        definition = self.achievement_definitions.get(achievement_id)
        stats = self.achievements.get("stats", {})

        if not definition:
            return 0

        # 计算进度百分比
        try:
            if achievement_id == "first_blood":
                games_played = stats.get("games_played", 0)
                return min(100, (games_played / 1) * 100) if games_played < 1 else 100
            elif achievement_id == "centurion":
                best_score = stats.get("best_score", 0)
                return min(100, (best_score / 100) * 100)
            elif achievement_id == "five_hundred":
                best_score = stats.get("best_score", 0)
                return min(100, (best_score / 500) * 100)
            elif achievement_id == "thousand_club":
                best_score = stats.get("best_score", 0)
                return min(100, (best_score / 1000) * 100)
            elif achievement_id == "survivor":
                best_time = stats.get("best_survival_time", 0)
                return min(100, (best_time / 180) * 100)
            elif achievement_id == "food_master":
                max_food = stats.get("max_food_in_game", 0)
                return min(100, (max_food / 50) * 100)
            elif achievement_id == "speed_demon":
                best_eff = stats.get("best_food_efficiency", 0)
                return min(100, (best_eff / 2.0) * 100)
            elif achievement_id == "marathon":
                longest = stats.get("longest_session", 0)
                return min(100, (longest / 600) * 100)
            elif achievement_id == "perfectionist":
                consecutive = stats.get("consecutive_growth", 0)
                return min(100, (consecutive / 3) * 100)
            elif achievement_id in ["early_bird", "night_owl"]:
                # 时间相关的成就，如果条件满足就是100%，否则0%
                if definition["condition"](stats):
                    return 100
                else:
                    return 0
        except Exception as e:
            print(f"计算成就进度失败 {achievement_id}: {e}")

        return 0


# 全局成就系统实例
achievement_system = AchievementSystem()

# 初始化时自动加载历史数据
achievement_system.load_game_data_from_scores()