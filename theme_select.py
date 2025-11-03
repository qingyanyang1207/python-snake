import pygame
from ui import show_text, draw_button
from themes import THEMES, set_theme, get_current_theme


class ThemeSelect:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        # 使用固定背景色，不依赖主题
        self.bg_color = (210, 225, 235)
        self.text_color = (50, 70, 90)
        self.btn_normal = (150, 180, 210)
        self.btn_hover = (120, 160, 200)

    def draw_theme_preview(self, theme_data, position, size, is_selected=False):
        """绘制主题预览"""
        x, y = position
        width, height = size
        colors = theme_data["colors"]

        # 预览背景
        preview_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, colors["game_bg"], preview_rect, 0, 8)

        # 选中边框
        border_color = (255, 255, 0) if is_selected else self.text_color
        border_width = 3 if is_selected else 2
        pygame.draw.rect(self.screen, border_color, preview_rect, border_width, 8)

        # 主题名称
        show_text(self.screen, (x + width // 2, y + 20),
                  theme_data["name"], self.text_color, font_size=20)

        # 颜色样本展示 - 只显示游戏相关颜色
        sample_size = 15
        samples = [
            ("蛇头", colors["snake_head"]),
            ("蛇身", colors["snake_body"]),
            ("食物", colors["food_color"]),
            ("背景", colors["game_bg"])
        ]

        for i, (label, color) in enumerate(samples):
            sample_y = y + 50 + i * 25
            # 颜色方块
            pygame.draw.rect(self.screen, color, (x + 20, sample_y, sample_size, sample_size))
            pygame.draw.rect(self.screen, self.text_color, (x + 20, sample_y, sample_size, sample_size), 1)
            # 标签
            show_text(self.screen, (x + 45, sample_y + sample_size // 2),
                      label, self.text_color, is_center=False, font_size=12)

        return preview_rect

    def run(self):
        """运行主题选择界面"""
        clock = pygame.time.Clock()

        # 获取当前主题名称
        current_theme_name = None
        current_theme_colors = get_current_theme()
        for name, theme in THEMES.items():
            if theme["colors"] == current_theme_colors:
                current_theme_name = name
                break

        if current_theme_name is None:
            current_theme_name = "CLASSIC"

        back_btn = pygame.Rect(10, 10, 40, 40)
        apply_btn = pygame.Rect(self.screen_width - 120, self.screen_height - 60, 100, 40)

        theme_rects = {}
        selected_theme = current_theme_name

        while True:
            # 使用固定背景色
            self.screen.fill(self.bg_color)

            # 标题
            show_text(self.screen, (self.screen_width // 2, 60),
                      "选择主题", self.text_color, font_size=36)

            # 绘制主题预览
            theme_rects.clear()
            preview_size = (280, 150)
            spacing = 20
            start_x = self.screen_width // 2 - (2 * (preview_size[0] + spacing) - spacing) // 2
            start_y = 120

            for i, (theme_id, theme_data) in enumerate(THEMES.items()):
                row = i // 2
                col = i % 2
                x = start_x + col * (preview_size[0] + spacing)
                y = start_y + row * (preview_size[1] + spacing)

                is_selected = (theme_id == selected_theme)
                rect = self.draw_theme_preview(theme_data, (x, y), preview_size, is_selected)
                theme_rects[theme_id] = rect

            # 按钮
            mx, my = pygame.mouse.get_pos()

            # 返回按钮
            back_color = self.btn_hover if back_btn.collidepoint(mx, my) else self.btn_normal
            draw_button(self.screen, back_btn, '←', back_color, self.text_color)

            # 应用按钮
            apply_color = self.btn_hover if apply_btn.collidepoint(mx, my) else self.btn_normal
            draw_button(self.screen, apply_btn, '应用主题', apply_color, self.text_color)

            pygame.display.update()

            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_btn.collidepoint(event.pos):
                        return "BACK"

                    if apply_btn.collidepoint(event.pos):
                        if set_theme(selected_theme):
                            return "APPLIED"

                    # 主题选择
                    for theme_id, rect in theme_rects.items():
                        if rect.collidepoint(event.pos):
                            selected_theme = theme_id

            clock.tick(60)