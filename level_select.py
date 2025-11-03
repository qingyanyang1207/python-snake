import pygame
from typing import List, Dict, Optional, Tuple
from ui import show_text, draw_button
from level_manage import LevelManager
from level_editor import LevelEditor


class LevelSelect:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.level_manager = LevelManager()
        self.level_editor = LevelEditor(screen)
        self.scroll_offset = 0  # 关卡列表滚动偏移

        # UI配置
        self.colors = {
            "bg": (210, 225, 235),
            "btn_normal": (150, 180, 210),
            "btn_hover": (120, 160, 200),
            "text_normal": (50, 70, 90),
            "text_title": (50, 70, 90),
            "level_card_bg": (220, 230, 240),
            "locked": (180, 180, 180)
        }

        # 按钮位置
        self.back_btn = pygame.Rect(10, 10, 40, 40)
        self.edit_btn = pygame.Rect(self.screen_width - 150, 10, 140, 40)

        # 关卡卡片配置
        self.card_width = 200
        self.card_height = 150
        self.card_spacing = 30
        self.cards_per_row = 4

    def get_visible_levels(self) -> List[Dict]:
        """获取当前可见的关卡（支持滚动）"""
        all_levels = self.level_manager.get_all_levels()
        # 计算可见范围
        items_per_page = self.cards_per_row * 3
        start_idx = self.scroll_offset * items_per_page
        end_idx = start_idx + items_per_page
        return all_levels[start_idx:end_idx], len(all_levels) > items_per_page

    def draw_level_cards(self):
        """绘制关卡卡片"""
        visible_levels, has_scroll = self.get_visible_levels()
        mx, my = pygame.mouse.get_pos()

        for idx, level in enumerate(visible_levels):
            # 计算卡片位置
            row = idx // self.cards_per_row
            col = idx % self.cards_per_row
            x = self.screen_width // 2 - (
                        self.cards_per_row * (self.card_width + self.card_spacing) - self.card_spacing) // 2 + col * (
                            self.card_width + self.card_spacing)
            y = 100 + row * (self.card_height + self.card_spacing)

            # 绘制卡片背景
            card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
            card_color = self.colors["level_card_bg"] if card_rect.collidepoint(mx, my) else (230, 240, 250)
            pygame.draw.rect(self.screen, card_color, card_rect, 0, 5)
            pygame.draw.rect(self.screen, self.colors["text_normal"], card_rect, 1, 5)

            # 绘制关卡信息
            level_id = level["level_id"]
            level_name = level["name"]
            score_target = level["score_target"]
            is_custom = level["is_custom"]

            # 关卡类型标签（内置/自定义）
            tag_text = "自定义" if is_custom else f"关卡{level_id.split('_')[1]}"
            tag_color = (255, 165, 0) if is_custom else self.colors["text_normal"]
            show_text(self.screen, (x + 10, y + 15), tag_text, tag_color, is_center=False, font_size=16)

            # 关卡名称（换行处理）
            if len(level_name) > 8:
                level_name = level_name[:8] + "..."
            show_text(self.screen, (x + self.card_width // 2, y + 50), level_name, self.colors["text_title"],
                      font_size=20)

            # 分数目标
            show_text(self.screen, (x + self.card_width // 2, y + 85), f"目标: {score_target}分",
                      self.colors["text_normal"], font_size=18)

            # 最佳成绩（如果有）
            best_score = self.level_manager.get_level_score(level_id)
            if best_score:
                score, time_used = best_score
                time_str = f"{time_used // 60:02d}:{time_used % 60:02d}"
                show_text(self.screen, (x + self.card_width // 2, y + 115), f"最佳: {score}分/{time_str}", (0, 120, 0),
                          font_size=16)

        # 绘制滚动指示器（如果需要滚动）
        if has_scroll:
            total_pages = (len(self.level_manager.get_all_levels()) + self.cards_per_row * 2 - 1) // (
                        self.cards_per_row * 2)
            indicator_width = 100
            indicator_height = 8
            indicator_x = self.screen_width // 2 - indicator_width // 2
            indicator_y = self.screen_height - 50

            # 绘制指示器背景
            pygame.draw.rect(self.screen, (180, 180, 180),
                             (indicator_x, indicator_y, indicator_width, indicator_height), 0, 4)

            # 绘制当前页指示器
            page_indicator_width = indicator_width // total_pages
            page_indicator_x = indicator_x + self.scroll_offset * page_indicator_width
            pygame.draw.rect(self.screen, self.colors["btn_hover"],
                             (page_indicator_x, indicator_y, page_indicator_width, indicator_height), 0, 4)

    def draw_ui(self):
        """绘制关卡选择界面UI"""
        self.screen.fill(self.colors["bg"])

        # 标题
        show_text(self.screen, (self.screen_width // 2, 50), "选择关卡", self.colors["text_title"], font_size=40)

        # 绘制关卡卡片
        self.draw_level_cards()

        # 绘制按钮
        mx, my = pygame.mouse.get_pos()
        # 返回按钮
        back_color = self.colors["btn_hover"] if self.back_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(self.screen, self.back_btn, '←', back_color)

        # 自定义关卡按钮
        edit_color = self.colors["btn_hover"] if self.edit_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(self.screen, self.edit_btn, '编辑关卡', edit_color)

        pygame.display.update()

    def handle_events(self) -> Optional[Tuple[str, str]]:
        """处理关卡选择界面事件"""
        mx, my = pygame.mouse.get_pos()
        visible_levels, has_scroll = self.get_visible_levels()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # 鼠标点击事件
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 返回按钮
                if self.back_btn.collidepoint(mx, my):
                    return ("MAIN_MENU", "")

                # 编辑关卡按钮
                if self.edit_btn.collidepoint(mx, my):
                    next_state = self.level_editor.run()
                    if next_state == "LEVEL_SELECT":
                        return ("LEVEL_SELECT", "")  # 刷新关卡列表

                # 点击关卡卡片进入游戏
                for idx, level in enumerate(visible_levels):
                    row = idx // self.cards_per_row
                    col = idx % self.cards_per_row
                    x = self.screen_width // 2 - (self.cards_per_row * (
                                self.card_width + self.card_spacing) - self.card_spacing) // 2 + col * (
                                    self.card_width + self.card_spacing)
                    y = 100 + row * (self.card_height + self.card_spacing)
                    card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
                    if card_rect.collidepoint(mx, my):
                        return ("PLAY_LEVEL", level["level_id"])

                # 滚动控制（点击滚动指示器）
                if has_scroll:
                    total_pages = (len(self.level_manager.get_all_levels()) + self.cards_per_row * 2 - 1) // (
                                self.cards_per_row * 2)
                    indicator_width = 100
                    indicator_x = self.screen_width // 2 - indicator_width // 2
                    indicator_y = self.screen_height - 50
                    indicator_rect = pygame.Rect(indicator_x, indicator_y, indicator_width, 8)
                    if indicator_rect.collidepoint(mx, my):
                        page = (mx - indicator_x) // (indicator_width // total_pages)
                        self.scroll_offset = max(0, min(total_pages - 1, page))

            # 滚轮控制滚动
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 4 and has_scroll:  # 上滚
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif event.button == 5 and has_scroll:  # 下滚
                    total_pages = (len(self.level_manager.get_all_levels()) + self.cards_per_row * 2 - 1) // (
                                self.cards_per_row * 2)
                    self.scroll_offset = min(total_pages - 1, self.scroll_offset + 1)

        return None

    def run(self):
        """运行关卡选择界面主循环"""
        while True:
            self.draw_ui()
            next_state = self.handle_events()
            if next_state:
                return next_state
            pygame.time.Clock().tick(60)