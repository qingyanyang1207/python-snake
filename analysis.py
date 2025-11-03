from typing import Dict, Optional, Tuple
import pygame
from ui import show_text, draw_button
from score_manage import get_rankings

#游戏分析器
class GameAnalyzer:

    def analyze_data(self) -> Optional[Dict[str, any]]:
        try:
            rankings = get_rankings()
            if not rankings:
                print("无有效游戏数据")
                return None
            if len(rankings) < 2:
                print("有效数据不足2条，无法计算增长率")
                return None
            try:
                # 提取基础数据（分数、时间、日期）
                scores = [rank[0] for rank in rankings]
                times = []
                for rank in rankings:
                    try:
                        times.append(int(rank[1]))  # 时间转换为整数（秒）
                    except ValueError:
                        print(f"时间转换失败，跳过数据：{rank}")
                        return None
                dates = [rank[2] for rank in rankings]
            except Exception as e:
                print(f"数据提取失败: {e}")
                return None

            # 按日期排序（确保时间顺序，避免数据混乱）
            combined = list(zip(scores, times, dates))
            combined.sort(key=lambda x: x[2])  # 按日期升序排列
            scores = [item[0] for item in combined]
            times = [item[1] for item in combined]
            dates = [item[2] for item in combined]

            # 1. 计算每局吃到食物（所得分数减去每存活一秒自动得一分再除五十取整）
            food_counts = []
            for score in scores:
                food_count = max(0, (score-int(rank[1])) // 50)
                food_counts.append(food_count)

            # 2. 计算每秒食物效率（食物数/游戏时间）
            food_efficiency = []
            for f, t in zip(food_counts, times):
                if t > 0:
                    food_efficiency.append(round(f / t, 2))
                else:
                    food_efficiency.append(0)

            # 3. 计算分数增长率（相邻局次对比，默认第一局为0）
            score_pairs = zip(scores[:-1], scores[1:])
            growth_rates = list(map(
                lambda x: round((x[1] - x[0]) / x[0] * 100, 1) if x[0] != 0 else 0,
                score_pairs
            ))
            growth_rates = [0.0] + growth_rates  # 第一局无前置数据，设为0

            # 4. 计算效率（每分耗时：游戏时间/分数）
            efficiency = list(map(
                lambda s, t: round(t / s, 2) if s != 0 else 0,
                scores,
                times
            ))

            # 5. 格式化日期标签
            indexed_dates = list(enumerate(dates))
            date_labels = [f"{idx + 1}.{date[:10]}" for idx, date in indexed_dates]

            # 6. 计算汇总指标（移除日期范围相关计算）
            avg_score = sum(scores) // len(scores)  # 平均分数（整数）
            best_efficiency = min(efficiency) if efficiency else 0  # 最佳效率（最小每分耗时）
            total_time = sum(times)  # 总游戏时间（秒）
            total_food = sum(food_counts)  # 总食物数量
            overall_food_rate = round(total_food / total_time, 2) if total_time > 0 else 0  # 整体食物效率

            # 7. 计算最长连续增长次数
            streak = 0
            max_streak = 0
            for rate in growth_rates[1:]:  # 跳过第一局的0值
                if rate > 0:
                    streak += 1
                    max_streak = max(max_streak, streak)
                else:
                    streak = 0

            # 返回完整分析结果（无日期范围字段）
            return {
                "scores": scores,
                "times": times,
                "efficiency": efficiency,
                "growth_rates": growth_rates,
                "dates": date_labels,
                "avg_score": avg_score,
                "best_efficiency": best_efficiency,
                "total_games": len(rankings),
                "total_time": total_time,
                "total_food": total_food,
                "food_efficiency": food_efficiency,
                "overall_food_rate": overall_food_rate,
                "max_streak": max_streak,
                "food_counts": food_counts
            }
        except Exception as e:
            print(f"数据分析失败: {e}")
            return None

#数据分析页界面管理器
class GameAnalysis:

    def __init__(self, screen):
        self.screen = screen
        self.analyzer = GameAnalyzer()
        self.screen_width, self.screen_height = screen.get_size()

        # 1. 界面元素基础配置（此处色卡找ai配的，改了几版依旧好丑，没招了，那个颜色色卡选的我眼睛疼
        self.back_btn = pygame.Rect(10, 10, 40, 40)  # 左上角返回按钮（←）
        self.colors = {
            "bg": (205, 218, 230),  # 背景色（保持不变，作为色系基准）
            "btn_normal": (170, 200, 230),  # 按钮正常色（浅亮蓝灰，比原版本亮20%）
            "btn_hover": (140, 180, 220),  # 按钮悬停色（中亮蓝灰，hover时仍有明显反馈）
            "text_title": (60, 90, 120),  # 标题文字色（中深蓝灰，增亮后更显清晰）
            "text_normal": (75, 105, 135),  # 普通文字色（中亮蓝灰，避免灰暗感）
            "text_highlight": (90, 130, 170),  # 高亮文字色（亮深蓝灰，突出数据且不刺眼）
            "chart_grid": (50,70,90),  # 图表网格线色（浅亮蓝灰，清晰不厚重）
            # 折线图颜色（亮蓝灰渐变，区分度+亮度双保障）
            "chart_score": (74,137,200),  # 分数曲线色（中亮蓝灰，视觉主色）
            "chart_efficiency": (55,188,188),  # 效率曲线色（浅亮蓝灰，与按钮呼应）
            "chart_growth": (150,125,220),  # 增长率曲线色（中深蓝灰，突出趋势）
            "chart_area": (170, 200, 230, 50),  # 分数区域填充色（浅亮蓝灰半透明，更显通透）
            "tooltip_bg": (250, 252, 255, 240),  # 提示框背景（近白色蓝灰，明亮不灰暗）
            "tooltip_border": (170, 200, 230),  # 提示框边框色（浅亮蓝灰，与按钮统一）
            "card_bg": (250, 252, 255, 200)  # 数据卡片背景（近白色蓝灰半透明，明亮且融入背景）
        }

        # 2. 图表滚动控制（统一单图表滚动，解决同步问题）
        self.chart_offset = 0  # 统一滚动偏移量
        self.is_dragging = False  # 是否正在拖动图表
        self.drag_start_x = 0  # 拖动起始X坐标
        self.active_chart = None  # 当前激活的图表（仅组合图表）

    def draw_tooltip(self, position: Tuple[int, int], tooltip_data: Dict):
        """绘制鼠标悬停提示框，显示当前局次的完整原始数据（优化排版）"""
        font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC"], 16)
        # 构建提示文本（局次、分数、效率、增长率）
        text_lines = [
            f"局次：{tooltip_data['round']}",
            f"分数：{tooltip_data['score']} 分",
            f"每分耗时：{tooltip_data['efficiency']} 秒/分",
            f"分数增长率：{tooltip_data['growth']} %"
        ]

        # 计算提示框尺寸（适配文本长度，增加内边距）
        max_width = max([font.size(line)[0] for line in text_lines])
        total_height = sum([font.size(line)[1] for line in text_lines]) + 12  # 增加行间距
        padding = 10  # 扩大内边距，提升舒适度

        # 提示框位置（优化边界调整，避免超出屏幕）
        rect = pygame.Rect(
            position[0] + 12,
            position[1] - total_height - 25,
            max_width + padding * 2,
            total_height + padding * 2
        )
        # 右边界超出屏幕则左移，上边界超出则下移
        if rect.right > self.screen_width:
            rect.x = position[0] - rect.width - 12
        if rect.top < 0:
            rect.y = position[1] + 12

        # 绘制提示框背景和边框（圆角视觉优化）
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill(self.colors["tooltip_bg"])
        self.screen.blit(s, (rect.x, rect.y))
        pygame.draw.rect(self.screen, self.colors["tooltip_border"], rect, 1, 4)  # 圆角半径4

        # 绘制提示文本（增加行间距，提升可读性）
        y_offset = rect.y + padding
        for line in text_lines:
            text_surface = font.render(line, True, self.colors["text_normal"])
            self.screen.blit(text_surface, (rect.x + padding, y_offset))
            y_offset += font.size(line)[1] + 3  # 优化行间距

    def draw_combined_chart(self, analysis_data: Dict) -> Optional[Dict]:
        """绘制组合折线图（优化布局：调整图表位置、图例分布，解决拥挤）"""
        # 1. 图表尺寸与位置（优化垂直布局，增加与汇总卡片的间距）
        chart_height = self.screen_height // 2.6  # 微调高度，避免底部溢出
        chart_rect = pygame.Rect(
            self.screen_width // 12,  # 左侧边距调整为1/12，增加左右空间
            self.screen_height // 2.8,  # 顶部边距上移，与汇总卡片保持40px+间距
            self.screen_width * 5 // 6,  # 图表宽度调整为5/6屏幕宽，提升横向显示空间
            chart_height
        )

        # 2. 绘制图表背景和边框（优化边框视觉）
        bg_surface = pygame.Surface((chart_rect.width, chart_rect.height), pygame.SRCALPHA)
        bg_surface.fill(self.colors["card_bg"])
        self.screen.blit(bg_surface, (chart_rect.left, chart_rect.top))
        pygame.draw.rect(self.screen, self.colors["chart_grid"], chart_rect, 2, 2)  # 轻微圆角

        # 3. 绘制网格线（优化密度，提升可读性）
        # 横向网格线（垂直方向分割：从8条减为6条，避免密集）
        num_grid_x = 6
        for i in range(1, num_grid_x):
            x = chart_rect.left + (chart_rect.width // num_grid_x) * i
            pygame.draw.line(
                self.screen,
                self.colors["chart_grid"],
                (x, chart_rect.top),
                (x, chart_rect.bottom),
                1
            )
        # 纵向网格线（水平方向分割：从6条减为5条，减少干扰）
        num_grid_y = 5
        for i in range(1, num_grid_y):
            y = chart_rect.top + (chart_rect.height // num_grid_y) * i
            pygame.draw.line(
                self.screen,
                self.colors["chart_grid"],
                (chart_rect.left, y),
                (chart_rect.right, y),
                1
            )

        # 4. 提取图表数据（确保三个指标长度一致）
        dates = analysis_data["dates"]
        scores = analysis_data["scores"]
        efficiency = analysis_data["efficiency"]
        growth_rates = analysis_data["growth_rates"]
        total_items = len(dates)  # 总局次

        # 5. 数据归一化（保持原逻辑，确保同图显示）
        # 分数归一化（0→最低分，1→最高分）
        max_score = max(scores) if scores else 1
        min_score = min(scores) if scores else 0
        normalized_scores = [(s - min_score) / (max_score - min_score) for s in scores]

        # 效率归一化（0→最低效率，1→最高效率）
        max_eff = max(efficiency) if efficiency else 1
        min_eff = min(efficiency) if efficiency else 0
        normalized_eff = [(e - min_eff) / (max_eff - min_eff) for e in efficiency]

        # 增长率归一化（覆盖-100%~500%常见范围）
        normalized_growth = []
        for g in growth_rates:
            if g < -100:
                normalized_growth.append(0)
            elif g > 500:
                normalized_growth.append(1)
            else:
                normalized_growth.append((g + 100) / 600)

        # 6. 处理可见数据范围（保持原逻辑，一屏显示8个局次）
        items_per_view = 8
        start_idx = max(0, self.chart_offset)
        end_idx = min(total_items, start_idx + items_per_view)
        if total_items <= items_per_view:
            start_idx = 0
            end_idx = total_items

        # 截取可见数据
        visible_dates = dates[start_idx:end_idx]
        visible_scores = normalized_scores[start_idx:end_idx]
        visible_eff = normalized_eff[start_idx:end_idx]
        visible_growth = normalized_growth[start_idx:end_idx]
        raw_scores = scores[start_idx:end_idx]
        raw_eff = efficiency[start_idx:end_idx]
        raw_growth = growth_rates[start_idx:end_idx]

        # 7. 绘制滚动指示器（优化位置和样式）
        if total_items > items_per_view:
            scroll_indicator_width = chart_rect.width * (items_per_view / total_items)
            scroll_indicator_x = chart_rect.left + (start_idx / total_items) * chart_rect.width
            scroll_indicator = pygame.Rect(
                scroll_indicator_x,
                chart_rect.bottom + 12,  # 下移指示器，增加与图表间距
                scroll_indicator_width,
                7  # 增加高度，提升可见性
            )
            pygame.draw.rect(self.screen, self.colors["chart_score"], scroll_indicator, 0, 3)  # 圆角

        # 8. 计算数据点坐标并绘制（优化点大小，增强区分度）
        points = {"score": [], "efficiency": [], "growth": []}
        hovered_idx = -1
        mx, my = pygame.mouse.get_pos()

        for i in range(len(visible_dates)):
            # 计算X坐标（横向均匀分布）
            x_ratio = i / (len(visible_dates) - 1) if len(visible_dates) > 1 else 0.5
            x = chart_rect.left + x_ratio * chart_rect.width

            # 计算Y坐标（归一化映射）
            score_y = chart_rect.bottom - (visible_scores[i] * chart_rect.height)
            eff_y = chart_rect.bottom - (visible_eff[i] * chart_rect.height)
            growth_y = chart_rect.bottom - (visible_growth[i] * chart_rect.height)
            points["score"].append((x, score_y))
            points["efficiency"].append((x, eff_y))
            points["growth"].append((x, growth_y))

            # 绘制数据点（增大半径，增强视觉区分）
            pygame.draw.circle(self.screen, self.colors["chart_score"], (int(x), int(score_y)), 6)
            pygame.draw.circle(self.screen, self.colors["chart_efficiency"], (int(x), int(eff_y)), 6)
            pygame.draw.circle(self.screen, self.colors["chart_growth"], (int(x), int(growth_y)), 6)

            # 绘制X轴标签（优化位置，避免与滚动指示器重叠）
            show_text(
                self.screen,
                (x, chart_rect.bottom + 25),  # 下移标签，增加与指示器间距
                visible_dates[i].split('.')[0],
                self.colors["text_normal"],
                is_center=True,
                font_size=15  # 增大字体，提升可读性
            )

            # 检测鼠标悬停（扩大检测范围，提升交互灵敏度）
            if (chart_rect.left - 10 <= mx <= chart_rect.right + 10 and
                    chart_rect.top - 10 <= my <= chart_rect.bottom + 10):
                if abs(mx - x) < 18:  # 扩大横向误差范围
                    hovered_idx = i

        # 9. 绘制折线（加粗线条，增强视觉冲击力）
        line_width = 3  # 线条宽度从2改为3
        if len(points["score"]) > 1:
            pygame.draw.lines(self.screen, self.colors["chart_score"], False, points["score"], line_width)
        if len(points["efficiency"]) > 1:
            pygame.draw.lines(self.screen, self.colors["chart_efficiency"], False, points["efficiency"], line_width)
        if len(points["growth"]) > 1:
            pygame.draw.lines(self.screen, self.colors["chart_growth"], False, points["growth"], line_width)

        # 10. 绘制图例（修改为左上角位置）
        legend_items = [
            ("分数", self.colors["chart_score"]),
            ("每分耗时", self.colors["chart_efficiency"]),
            ("分数增长率", self.colors["chart_growth"])
        ]
        legend_y = chart_rect.top + 15  # 左上角起始Y坐标
        legend_x = chart_rect.left + 20  # 左上角起始X坐标
        for name, color in legend_items:
            # 图例色块（增大尺寸，提升辨识度）
            legend_rect = pygame.Rect(legend_x, legend_y, 18, 18)
            pygame.draw.rect(self.screen, color, legend_rect, 0, 2)  # 轻微圆角
            # 图例文字（右对齐，与色块间距优化）
            show_text(
                self.screen,
                (legend_x + 28, legend_y + 9),
                name,
                self.colors["text_normal"],
                is_center=False,
                font_size=15  # 增大字体
            )
            legend_y += 30  # 增大概率间距，避免拥挤


        # 原始数据范围提示（优化位置，改为图表顶部居中，提升可读性）
        value_range_text = (
            f"分数范围：{min_score}-{max_score} 分 | "
            f"每分耗时：{min_eff}-{max_eff} 秒 | "
            f"增长率范围：-1000%~5000%"
        )
        show_text(
            self.screen,
            (chart_rect.centerx, chart_rect.top - 25),  # 上移提示，与图表顶部保持间距
            value_range_text,
            self.colors["text_normal"],
            is_center=True,
            font_size=13  # 增大字体
        )

        # 12. 显示鼠标悬停提示（保持原逻辑，优化位置）
        if hovered_idx != -1 and 0 <= hovered_idx < len(visible_dates):
            tooltip_data = {
                "round": visible_dates[hovered_idx].split('.')[0],
                "score": raw_scores[hovered_idx],
                "efficiency": raw_eff[hovered_idx],
                "growth": raw_growth[hovered_idx]
            }
            tip_x, tip_y = points["score"][hovered_idx]
            self.draw_tooltip((tip_x, tip_y), tooltip_data)

        return {
            "rect": chart_rect,
            "start_idx": start_idx,
            "end_idx": end_idx,
            "total_items": total_items,
            "items_per_view": items_per_view
        }

    def draw_analysis(self, analysis_data):
        """绘制完整数据分析界面（优化汇总卡片布局，移除日期范围）"""
        # 1. 填充背景
        self.screen.fill(self.colors["bg"])

        # 2. 绘制标题与返回按钮（优化位置和样式）
        # 标题（上移位置，增加与汇总卡片间距）
        show_text(
            self.screen,
            (self.screen_width // 2, 55),
            "游戏数据分析",
            self.colors["text_title"],
            is_center=True,
            font_size=38  # 增大字体，提升标题权重
        )
        # 返回按钮（优化悬停反馈，增加边框）
        mx, my = pygame.mouse.get_pos()
        back_btn_color = self.colors["btn_hover"] if self.back_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(self.screen, self.back_btn, '←', back_btn_color)
        # 按钮边框优化
        pygame.draw.rect(self.screen, (120, 160, 200), self.back_btn, 1, 3)

        # 3. 数据展示逻辑（有数据则显示汇总卡片+图表，无数据则提示）
        chart_info = None
        if analysis_data:
            # 3.1 绘制汇总信息卡片（优化布局：三列两行→三列两行，移除日期范围，增加内边距）
            card_width = self.screen_width * 5 // 6  # 卡片宽度与图表对齐
            card_height = 130  # 增加卡片高度，提升数据展示空间
            card_rect = pygame.Rect(
                (self.screen_width - card_width) // 2,
                90,  # 卡片Y坐标，与标题保持35px间距
                card_width,
                card_height
            )
            # 卡片背景与边框（优化圆角和透明度）
            card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            card_surface.fill(self.colors["card_bg"])
            self.screen.blit(card_surface, (card_rect.left, card_rect.top))
            pygame.draw.rect(self.screen, self.colors["chart_grid"], card_rect, 2, 3)  # 圆角半径3

            # 汇总卡片标题（优化位置，增加底部间距）
            show_text(
                self.screen,
                (card_rect.centerx, card_rect.top + 20),
                "游戏汇总数据",
                self.colors["text_title"],
                is_center=True,
                font_size=20  # 增大字体
            )

            # 汇总数据项（移除日期范围，优化分布，增加字体大小）
            column_width = card_width // 3  # 三列均分，提升整洁度
            item_y1 = card_rect.top + 55  # 第一行数据Y坐标
            item_y2 = card_rect.top + 90  # 第二行数据Y坐标
            summary_items = [
                # 第一行（总局数、平均分、最佳效率）
                (f"总游戏局数：{analysis_data['total_games']} 局", card_rect.left + column_width * 0.5),
                (f"平均分数：{analysis_data['avg_score']} 分", card_rect.left + column_width * 1.5),
                (f"最佳效率：{analysis_data['best_efficiency']} 秒/分", card_rect.left + column_width * 2.5),
                # 第二行（总时间、总食物、平均每秒食物）
                (f"总游戏时间：{analysis_data['total_time']} 秒", card_rect.left + column_width * 0.5),
                (f"总食物数量：{analysis_data['total_food']} 个", card_rect.left + column_width * 1.5),
                (f"平均每秒食物：{analysis_data['overall_food_rate']} 个/秒", card_rect.left + column_width * 2.5),
            ]

            # 绘制第一行数据（优化字体大小，增强关键指标视觉）
            for i in range(3):
                text, x_pos = summary_items[i]
                show_text(
                    self.screen,
                    (x_pos, item_y1),
                    text,
                    self.colors["text_highlight"],
                    is_center=True,
                    font_size=16  # 增大字体
                )
            # 绘制第二行数据
            for i in range(3, 6):
                text, x_pos = summary_items[i]
                show_text(
                    self.screen,
                    (x_pos, item_y2),
                    text,
                    self.colors["text_highlight"],
                    is_center=True,
                    font_size=16
                )

            # 3.2 绘制组合图表（分数+效率+增长率）
            chart_info = self.draw_combined_chart(analysis_data)

        else:
            # 无数据提示（优化位置和字体，提升友好度）
            show_text(
                self.screen,
                (self.screen_width // 2, self.screen_height // 2 - 50),
                "暂无足够游戏数据（需至少2局记录）",
                self.colors["text_normal"],
                is_center=True,
                font_size=30
            )
            show_text(
                self.screen,
                (self.screen_width // 2, self.screen_height // 2 + 10),
                "快去玩几局吧！",
                self.colors["text_highlight"],
                is_center=True,
                font_size=26
            )

        # 4. 更新屏幕显示
        pygame.display.update()
        return {"chart_info": chart_info}

    def handle_chart_drag(self, event, chart_info):
        """处理图表拖动和滚轮事件（保持原逻辑，优化拖动灵敏度）"""
        mx, my = pygame.mouse.get_pos()
        chart_info = chart_info.get("chart_info")
        if not chart_info:
            return

        # 提取图表关键参数
        chart_rect = chart_info["rect"]
        total_items = chart_info["total_items"]
        items_per_view = chart_info["items_per_view"]
        max_offset = max(0, total_items - items_per_view)

        # 处理鼠标事件（优化拖动触发阈值，从20px改为15px，提升灵敏度）
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击（开始拖动）
                if chart_rect.collidepoint(mx, my):
                    self.is_dragging = True
                    self.drag_start_x = mx
                    self.active_chart = "combined"
            elif event.button == 4:  # 滚轮上滚（向左滚动）
                if chart_rect.collidepoint(mx, my):
                    self.chart_offset = max(0, self.chart_offset - 1)
            elif event.button == 5:  # 滚轮下滚（向右滚动）
                if chart_rect.collidepoint(mx, my):
                    self.chart_offset = min(max_offset, self.chart_offset + 1)

        elif event.type == pygame.MOUSEMOTION:  # 鼠标拖动
            if self.is_dragging and self.active_chart == "combined":
                drag_delta = self.drag_start_x - mx
                if abs(drag_delta) > 15:  # 降低触发阈值，提升拖动响应速度
                    scroll_amount = 1 if drag_delta > 0 else -1
                    self.chart_offset = max(0, min(max_offset, self.chart_offset + scroll_amount))
                    self.drag_start_x = mx

        elif event.type == pygame.MOUSEBUTTONUP:  # 鼠标释放（结束拖动）
            if event.button == 1:
                self.is_dragging = False
                self.active_chart = None

    def run(self):
        """运行数据分析界面主循环（保持原逻辑）"""
        clock = pygame.time.Clock()
        analysis_data = self.analyzer.analyze_data()  # 提前计算一次数据
        chart_info = {}

        while True:
            # 1. 绘制界面
            chart_info = self.draw_analysis(analysis_data)

            # 2. 处理事件
            for event in pygame.event.get():
                # 退出游戏
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                # 点击返回按钮（返回主菜单）
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if self.back_btn.collidepoint(mx, my):
                        return "MAIN_MENU"
                # 按ESC键返回主菜单
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "MAIN_MENU"
                # 处理图表滚动（拖动/滚轮）
                self.handle_chart_drag(event, chart_info)

            # 3. 控制帧率（60FPS，避免界面卡顿）
            clock.tick(60)