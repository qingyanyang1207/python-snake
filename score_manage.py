import os


def save_score(score_data):
    """保存分数数据到文件"""
    try:
        with open("scores.txt", "a", encoding="utf-8") as f:
            f.write(score_data + "\n")
    except Exception as e:
        print(f"保存分数失败: {e}")

def get_rankings():
    rankings = []
    if not os.path.exists("scores.txt"):
        return rankings
    try:
        with open("scores.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    # 1. 确保是3个字段
                    if len(parts) != 3:
                        print(f"跳过无效数据（字段数错误）：{line}")
                        continue
                    score_str, time_str, date_str = parts
                    # 2. 校验分数是整数
                    try:
                        score = int(score_str)
                    except ValueError:
                        print(f"跳过无效数据（分数非整数）：{line}")
                        continue
                    # 3. 校验时间是整数（秒数）
                    try:
                        time = int(time_str)  # 确保时间是纯数字秒数
                    except ValueError:
                        print(f"跳过无效数据（时间非整数）：{line}")
                        continue
                    # 4. 简单校验日期格式（至少包含“-”）
                    if "-" not in date_str:
                        print(f"跳过无效数据（日期格式错误）：{line}")
                        continue
                    rankings.append((score, time_str, date_str))  # 注意：time_str保留原字符串，后续分析时再转int
        rankings.sort(reverse=True, key=lambda x: x[0])
        return rankings
    except Exception as e:
        print(f"读取排行榜失败: {e}")
        return []