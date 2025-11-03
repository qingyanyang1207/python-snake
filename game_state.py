import pygame
import sys
from score_manage import save_score, get_rankings
from moudle.snake import Snake
from moudle.food import Food
from ui import show_text, draw_button
from sound import SoundManager
from time_manager import TimeManager
from analysis import GameAnalysis
from level_manage import LevelManager
from level_select import LevelSelect
from achievement_ui import AchievementUI


class GameState:
    # 游戏状态定义
    MAIN_MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    RANKING = 3
    PAUSED = 4
    ANALYSIS = 5
    LEVEL_SELECT = 6
    PLAY_LEVEL = 7
    EVOLUTION_MODE = 8

    def __init__(self, screen):
        self.screen = screen
        self.state = self.MAIN_MENU
        self.prev_state = self.MAIN_MENU
        self.snake = Snake()
        self.food = Food()
        self.scores = 0
        self.isdead = False
        self.score_saved = False
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.level_manager = LevelManager()
        self.level_select = LevelSelect(screen)
        self.current_level = None
        self.level_time_used = 0
        self.evolution_level = 0
        self.special_abilities = []
        self.evolution_timer = 0

        self.screen_width, self.screen_height = screen.get_size()
        self.food.set(self.screen_width, self.screen_height, self.snake.body)

        self.bgm_btn = pygame.Rect(self.screen_width - 90, 10, 40, 40)
        self.pause_btn = pygame.Rect(self.screen_width - 40, 10, 40, 40)
        self.back_btn = pygame.Rect(10, 10, 40, 40)

        # 颜色配置
        self.colors = {
            # 背景色
            "game_bg": (220, 230, 240),  # 这个会被主题覆盖
            "pause_bg": (210, 225, 235),
            "main_menu_bg": (210, 225, 235),
            "ranking_bg": (210, 225, 235),
            # 按钮色
            "btn_normal": (150, 180, 210),
            "btn_hover": (120, 160, 200),
            # 文字色
            "text_title": (50, 70, 90),
            "text_normal": (50, 70, 90),
            "text_menu": (50, 70, 90),
            "text_info": (50, 70, 90),
            "text_warning": (180, 60, 60),
            "game_over_title": (180, 60, 60),
            "text_primary": (50, 70, 90),  # 确保这个键存在
            # 游戏元素色（这些会被主题覆盖）
            "snake_body": (120, 160, 200),
            "snake_head": (90, 140, 190),
            "food_color": (251, 192, 45),
            "obstacle": (180, 60, 60),
            # 排行榜色
            "ranking_header": (150, 180, 210),
            "ranking_row_odd": (200, 215, 230),
            "ranking_row_even": (190, 205, 220),
            # 面板色
            "panel_bg": (180, 200, 220, 180),
            "score_panel_bg": (180, 200, 220, 200)
        }

        self.sound_manager.play_bgm()

        self.time_manager = TimeManager()
        self.analysis = GameAnalysis(screen)
        self.ranking_scroll_offset = 0

    def handle_playing(self):
        screen = self.screen
        self.update_theme_colors()
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # 正常方向控制
                self.snake.changedirection(event.key)
                # 空格键重新开始（游戏结束时）
                if event.key == pygame.K_SPACE and self.isdead:
                    self.reset_game()
                # P键暂停/继续
                if event.key == pygame.K_p:
                    if self.state == self.PLAYING:
                        self.enter_pause()
                    elif self.state == self.PAUSED:
                        self.exit_pause()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # BGM按钮控制
                if self.bgm_btn.collidepoint(mx, my) and self.sound_manager.is_bgm_loaded():
                    self.sound_manager.toggle_bgm()
                # 暂停按钮控制
                if self.pause_btn.collidepoint(mx, my):
                    self.enter_pause()
                # 返回主菜单按钮控制
                if self.back_btn.collidepoint(mx, my):
                    self.prev_state = self.PLAYING
                    self.state = self.MAIN_MENU
                    self.time_manager.pause()

        screen.fill(self.colors["game_bg"])

        # 返回按钮
        back_btn_color = self.colors["btn_hover"] if self.back_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(screen, self.back_btn, '←', back_btn_color)
        # BGM按钮（根据播放状态显示图标）
        bgm_btn_color = self.colors["btn_hover"] if self.bgm_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        bgm_icon = "▶" if not self.sound_manager.is_bgm_playing() and self.sound_manager.is_bgm_loaded() else "■" if self.sound_manager.is_bgm_loaded() else "?"
        draw_button(screen, self.bgm_btn, bgm_icon, bgm_btn_color)
        # 暂停按钮
        pause_btn_color = self.colors["btn_hover"] if self.pause_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(screen, self.pause_btn, '||', pause_btn_color)

        # 左下角分数与时间面板
        info_bg_rect = pygame.Rect(10, self.screen_height - 80, 300, 70)
        info_surface = pygame.Surface((info_bg_rect.width, info_bg_rect.height), pygame.SRCALPHA)
        info_surface.fill(self.colors["score_panel_bg"])
        screen.blit(info_surface, (info_bg_rect.x, info_bg_rect.y))
        pygame.draw.rect(screen, (180, 200, 220), info_bg_rect, 1)
        # 显示分数
        show_text(screen, (20, self.screen_height - 70), f'分数: {self.scores}',
                  self.colors["text_normal"], is_center=False, font_size=24)
        # 显示时间
        show_text(screen, (20, self.screen_height - 40), f'时间: {self.time_manager.get_formatted_time()}',
                  self.colors["text_normal"], is_center=False, font_size=24)

        # 游戏逻辑（未死亡时）
        if not self.isdead:
            self.scores += 1  # 每帧加1分
            self.snake.move()  # 蛇移动

            # 检测吃到普通食物
            if self.snake.body[0].colliderect(self.food.rect):
                self.scores += 50  # 吃到食物加50分
                self.snake.grow()  # 蛇增长
                self.food.set(self.screen_width, self.screen_height, self.snake.body)  # 生成新食物
                self.sound_manager.play_eat_sound()  # 播放吃食物音效
            else:
                self.snake.remove_tail()  # 未吃到食物则移除尾部

        # 绘制蛇
        for i, rect in enumerate(self.snake.body):
            color = self.colors["snake_head"] if i == 0 else self.colors["snake_body"]
            pygame.draw.rect(screen, color, rect, 0, 2)
            pygame.draw.rect(screen, (180, 200, 220, 30), rect, 1, 2)

        # 死亡检测与处理
        self.isdead = self.snake.isdead(self.screen_width, self.screen_height)
        if self.isdead:
            if not self.score_saved:
                # 保存分数数据
                game_time = self.time_manager.get_elapsed()
                end_time = self.time_manager.get_game_end_time()
                save_score(f"{self.scores},{game_time},{end_time}")
                self.score_saved = True
                self.sound_manager.play_death_sound()  # 播放死亡音效

            # 游戏结束面板
            death_bg_rect = pygame.Rect(
                (self.screen_width - 400) // 2,
                (self.screen_height - 180) // 2,
                400, 180
            )
            death_surface = pygame.Surface((death_bg_rect.width, death_bg_rect.height), pygame.SRCALPHA)
            death_surface.fill(self.colors["panel_bg"])
            screen.blit(death_surface, (death_bg_rect.x, death_bg_rect.y))
            pygame.draw.rect(screen, (180, 200, 220), death_bg_rect, 2)

            # 显示游戏结束文字
            show_text(screen, (self.screen_width // 2, death_bg_rect.y + 50),
                      '游戏结束!', self.colors["game_over_title"], is_center=True, font_size=60)
            show_text(screen, (self.screen_width // 2, death_bg_rect.y + 100),
                      f'最终分数: {self.scores}', self.colors["text_normal"], is_center=True, font_size=30)
            show_text(screen, (self.screen_width // 2, death_bg_rect.y + 140),
                      '按空格键重新开始', self.colors["text_normal"], is_center=True, font_size=24)

        # 绘制普通食物
        pygame.draw.rect(screen, self.colors["food_color"], self.food.rect, 0, 3)

        # 更新屏幕显示
        pygame.display.update()
        self.clock.tick(10)  # 控制游戏速度
        if self.isdead and not self.score_saved:
            # 保存分数数据
            game_time = self.time_manager.get_elapsed()
            end_time = self.time_manager.get_game_end_time()
            save_score(f"{self.scores},{game_time},{end_time}")
            self.score_saved = True
            self.sound_manager.play_death_sound()

            # 更新成就系统
            game_data = {
                "score": self.scores,
                "time": game_time,
                "session_duration": game_time  # 使用游戏时间作为会话时长
            }
            new_achievements = self.achievement_system.update_stats(game_data)

            # 显示新成就通知
            if new_achievements:
                self.show_achievement_notification(new_achievements[0])

    def handle_ranking(self):
        """处理排行榜界面逻辑"""
        self.update_theme_colors()
        screen = self.screen
        rankings = get_rankings()
        # 填充排行榜背景
        screen.fill(self.colors["ranking_bg"])

        # 排行榜主体区域
        content_rect = pygame.Rect(
            20, 80,
            self.screen_width - 40,
            self.screen_height - 100
        )
        content_surface = pygame.Surface((content_rect.width, content_rect.height), pygame.SRCALPHA)
        content_surface.fill(self.colors["game_bg"])
        screen.blit(content_surface, (content_rect.x, content_rect.y))
        pygame.draw.rect(screen, (180, 200, 220), content_rect, 1)

        # 鼠标位置获取
        mx, my = pygame.mouse.get_pos()

        # 绘制功能按钮
        # 返回按钮
        back_btn_color = self.colors["btn_hover"] if self.back_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(screen, self.back_btn, '←', back_btn_color)
        # BGM按钮
        bgm_btn_color = self.colors["btn_hover"] if self.bgm_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        bgm_icon = "▶" if not self.sound_manager.is_bgm_playing() and self.sound_manager.is_bgm_loaded() else "■" if self.sound_manager.is_bgm_loaded() else "?"
        draw_button(screen, self.bgm_btn, bgm_icon, bgm_btn_color)

        # 排行榜标题
        show_text(screen, (self.screen_width // 2, 50), '本地排行',
                  self.colors["text_menu"], is_center=True, font_size=50)

        # 排行榜列宽配置
        col_widths = {
            "rank": int(content_rect.width * 0.15),
            "score": int(content_rect.width * 0.25),
            "time": int(content_rect.width * 0.25),
            "date": int(content_rect.width * 0.35)
        }
        table_top = 120
        row_height = 40
        max_visible_rows = (content_rect.height - 40) // row_height  # 可见行数
        base_x = content_rect.x  # 列起始X坐标

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # ESC键返回上一状态
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = self.prev_state if self.prev_state else self.MAIN_MENU
                self.ranking_scroll_offset = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 返回按钮点击
                if self.back_btn.collidepoint(mx, my):
                    self.state = self.prev_state if self.prev_state else self.MAIN_MENU
                    self.ranking_scroll_offset = 0
                # BGM按钮点击
                if self.bgm_btn.collidepoint(mx, my) and self.sound_manager.is_bgm_loaded():
                    self.sound_manager.toggle_bgm()
                # 滚轮控制滚动
                if event.button == 4:  # 上滚
                    self.ranking_scroll_offset = max(0, self.ranking_scroll_offset - 1)
                elif event.button == 5:  # 下滚
                    self.ranking_scroll_offset = min(len(rankings) - max_visible_rows,
                                                     self.ranking_scroll_offset + 1)

        # 绘制表头
        header_rect = pygame.Rect(base_x, table_top, content_rect.width, row_height)
        pygame.draw.rect(screen, self.colors["ranking_header"], header_rect, 0)
        # 表头文字
        show_text(screen, (base_x + col_widths["rank"] // 2, table_top + row_height // 2),
                  '排名', self.colors["text_menu"], is_center=True, font_size=24)
        show_text(screen, (base_x + col_widths["rank"] + col_widths["score"] // 2, table_top + row_height // 2),
                  '分数', self.colors["text_menu"], is_center=True, font_size=24)
        show_text(screen, (base_x + col_widths["rank"] + col_widths["score"] + col_widths["time"] // 2,
                           table_top + row_height // 2),
                  '时间(秒)', self.colors["text_menu"], is_center=True, font_size=24)
        show_text(screen,
                  (base_x + col_widths["rank"] + col_widths["score"] + col_widths["time"] + col_widths["date"] // 2,
                   table_top + row_height // 2),
                  '日期', self.colors["text_menu"], is_center=True, font_size=24)

        # 绘制排行榜内容（带滚动）
        visible_rankings = rankings[self.ranking_scroll_offset:self.ranking_scroll_offset + max_visible_rows]
        for idx, item in enumerate(visible_rankings):
            score, time, date = item
            y_pos = table_top + row_height + idx * row_height
            # 行背景色（奇偶行区分）
            row_color = self.colors["ranking_row_odd"] if idx % 2 == 0 else self.colors["ranking_row_even"]
            row_rect = pygame.Rect(base_x, y_pos, content_rect.width, row_height)
            pygame.draw.rect(screen, row_color, row_rect, 0)
            # 行内容文字
            show_text(screen, (base_x + col_widths["rank"] // 2, y_pos + row_height // 2),
                      f'{self.ranking_scroll_offset + idx + 1}', self.colors["text_normal"], is_center=True,
                      font_size=22)
            show_text(screen, (base_x + col_widths["rank"] + col_widths["score"] // 2, y_pos + row_height // 2),
                      f'{score}', self.colors["text_normal"], is_center=True, font_size=22)
            show_text(screen, (base_x + col_widths["rank"] + col_widths["score"] + col_widths["time"] // 2,
                               y_pos + row_height // 2),
                      f'{time}', self.colors["text_normal"], is_center=True, font_size=22)
            show_text(screen,
                      (base_x + col_widths["rank"] + col_widths["score"] + col_widths["time"] + col_widths["date"] // 2,
                       y_pos + row_height // 2),
                      f'{date}', self.colors["text_normal"], is_center=True, font_size=22)

        # 无排行榜数据提示
        if not rankings:
            empty_rect = pygame.Rect(
                (self.screen_width - 300) // 2,
                (self.screen_height - 80) // 2,
                300, 80
            )
            pygame.draw.rect(screen, self.colors["ranking_row_odd"], empty_rect, 0)
            pygame.draw.rect(screen, (180, 200, 220), empty_rect, 1)
            show_text(screen, (self.screen_width // 2, self.screen_height // 2),
                      '暂无游戏记录', self.colors["text_normal"], is_center=True, font_size=36)

        # 绘制滚动条（有数据且超出可见行数时）
        if len(rankings) > max_visible_rows:
            scrollbar_height = (max_visible_rows / len(rankings)) * content_rect.height
            scrollbar_y = table_top + (self.ranking_scroll_offset / len(rankings)) * content_rect.height
            scrollbar_rect = pygame.Rect(
                content_rect.right - 10,
                scrollbar_y,
                8,
                scrollbar_height
            )
            pygame.draw.rect(screen, (150, 180, 210), scrollbar_rect, 0, 4)

        # 更新屏幕显示
        pygame.display.update()

    def handle_main_menu(self):
        """处理主菜单界面逻辑（优化排版和主题同步）"""
        screen = self.screen

        # 每次进入主菜单时更新主题颜色
        self.update_theme_colors()
        screen.fill(self.colors["main_menu_bg"])

        # 主菜单标题（上移）
        show_text(screen, (self.screen_width // 2, self.screen_height // 6),
                  '贪吃蛇游戏', self.colors["text_title"], is_center=True, font_size=50)

        # 菜单按钮配置（紧凑布局）
        button_width = 180
        button_height = 45
        button_y = self.screen_height // 3
        button_spacing = 55

        # 按钮位置（两列布局）
        left_column_x = self.screen_width // 2 - button_width - 20
        right_column_x = self.screen_width // 2 + 20

        # 左列按钮
        start_btn = pygame.Rect(left_column_x, button_y, button_width, button_height)
        level_btn = pygame.Rect(left_column_x, button_y + button_spacing, button_width, button_height)
        evolution_btn = pygame.Rect(left_column_x, button_y + button_spacing * 2, button_width, button_height)  # 新增进化模式
        exit_btn = pygame.Rect(left_column_x, button_y + button_spacing * 3, button_width, button_height)

        # 右列按钮
        theme_btn = pygame.Rect(right_column_x, button_y, button_width, button_height)
        rank_btn = pygame.Rect(right_column_x, button_y + button_spacing, button_width, button_height)
        analysis_btn = pygame.Rect(right_column_x, button_y + button_spacing * 2, button_width, button_height)
        achievement_btn = pygame.Rect(right_column_x, button_y + button_spacing * 3, button_width, button_height)

        # 鼠标位置获取
        mx, my = pygame.mouse.get_pos()

        # 按钮颜色
        start_color = self.colors["btn_hover"] if start_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        level_color = self.colors["btn_hover"] if level_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        evolution_color = self.colors["btn_hover"] if evolution_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        theme_color = self.colors["btn_hover"] if theme_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        rank_color = self.colors["btn_hover"] if rank_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        analysis_color = self.colors["btn_hover"] if analysis_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        achievement_color = self.colors["btn_hover"] if achievement_btn.collidepoint(mx, my) else self.colors[
            "btn_normal"]
        exit_color = self.colors["btn_hover"] if exit_btn.collidepoint(mx, my) else self.colors["btn_normal"]

        # 绘制菜单按钮（包含进化模式）
        draw_button(screen, start_btn, '开始游戏', start_color)
        draw_button(screen, level_btn, '闯关模式', level_color)
        draw_button(screen, evolution_btn, '进化模式', evolution_color)  # 确保这行存在
        draw_button(screen, theme_btn, '主题切换', theme_color)
        draw_button(screen, rank_btn, '本地排行', rank_color)
        draw_button(screen, analysis_btn, '数据分析', analysis_color)
        draw_button(screen, achievement_btn, '成就系统', achievement_color)
        draw_button(screen, exit_btn, '退出游戏', exit_color)

        # 绘制BGM按钮
        bgm_btn_color = self.colors["btn_hover"] if self.bgm_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        bgm_icon = "?" if not self.sound_manager.is_bgm_playing() and self.sound_manager.is_bgm_loaded() else "■" if self.sound_manager.is_bgm_loaded() else "?"
        draw_button(screen, self.bgm_btn, bgm_icon, bgm_btn_color)

        # 更新屏幕显示
        pygame.display.update()

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 开始游戏（自由模式）
                if start_btn.collidepoint(mx, my):
                    self.state = self.PLAYING
                    self.prev_state = self.MAIN_MENU
                    self.reset_game()
                    self.time_manager.start()
                # 闯关模式
                if level_btn.collidepoint(mx, my):
                    self.state = self.LEVEL_SELECT
                    self.prev_state = self.MAIN_MENU
                # 进化模式（新增）
                if evolution_btn.collidepoint(mx, my):
                    self.state = self.EVOLUTION_MODE
                    self.prev_state = self.MAIN_MENU
                    self.reset_evolution_game()
                # 主题切换
                if theme_btn.collidepoint(mx, my):
                    from theme_select import ThemeSelect
                    theme_select = ThemeSelect(self.screen)
                    result = theme_select.run()
                    if result == "APPLIED":
                        # 主题已更改，强制刷新颜色
                        self.update_theme_colors()
                # 本地排行
                if rank_btn.collidepoint(mx, my):
                    self.prev_state = self.MAIN_MENU
                    self.state = self.RANKING
                # 数据分析
                if analysis_btn.collidepoint(mx, my):
                    self.prev_state = self.MAIN_MENU
                    self.state = self.ANALYSIS
                # 成就系统
                if achievement_btn.collidepoint(mx, my):
                    from achievement_ui import AchievementUI
                    achievement_ui = AchievementUI(self.screen)
                    achievement_ui.run()
                # 退出游戏
                if exit_btn.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()
                # BGM控制
                if self.bgm_btn.collidepoint(mx, my) and self.sound_manager.is_bgm_loaded():
                    self.sound_manager.toggle_bgm()

    def handle_paused(self):
        """处理游戏暂停界面逻辑"""
        screen = self.screen
        # 填充暂停背景
        screen.fill(self.colors["pause_bg"])

        # 暂停面板
        panel_rect = pygame.Rect(
            (self.screen_width - 300) // 2,
            (self.screen_height - 200) // 2,
            300, 200
        )
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.colors["panel_bg"])
        screen.blit(panel_surface, (panel_rect.x, panel_rect.y))
        pygame.draw.rect(screen, (180, 200, 220), panel_rect, 2)

        # 暂停标题
        show_text(screen, (self.screen_width // 2, panel_rect.y + 50),
                  '游戏暂停', self.colors["text_title"], is_center=True, font_size=40)

        # 暂停界面按钮
        button_width = 150
        button_height = 40
        button_y = panel_rect.y + 110
        button_spacing = 60
        # 继续游戏按钮
        resume_btn = pygame.Rect((self.screen_width - button_width) // 2, button_y, button_width, button_height)
        # 返回菜单按钮
        menu_btn = pygame.Rect((self.screen_width - button_width) // 2, button_y + button_spacing, button_width,
                               button_height)

        # 鼠标位置获取
        mx, my = pygame.mouse.get_pos()

        # 按钮颜色（hover状态变化）
        resume_color = self.colors["btn_hover"] if resume_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        menu_color = self.colors["btn_hover"] if menu_btn.collidepoint(mx, my) else self.colors["btn_normal"]

        # 绘制按钮
        draw_button(screen, resume_btn, '继续游戏', resume_color)
        draw_button(screen, menu_btn, '返回菜单', menu_color)

        # 绘制BGM按钮
        bgm_btn_color = self.colors["btn_hover"] if self.bgm_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        bgm_icon = "▶" if not self.sound_manager.is_bgm_playing() and self.sound_manager.is_bgm_loaded() else "■" if self.sound_manager.is_bgm_loaded() else "?"
        draw_button(screen, self.bgm_btn, bgm_icon, bgm_btn_color)

        # 更新屏幕显示
        pygame.display.update()

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # P键或ESC键继续游戏
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    self.exit_pause()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 继续游戏
                if resume_btn.collidepoint(mx, my):
                    self.exit_pause()
                # 返回主菜单
                if menu_btn.collidepoint(mx, my):
                    self.state = self.MAIN_MENU
                # BGM控制
                if self.bgm_btn.collidepoint(mx, my) and self.sound_manager.is_bgm_loaded():
                    self.sound_manager.toggle_bgm()

    def handle_analysis(self):
        """处理数据分析界面逻辑"""
        # 调用数据分析模块，返回后切换到主菜单
        next_state = self.analysis.run()
        if next_state == "MAIN_MENU":
            self.state = self.MAIN_MENU
            self.prev_state = self.ANALYSIS

    def reset_game(self):
        """重置游戏状态"""
        self.snake = Snake()
        self.food = Food()
        self.food.set(self.screen_width, self.screen_height, self.snake.body)
        self.scores = 0
        self.isdead = False
        self.score_saved = False
        self.time_manager.start()

    def enter_pause(self):
        """进入暂停状态"""
        self.prev_state = self.PLAYING if self.state == self.PLAYING else self.PLAY_LEVEL
        self.state = self.PAUSED
        self.time_manager.pause()

    def exit_pause(self):
        """退出暂停状态"""
        self.state = self.prev_state
        self.time_manager.resume()

    def handle_level_select(self):
        next_state, level_id = self.level_select.run()
        if next_state == "MAIN_MENU":
            self.state = self.MAIN_MENU
        elif next_state == "PLAY_LEVEL" and level_id:
            self.state = self.PLAY_LEVEL
            self.load_level(level_id)  # 加载选中的关卡

    def load_level(self, level_id: str):
        """加载关卡数据并初始化游戏状态"""
        self.current_level = self.level_manager.get_level_by_id(level_id)
        if not self.current_level:
            self.state = self.LEVEL_SELECT
            return

        # 重置游戏状态
        self.snake = Snake()
        self.food = Food()
        self.food.set(self.screen_width, self.screen_height, self.snake.body, self.current_level["obstacles"])  # 传入障碍物
        self.scores = 0
        self.isdead = False
        self.score_saved = False
        self.time_manager.start()
        self.level_time_used = 0

        # 设置关卡速度（覆盖默认10FPS）
        self.game_speed = self.current_level["speed"]

    def handle_play_level(self):
        """处理闯关模式游戏进行中的逻辑"""
        if not self.current_level:
            self.state = self.LEVEL_SELECT
            return

        screen = self.screen
        mx, my = pygame.mouse.get_pos()
        level = self.current_level

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.snake.changedirection(event.key)
                # 空格键重新开始（关卡失败/通关后）
                if event.key == pygame.K_SPACE and (self.isdead or self.scores >= level["score_target"]):
                    self.load_level(level["level_id"])
                # P键暂停/继续
                if event.key == pygame.K_p:
                    if self.state == self.PLAY_LEVEL:
                        self.enter_pause()
                    elif self.state == self.PAUSED:
                        self.exit_pause()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 按钮逻辑
                if self.bgm_btn.collidepoint(mx, my) and self.sound_manager.is_bgm_loaded():
                    self.sound_manager.toggle_bgm()
                if self.pause_btn.collidepoint(mx, my):
                    self.enter_pause()
                if self.back_btn.collidepoint(mx, my):
                    self.prev_state = self.PLAY_LEVEL
                    self.state = self.LEVEL_SELECT
                    self.time_manager.pause()

        # 填充背景
        screen.fill(self.colors["game_bg"])

        # 绘制UI元素
        # 返回按钮
        back_btn_color = self.colors["btn_hover"] if self.back_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(screen, self.back_btn, '←', back_btn_color)
        # BGM按钮
        bgm_btn_color = self.colors["btn_hover"] if self.bgm_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        bgm_icon = "▶" if not self.sound_manager.is_bgm_playing() and self.sound_manager.is_bgm_loaded() else "■" if self.sound_manager.is_bgm_loaded() else "?"
        draw_button(screen, self.bgm_btn, bgm_icon, bgm_btn_color)
        # 暂停按钮
        pause_btn_color = self.colors["btn_hover"] if self.pause_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(screen, self.pause_btn, '||', pause_btn_color)

        # 关卡信息面板（新增）
        level_panel_rect = pygame.Rect(self.screen_width - 300, 10, 290, 100)
        panel_surface = pygame.Surface((level_panel_rect.width, level_panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.colors["score_panel_bg"])
        screen.blit(panel_surface, (level_panel_rect.x, level_panel_rect.y))
        pygame.draw.rect(screen, (180, 200, 220), level_panel_rect, 1)
        # 关卡名称
        show_text(screen, (level_panel_rect.x + 10, level_panel_rect.y + 20), f'关卡：{level["name"]}',
                  self.colors["text_normal"], is_center=False, font_size=20)
        # 剩余时间
        self.level_time_used = self.time_manager.get_elapsed()
        time_left = max(0, level["time_limit"] - self.level_time_used)
        time_color = self.colors["text_warning"] if time_left < 10 else self.colors["text_normal"]
        show_text(screen, (level_panel_rect.x + 10, level_panel_rect.y + 50),
                  f'剩余时间：{time_left // 60:02d}:{time_left % 60:02d}',
                  time_color, is_center=False, font_size=20)
        # 分数进度
        progress = min(100, (self.scores / level["score_target"]) * 100)
        show_text(screen, (level_panel_rect.x + 10, level_panel_rect.y + 80), f'分数进度：{progress:.0f}%',
                  self.colors["text_normal"], is_center=False, font_size=20)

        # 左下角分数面板
        info_bg_rect = pygame.Rect(10, self.screen_height - 80, 300, 70)
        info_surface = pygame.Surface((info_bg_rect.width, info_bg_rect.height), pygame.SRCALPHA)
        info_surface.fill(self.colors["score_panel_bg"])
        screen.blit(info_surface, (info_bg_rect.x, info_bg_rect.y))
        pygame.draw.rect(screen, (180, 200, 220), info_bg_rect, 1)
        show_text(screen, (20, self.screen_height - 70), f'当前分数: {self.scores}',
                  self.colors["text_normal"], is_center=False, font_size=24)
        show_text(screen, (20, self.screen_height - 40), f'目标分数: {level["score_target"]}',
                  self.colors["text_normal"], is_center=False, font_size=24)

        # 游戏逻辑（未死亡、未通关时）
        # 在 handle_play_level 方法的游戏逻辑部分修改
        if not self.isdead and self.scores < level["score_target"] and self.level_time_used < level["time_limit"]:
            self.snake.move()  # 先移动再检测碰撞（关键修改）
            self.scores += 1  # 每帧加1分

            # 检测撞墙（加强判定）
            head = self.snake.body[0]
            if (head.x < 0 or head.x >= self.screen_width or
                    head.y < 0 or head.y >= self.screen_height):
                self.isdead = True
                self.sound_manager.play_death_sound()  # 立即播放死亡音效
                return  # 一旦撞墙直接结束本轮逻辑

            # 检测吃到食物
            if head.colliderect(self.food.rect):
                self.scores += 50
                self.snake.grow()
                self.food.set(self.screen_width, self.screen_height, self.snake.body, level["obstacles"])
                self.sound_manager.play_eat_sound()
            else:
                self.snake.remove_tail()

            # 检测碰撞障碍物
            for obstacle in level["obstacles"]:
                obs_rect = pygame.Rect(*obstacle)
                if head.colliderect(obs_rect):
                    self.isdead = True
                    self.sound_manager.play_death_sound()
                    break

        # 绘制障碍物
        for obstacle in level["obstacles"]:
            pygame.draw.rect(screen, self.colors["text_warning"], obstacle, 0, 3)
            pygame.draw.rect(screen, (0, 0, 0), obstacle, 1, 3)

        # 绘制蛇
        for i, rect in enumerate(self.snake.body):
            color = self.colors["snake_head"] if i == 0 else self.colors["snake_body"]
            pygame.draw.rect(screen, color, rect, 0, 2)
            pygame.draw.rect(screen, (180, 200, 220, 30), rect, 1, 2)

        # 绘制食物
        pygame.draw.rect(screen, self.colors["food_color"], self.food.rect, 0, 3)

        # 通关检测
        if self.scores >= level["score_target"] and not self.score_saved:
            # 保存关卡分数
            self.level_manager.save_level_score(level["level_id"], self.scores, self.level_time_used)
            self.score_saved = True
            self.sound_manager.play_eat_sound()  # 播放通关音效

            # 通关面板
            pass_panel_rect = pygame.Rect(
                (self.screen_width - 400) // 2,
                (self.screen_height - 180) // 2,
                400, 180
            )
            pass_surface = pygame.Surface((pass_panel_rect.width, pass_panel_rect.height), pygame.SRCALPHA)
            pass_surface.fill(self.colors["panel_bg"])
            screen.blit(pass_surface, (pass_panel_rect.x, pass_panel_rect.y))
            pygame.draw.rect(screen, (0, 120, 0), pass_panel_rect, 2)
            show_text(screen, (self.screen_width // 2, pass_panel_rect.y + 50),
                      '关卡通关!', (0, 120, 0), is_center=True, font_size=60)
            show_text(screen, (self.screen_width // 2, pass_panel_rect.y + 100),
                      f'得分：{self.scores} 用时：{self.level_time_used // 60:02d}:{self.level_time_used % 60:02d}',
                      self.colors["text_normal"], is_center=True, font_size=30)
            show_text(screen, (self.screen_width // 2, pass_panel_rect.y + 140),
                      '按空格键重新挑战', self.colors["text_normal"], is_center=True, font_size=24)

        # 失败检测（死亡或超时）
        if (self.isdead or self.level_time_used >= level["time_limit"]) and not self.score_saved:
            self.score_saved = True
            if self.isdead:
                self.sound_manager.play_death_sound()

            # 失败面板
            fail_panel_rect = pygame.Rect(
                (self.screen_width - 400) // 2,
                (self.screen_height - 180) // 2,
                400, 180
            )
            fail_surface = pygame.Surface((fail_panel_rect.width, fail_panel_rect.height), pygame.SRCALPHA)
            fail_surface.fill(self.colors["panel_bg"])
            screen.blit(fail_surface, (fail_panel_rect.x, fail_panel_rect.y))
            pygame.draw.rect(screen, self.colors["text_warning"], fail_panel_rect, 2)

            fail_text = '碰撞障碍物!' if self.isdead else '时间耗尽!'
            show_text(screen, (self.screen_width // 2, fail_panel_rect.y + 50),
                      fail_text, self.colors["game_over_title"], is_center=True, font_size=60)
            show_text(screen, (self.screen_width // 2, fail_panel_rect.y + 100),
                      f'当前得分：{self.scores}', self.colors["text_normal"], is_center=True, font_size=30)
            show_text(screen, (self.screen_width // 2, fail_panel_rect.y + 140),
                      '按空格键重新挑战', self.colors["text_normal"], is_center=True, font_size=24)

        # 更新屏幕
        pygame.display.update()
        self.clock.tick(self.game_speed)  # 使用关卡自定义速度

    def handle_evolution_mode(self):
        """处理进化模式游戏逻辑"""
        if not hasattr(self, 'evolution_mode'):
            from evolution_mode import EvolutionMode
            self.evolution_mode = EvolutionMode(self.screen)

        # 使用进化模式的特殊逻辑
        screen = self.screen
        self.update_theme_colors()
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self.snake.changedirection(event.key)
                # 空格键重新开始（游戏结束时）
                if event.key == pygame.K_SPACE and self.isdead:
                    self.reset_evolution_game()
                # P键暂停/继续
                if event.key == pygame.K_p:
                    if self.state == self.EVOLUTION_MODE:
                        self.enter_pause()
                    elif self.state == self.PAUSED:
                        self.exit_pause()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # BGM按钮控制
                if self.bgm_btn.collidepoint(mx, my) and self.sound_manager.is_bgm_loaded():
                    self.sound_manager.toggle_bgm()
                # 暂停按钮控制
                if self.pause_btn.collidepoint(mx, my):
                    self.enter_pause()
                # 返回主菜单按钮控制
                if self.back_btn.collidepoint(mx, my):
                    self.prev_state = self.EVOLUTION_MODE
                    self.state = self.MAIN_MENU
                    self.time_manager.pause()

        screen.fill(self.colors["game_bg"])

        # 返回按钮（确保在最上层）
        back_btn_color = self.colors["btn_hover"] if self.back_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(screen, self.back_btn, '←', back_btn_color)
        # BGM按钮
        bgm_btn_color = self.colors["btn_hover"] if self.bgm_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        bgm_icon = "▶" if not self.sound_manager.is_bgm_playing() and self.sound_manager.is_bgm_loaded() else "■" if self.sound_manager.is_bgm_loaded() else "?"
        draw_button(screen, self.bgm_btn, bgm_icon, bgm_btn_color)
        # 暂停按钮
        pause_btn_color = self.colors["btn_hover"] if self.pause_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(screen, self.pause_btn, '||', pause_btn_color)

        # 左下角分数与时间面板
        info_bg_rect = pygame.Rect(10, self.screen_height - 80, 300, 70)
        info_surface = pygame.Surface((info_bg_rect.width, info_bg_rect.height), pygame.SRCALPHA)
        info_surface.fill(self.colors["score_panel_bg"])
        screen.blit(info_surface, (info_bg_rect.x, info_bg_rect.y))
        pygame.draw.rect(screen, (180, 200, 220), info_bg_rect, 1)
        # 显示分数
        show_text(screen, (20, self.screen_height - 70), f'分数: {self.scores}',
                  self.colors["text_normal"], is_center=False, font_size=24)
        # 显示时间
        show_text(screen, (20, self.screen_height - 40), f'时间: {self.time_manager.get_formatted_time()}',
                  self.colors["text_normal"], is_center=False, font_size=24)

        # 游戏逻辑（未死亡时）
        if not self.isdead:
            self.scores += 1  # 每帧加1分
            self.snake.move()  # 蛇移动

            # 检测吃到普通食物
            if self.snake.body[0].colliderect(self.food.rect):
                self.scores += 50  # 吃到食物加50分
                self.snake.grow()  # 蛇增长
                self.food.set(self.screen_width, self.screen_height, self.snake.body)  # 生成新食物
                self.sound_manager.play_eat_sound()  # 播放吃食物音效

                # 进化模式特殊逻辑 - 修复进化检测
                self.evolution_mode.food_eaten += 1
                # 立即检查并应用进化
                if self.evolution_mode.check_evolution():
                    self.evolution_mode.apply_special_ability()
                    print(f"进化到: {self.evolution_mode.evolution_stages[self.evolution_mode.current_stage]['name']}")
            else:
                self.snake.remove_tail()  # 未吃到食物则移除尾部

        # 绘制蛇 - 根据进化阶段使用不同颜色
        self.draw_evolved_snake()

        # 死亡检测（考虑无敌效果）
        is_invincible = any(effect['type'] == 'invincible' for effect in self.evolution_mode.active_effects)
        if not is_invincible:
            self.isdead = self.snake.isdead(self.screen_width, self.screen_height)

        # 死亡处理
        if self.isdead:
            if not self.score_saved:
                # 保存分数数据
                game_time = self.time_manager.get_elapsed()
                end_time = self.time_manager.get_game_end_time()
                save_score(f"{self.scores},{game_time},{end_time}")
                self.score_saved = True
                self.sound_manager.play_death_sound()  # 播放死亡音效

            # 游戏结束面板（像正常模式那样显示）
            death_bg_rect = pygame.Rect(
                (self.screen_width - 400) // 2,
                (self.screen_height - 180) // 2,
                400, 180
            )
            death_surface = pygame.Surface((death_bg_rect.width, death_bg_rect.height), pygame.SRCALPHA)
            death_surface.fill(self.colors["panel_bg"])
            screen.blit(death_surface, (death_bg_rect.x, death_bg_rect.y))
            pygame.draw.rect(screen, (180, 200, 220), death_bg_rect, 2)

            # 显示游戏结束文字
            show_text(screen, (self.screen_width // 2, death_bg_rect.y + 50),
                      '游戏结束!', self.colors["game_over_title"], is_center=True, font_size=60)
            show_text(screen, (self.screen_width // 2, death_bg_rect.y + 100),
                      f'最终分数: {self.scores}', self.colors["text_normal"], is_center=True, font_size=30)
            show_text(screen, (self.screen_width // 2, death_bg_rect.y + 140),
                      '按空格键重新开始', self.colors["text_normal"], is_center=True, font_size=24)

        # 绘制进化模式UI - 优化排版，移到右上角
        self.draw_evolution_ui_optimized()

        # 更新特殊效果
        self.evolution_mode.update_effects()

        # 绘制普通食物
        pygame.draw.rect(screen, self.colors["food_color"], self.food.rect, 0, 3)

        # 更新屏幕显示
        pygame.display.update()
        self.clock.tick(self.evolution_mode.get_current_speed())

    def draw_evolved_snake(self):
        """根据进化阶段绘制不同外观的蛇"""
        screen = self.screen
        current_stage = self.evolution_mode.evolution_stages[self.evolution_mode.current_stage]

        for i, rect in enumerate(self.snake.body):
            # 根据进化阶段设置颜色
            if i == 0:  # 蛇头
                color = current_stage["color"]
                # 绘制蛇头
                pygame.draw.rect(screen, color, rect, 0, 5)

                # 根据能力添加特殊效果
                if current_stage["ability"] == "火焰蛇":
                    # 火焰效果
                    flame_rect = pygame.Rect(rect.x - 2, rect.y - 2, rect.width + 4, rect.height + 4)
                    pygame.draw.rect(screen, (255, 150, 0), flame_rect, 2, 5)
                elif current_stage["ability"] == "雷霆蛇":
                    # 闪电效果
                    import random
                    for j in range(3):
                        spark_x = rect.x + random.randint(0, rect.width)
                        spark_y = rect.y + random.randint(0, rect.height)
                        pygame.draw.circle(screen, (255, 255, 0), (spark_x, spark_y), 2)
            else:  # 蛇身
                # 蛇身颜色稍微变暗
                body_color = tuple(max(0, c - 30) for c in current_stage["color"])
                pygame.draw.rect(screen, body_color, rect, 0, 3)

            # 绘制边框
            pygame.draw.rect(screen, (180, 200, 220, 30), rect, 1, 2)

    def draw_evolution_ui_optimized(self):
        """绘制优化排版的进化模式UI"""
        screen = self.screen

        # 进化信息面板 - 移到右上角，避免遮挡左上角按钮
        panel_width = 250
        panel_height = 120
        panel_x = self.screen_width - panel_width - 20  # 右边距20
        panel_y = 80  # 下移避免与BGM/暂停按钮重叠

        # 创建半透明背景面板
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((180, 200, 220, 180))  # 半透明背景
        screen.blit(panel_surface, (panel_x, panel_y))
        pygame.draw.rect(screen, (150, 180, 210), (panel_x, panel_y, panel_width, panel_height), 2)

        # 当前阶段信息
        current_stage = self.evolution_mode.evolution_stages[self.evolution_mode.current_stage]

        # 计算下一阶段信息（如果有）
        if self.evolution_mode.current_stage < len(self.evolution_mode.evolution_stages) - 1:
            next_stage = self.evolution_mode.evolution_stages[self.evolution_mode.current_stage + 1]
            food_required = next_stage["food_required"]
            next_stage_name = next_stage["name"]
        else:
            # 已经是最高阶段
            food_required = 0
            next_stage_name = "最高阶段"

        # 文字信息
        text_y = panel_y + 15
        line_height = 25

        # 当前阶段
        show_text(screen, (panel_x + 10, text_y),
                  f'当前：{current_stage["name"]}',
                  self.colors["text_normal"], is_center=False, font_size=20)

        # 进度条背景（只在有下一阶段时显示）
        if self.evolution_mode.current_stage < len(self.evolution_mode.evolution_stages) - 1:
            progress_bg_rect = pygame.Rect(panel_x + 10, text_y + line_height, panel_width - 20, 12)
            pygame.draw.rect(screen, (200, 200, 200), progress_bg_rect, 0, 6)

            # 进度条前景
            progress = min(1.0, self.evolution_mode.food_eaten / food_required)
            progress_fg_rect = pygame.Rect(panel_x + 10, text_y + line_height,
                                           int((panel_width - 20) * progress), 12)
            progress_color = (100, 200, 100) if progress < 1.0 else (100, 150, 255)
            pygame.draw.rect(screen, progress_color, progress_fg_rect, 0, 6)

            # 进度文字
            progress_text = f'{self.evolution_mode.food_eaten}/{food_required}'
            show_text(screen, (panel_x + panel_width // 2, text_y + line_height + 6),
                      progress_text, self.colors["text_normal"], is_center=True, font_size=14)

            # 下一阶段
            show_text(screen, (panel_x + 10, text_y + line_height * 2 + 5),
                      f'下一阶段：{next_stage_name}',
                      self.colors["text_normal"], is_center=False, font_size=18)
        else:
            # 最高阶段显示
            show_text(screen, (panel_x + 10, text_y + line_height),
                      '已达最高阶段！',
                      (255, 200, 0), is_center=False, font_size=18)

        # 特殊能力显示（如果有）
        if self.evolution_mode.active_effects:
            effect_text = "特殊能力："
            for effect in self.evolution_mode.active_effects:
                if effect['type'] == 'speed_boost':
                    effect_text += "加速 "
                elif effect['type'] == 'invincible':
                    effect_text += "无敌 "
                elif effect['type'] == 'lightning_move':
                    effect_text += "闪电移动 "

            show_text(screen, (panel_x + 10, text_y + line_height * 3 + 10),
                      effect_text, self.colors["text_warning"], is_center=False, font_size=16)

    def reset_evolution_game(self):
        """重置进化模式游戏"""
        self.snake = Snake()
        self.food = Food()
        self.food.set(self.screen_width, self.screen_height, self.snake.body)
        self.scores = 0
        self.isdead = False
        self.score_saved = False
        self.time_manager.start()

        # 重置进化模式状态
        if hasattr(self, 'evolution_mode'):
            self.evolution_mode.current_stage = 0
            self.evolution_mode.food_eaten = 0
            self.evolution_mode.active_effects = []

    def update_theme_colors(self):
        """更新主题颜色"""
        from themes import get_current_theme
        self.colors = get_current_theme()

    def update_theme_colors(self):
        """更新主题颜色 - 只更新游戏运行相关颜色"""
        try:
            from themes import get_current_theme
            theme_colors = get_current_theme()

            # 只更新游戏运行相关的颜色
            self.colors.update({
                "game_bg": theme_colors.get("game_bg", (220, 230, 240)),
                "snake_body": theme_colors.get("snake_body", (120, 160, 200)),
                "snake_head": theme_colors.get("snake_head", (90, 140, 190)),
                "food_color": theme_colors.get("food_color", (251, 192, 45)),
                "obstacle": theme_colors.get("obstacle", (180, 60, 60))
            })

            print(f"游戏主题已更新")

        except Exception as e:
            print(f"加载游戏主题失败: {e}")
            # 回退到默认游戏颜色
            self.colors.update({
                "game_bg": (220, 230, 240),
                "snake_body": (120, 160, 200),
                "snake_head": (90, 140, 190),
                "food_color": (251, 192, 45),
                "obstacle": (180, 60, 60)
            })

    def run(self):
        """游戏主循环"""
        while True:
            if self.state == self.MAIN_MENU:
                self.handle_main_menu()
            elif self.state == self.PLAYING:
                self.handle_playing()
            elif self.state == self.PAUSED:
                self.handle_paused()
            elif self.state == self.RANKING:
                self.handle_ranking()
            elif self.state == self.ANALYSIS:
                self.handle_analysis()
            elif self.state == self.LEVEL_SELECT:
                self.handle_level_select()
            elif self.state == self.PLAY_LEVEL:
                self.handle_play_level()
            elif self.state == self.EVOLUTION_MODE:  # 确保这行存在
                self.handle_evolution_mode()
            self.clock.tick(60)

