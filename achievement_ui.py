# achievement_ui.py - 修复图标显示和进度刷新问题
import pygame
from ui import show_text, draw_button
from achievements import achievement_system


class AchievementUI:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.update_colors()

        # 按钮位置调整
        self.back_btn = pygame.Rect(10, 10, 40, 40)
        self.refresh_btn = pygame.Rect(self.screen_width - 150, 10, 140, 40)
        self.categories = ["全部", "进度", "技能", "里程碑", "挑战", "趣味"]
        self.current_category = "全部"

        # 布局参数
        self.card_width = 320
        self.card_height = 70
        self.cards_per_column = 5
        self.card_spacing = 10

    def update_colors(self):
        """使用固定颜色配置"""
        self.colors = {
            "bg": (210, 225, 235),
            "card_bg": (230, 240, 250),
            "card_locked": (200, 200, 200),
            "text_primary": (50, 70, 90),
            "text_secondary": (80, 100, 120),
            "unlocked": (100, 200, 100),
            "locked": (150, 150, 150),
            "progress_bg": (180, 180, 180),
            "progress_fill": (100, 180, 100)
        }

    def draw_achievement_card(self, achievement_id, definition, is_unlocked, position, size):
        """绘制成就卡片"""
        x, y = position
        width, height = size

        # 卡片背景
        card_rect = pygame.Rect(x, y, width, height)
        bg_color = self.colors["card_bg"] if is_unlocked else self.colors["card_locked"]
        pygame.draw.rect(self.screen, bg_color, card_rect, 0, 6)
        pygame.draw.rect(self.screen, self.colors["text_secondary"], card_rect, 1, 6)

        # 成就图标 - 修复图标显示
        icon_size = 30
        icon_rect = pygame.Rect(x + 10, y + 10, icon_size, icon_size)

        # 绘制图标背景
        icon_bg_color = self.colors["unlocked"] if is_unlocked else self.colors["locked"]
        pygame.draw.rect(self.screen, icon_bg_color, icon_rect, 0, 4)
        pygame.draw.rect(self.screen, self.colors["text_primary"], icon_rect, 1, 4)

        # 绘制图标文字 - 确保使用正确的字体
        try:
            # 尝试使用支持emoji的字体
            icon_font = pygame.font.SysFont("segoeuiemoji", 16)
            icon_surface = icon_font.render(definition["icon"], True, self.colors["text_primary"])
            icon_text_rect = icon_surface.get_rect(center=icon_rect.center)
            self.screen.blit(icon_surface, icon_text_rect)
        except:
            # 回退到系统字体
            show_text(self.screen, icon_rect.center, definition["icon"],
                      self.colors["text_primary"], font_size=16)

        # 成就信息
        name_color = self.colors["unlocked"] if is_unlocked else self.colors["locked"]
        show_text(self.screen, (x + 50, y + 15), definition["name"],
                  name_color, is_center=False, font_size=16)

        # 描述文字
        desc = definition["desc"]
        if len(desc) > 12:
            desc = desc[:12] + "..."
        show_text(self.screen, (x + 50, y + 35), desc,
                  self.colors["text_secondary"], is_center=False, font_size=12)

        # 解锁状态或进度条
        if is_unlocked:
            unlocked_data = achievement_system.get_unlocked_achievements().get(achievement_id, {})
            if unlocked_data and 'unlocked_at' in unlocked_data:
                date_str = unlocked_data['unlocked_at'][5:10]  # 提取月-日
                show_text(self.screen, (x + width - 40, y + height - 15),
                          date_str, self.colors["text_secondary"], is_center=False, font_size=10)
            else:
                show_text(self.screen, (x + width - 40, y + height - 15),
                          "已解锁", self.colors["unlocked"], is_center=False, font_size=10)
        else:
            progress = achievement_system.get_progress(achievement_id)

            # 进度条
            progress_bg_rect = pygame.Rect(x + width - 80, y + height - 20, 60, 8)
            pygame.draw.rect(self.screen, self.colors["progress_bg"], progress_bg_rect, 0, 4)

            if progress > 0:
                progress_width = max(6, int(60 * progress / 100))
                progress_rect = pygame.Rect(x + width - 80, y + height - 20, progress_width, 8)
                pygame.draw.rect(self.screen, self.colors["progress_fill"], progress_rect, 0, 4)

            show_text(self.screen, (x + width - 50, y + height - 16),
                      f"{int(progress)}%", self.colors["locked"], is_center=True, font_size=8)

        return card_rect

    def run(self):
        """运行成就界面"""
        clock = pygame.time.Clock()

        # 每次进入时更新颜色
        self.update_colors()

        # 初始加载数据
        achievement_system.load_game_data_from_scores()
        unlocked_achievements = achievement_system.get_unlocked_achievements()

        # 分类按钮
        category_btns = {}
        btn_width = 80
        btn_height = 30
        start_x = self.screen_width // 2 - (len(self.categories) * (btn_width + 5)) // 2

        for i, category in enumerate(self.categories):
            x = start_x + i * (btn_width + 5)
            category_btns[category] = pygame.Rect(x, 80, btn_width, btn_height)

        while True:
            # 使用当前主题颜色
            self.screen.fill(self.colors["bg"])

            # 标题
            show_text(self.screen, (self.screen_width // 2, 40),
                      "成就系统", self.colors["text_primary"], font_size=32)

            # 统计信息 - 实时更新
            total_achievements = len(achievement_system.achievement_definitions)
            unlocked_count = len(unlocked_achievements)
            completion_rate = (unlocked_count / total_achievements) * 100 if total_achievements > 0 else 0

            show_text(self.screen, (self.screen_width // 2, 65),
                      f"{unlocked_count}/{total_achievements} ({completion_rate:.1f}%)",
                      self.colors["text_secondary"], font_size=16)

            # 分类按钮
            mx, my = pygame.mouse.get_pos()
            for category, btn_rect in category_btns.items():
                is_active = (category == self.current_category)
                btn_color = self.colors["unlocked"] if is_active else self.colors["card_bg"]
                if btn_rect.collidepoint(mx, my) and not is_active:
                    btn_color = self.colors["card_locked"]

                draw_button(self.screen, btn_rect, category, btn_color, self.colors["text_primary"])

            # 刷新按钮
            refresh_color = self.colors["card_locked"] if self.refresh_btn.collidepoint(mx, my) else self.colors[
                "card_bg"]
            draw_button(self.screen, self.refresh_btn, '刷新数据', refresh_color, self.colors["text_primary"])

            # 成就列表
            filtered_achievements = []
            for achievement_id, definition in achievement_system.achievement_definitions.items():
                achievement_type = definition["type"]
                type_mapping = {
                    "progress": "进度", "skill": "技能", "milestone": "里程碑",
                    "challenge": "挑战", "endurance": "挑战", "fun": "趣味"
                }

                display_type = type_mapping.get(achievement_type, "其他")

                if (self.current_category == "全部" or
                        display_type == self.current_category):
                    filtered_achievements.append((achievement_id, definition))

            # 动态计算布局
            available_height = self.screen_height - 120
            max_cards_per_column = available_height // (self.card_height + self.card_spacing)
            actual_cards_per_column = min(max_cards_per_column, self.cards_per_column)

            num_columns = max(1, (len(filtered_achievements) + actual_cards_per_column - 1) // actual_cards_per_column)
            column_width = self.card_width + self.card_spacing

            total_width = num_columns * column_width - self.card_spacing
            start_x = (self.screen_width - total_width) // 2

            # 绘制成就卡片
            for col in range(num_columns):
                start_idx = col * actual_cards_per_column
                end_idx = min(start_idx + actual_cards_per_column, len(filtered_achievements))

                for row in range(end_idx - start_idx):
                    achievement_id, definition = filtered_achievements[start_idx + row]
                    is_unlocked = achievement_id in unlocked_achievements

                    x = start_x + col * column_width
                    y = 120 + row * (self.card_height + self.card_spacing)

                    self.draw_achievement_card(
                        achievement_id, definition, is_unlocked,
                        (x, y), (self.card_width, self.card_height)
                    )

            # 返回按钮
            back_color = self.colors["card_locked"] if self.back_btn.collidepoint(mx, my) else self.colors["card_bg"]
            draw_button(self.screen, self.back_btn, '←', back_color, self.colors["text_primary"])

            # 滚动提示
            if len(filtered_achievements) > actual_cards_per_column * num_columns:
                show_text(self.screen, (self.screen_width // 2, self.screen_height - 20),
                          "↑↓ 使用鼠标滚轮滚动", self.colors["text_secondary"], font_size=12)

            pygame.display.update()

            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.back_btn.collidepoint(event.pos):
                        return

                    if self.refresh_btn.collidepoint(event.pos):
                        # 刷新数据
                        achievement_system.load_game_data_from_scores()
                        unlocked_achievements = achievement_system.get_unlocked_achievements()
                        print("已刷新成就数据")

                    for category, btn_rect in category_btns.items():
                        if btn_rect.collidepoint(event.pos):
                            self.current_category = category

            clock.tick(60)