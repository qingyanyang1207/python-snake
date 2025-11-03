import pygame
from typing import List, Tuple, Optional
from ui import show_text, draw_button
from level_manage import LevelManager

class ParamDialog:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.is_active = False
        self.params = {
            "name": "自定义关卡",
            "score_target": 500,
            "time_limit": 100,
            "speed": 10
        }
        self.active_input = None
        self.input_text = {
            "name": "自定义关卡",
            "score_target": "500",
            "time_limit": "100",
            "speed": "10"
        }

        self.colors = {
            "bg": (240, 245, 250),
            "border": (100, 140, 180),
            "text": (50, 70, 90),
            "input_bg": (255, 255, 255),
            "input_active": (200, 220, 240),
            "btn_normal": (150, 180, 210),
            "btn_hover": (120, 160, 200)
        }

        # 弹窗位置和大小
        self.dialog_rect = pygame.Rect(
            (self.screen_width - 400) // 2,
            (self.screen_height - 400) // 2,
            400, 400
        )

        # 输入框位置（绝对坐标）
        base_x = self.dialog_rect.x
        base_y = self.dialog_rect.y
        self.input_rects = {
            "name": pygame.Rect(base_x + 100, base_y + 80, 250, 35),
            "score_target": pygame.Rect(base_x + 100, base_y + 150, 250, 35),
            "time_limit": pygame.Rect(base_x + 100, base_y + 220, 250, 35),
            "speed": pygame.Rect(base_x + 100, base_y + 290, 250, 35)
        }

        # 按钮位置（绝对坐标）
        self.confirm_btn = pygame.Rect(base_x + 100, base_y + 350, 120, 40)
        self.cancel_btn = pygame.Rect(base_x + 230, base_y + 350, 120, 40)

    def set_params(self, params):
        """设置初始参数"""
        self.params.update(params)
        self.input_text = {k: str(v) for k, v in params.items()}
        self.is_active = True
        self.active_input = None

    def get_params(self):
        """获取参数"""
        try:
            # 如果输入为空，使用默认值
            name = self.input_text["name"].strip() or "自定义关卡"
            score_target = int(self.input_text["score_target"] or "500")
            time_limit = int(self.input_text["time_limit"] or "100")
            speed = int(self.input_text["speed"] or "10")

            return {
                "name": name,
                "score_target": max(100, score_target),
                "time_limit": max(30, time_limit),
                "speed": max(5, min(20, speed))
            }
        except ValueError:
            return self.params

    def draw(self):
        if not self.is_active:
            return

        # 绘制半透明背景遮罩
        mask = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 100))
        self.screen.blit(mask, (0, 0))

        # 绘制弹窗
        pygame.draw.rect(self.screen, self.colors["bg"], self.dialog_rect, 0, 5)
        pygame.draw.rect(self.screen, self.colors["border"], self.dialog_rect, 2, 5)

        # 标题
        show_text(self.screen, (self.dialog_rect.centerx, self.dialog_rect.y + 30),
                  "关卡参数设置", self.colors["text"], font_size=24, is_center=True)

        # 绘制标签和输入框
        labels = {
            "name": "关卡名称：",
            "score_target": "分数目标：",
            "time_limit": "时间限制（秒）：",
            "speed": "移动速度（FPS）："
        }

        for key, rect in self.input_rects.items():
            # 标签
            label_x = rect.x - 90
            label_y = rect.centery
            show_text(self.screen, (label_x, label_y),
                      labels[key], self.colors["text"], is_center=False, font_size=18)

            # 输入框背景
            input_bg_color = self.colors["input_active"] if self.active_input == key else self.colors["input_bg"]
            pygame.draw.rect(self.screen, input_bg_color, rect, 0, 3)
            pygame.draw.rect(self.screen, self.colors["border"], rect, 2, 3)

            # 输入内容
            text = self.input_text[key]
            show_text(self.screen, (rect.x + 10, rect.centery),
                      text, self.colors["text"], is_center=False, font_size=18)

            # 光标
            if self.active_input == key:
                font = pygame.font.SysFont(None, 18)
                text_surface = font.render(text, True, self.colors["text"])
                text_width = text_surface.get_width()
                cursor_x = rect.x + 10 + text_width
                pygame.draw.line(self.screen, self.colors["text"],
                                 (cursor_x, rect.y + 5),
                                 (cursor_x, rect.bottom - 5), 2)

        # 绘制按钮
        mx, my = pygame.mouse.get_pos()

        # 确认按钮
        confirm_color = self.colors["btn_hover"] if self.confirm_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        pygame.draw.rect(self.screen, confirm_color, self.confirm_btn, 0, 3)
        show_text(self.screen, self.confirm_btn.center, "确认", self.colors["text"], font_size=18, is_center=True)

        # 取消按钮
        cancel_color = self.colors["btn_hover"] if self.cancel_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        pygame.draw.rect(self.screen, cancel_color, self.cancel_btn, 0, 3)
        show_text(self.screen, self.cancel_btn.center, "取消", self.colors["text"], font_size=18, is_center=True)

    def handle_click(self, pos):
        """处理鼠标点击"""
        if not self.is_active:
            return None

        mx, my = pos

        # 检查按钮点击
        if self.confirm_btn.collidepoint(mx, my):
            self.is_active = False
            self.params = self.get_params()
            return "confirm"

        if self.cancel_btn.collidepoint(mx, my):
            self.is_active = False
            return "cancel"

        # 检查输入框点击
        self.active_input = None
        for key, rect in self.input_rects.items():
            if rect.collidepoint(mx, my):
                self.active_input = key
                break

        return None

    def handle_key(self, event):
        """处理键盘输入"""
        if not self.is_active or self.active_input is None:
            return None

        key = self.active_input
        current_text = self.input_text[key]

        if event.key == pygame.K_RETURN:
            self.active_input = None
        elif event.key == pygame.K_ESCAPE:
            self.is_active = False
            return "cancel"
        elif event.key == pygame.K_TAB:
            # Tab键切换输入框
            keys = list(self.input_rects.keys())
            current_index = keys.index(key)
            next_index = (current_index + 1) % len(keys)
            self.active_input = keys[next_index]
        elif event.key == pygame.K_BACKSPACE:
            # 允许清空输入框
            if current_text:
                self.input_text[key] = current_text[:-1]
            else:
                self.input_text[key] = ""  # 确保可以完全清空
        else:
            # 处理字符输入
            if event.unicode:
                if key == "name":
                    # 关卡名称可以输入任何字符，限制长度
                    if len(current_text) < 20:
                        self.input_text[key] = current_text + event.unicode
                else:
                    # 数字字段只接受数字，但允许空字符串
                    if event.unicode.isdigit():
                        new_text = current_text + event.unicode
                        # 只在有内容时检查范围
                        if new_text:
                            try:
                                new_val = int(new_text)
                                # 设置合理的最小值
                                if key == "score_target" and new_val >= 1:  # 降低最小值要求
                                    self.input_text[key] = new_text
                                elif key == "time_limit" and new_val >= 1:  # 降低最小值要求
                                    self.input_text[key] = new_text
                                elif key == "speed" and new_val >= 1:  # 降低最小值要求
                                    self.input_text[key] = new_text
                            except ValueError:
                                pass
                        else:
                            # 允许空字符串
                            self.input_text[key] = new_text

        return None

class LevelEditor:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()
        self.level_manager = LevelManager()
        self.current_obstacles: List[Tuple[int, int, int, int]] = []
        self.dragging_obstacle = None
        self.drag_offset = (0, 0)

        # 参数设置弹窗
        self.param_dialog = ParamDialog(screen)
        self.edit_params = {
            "name": "自定义关卡",
            "score_target": 500,
            "time_limit": 100,
            "speed": 10
        }

        # 编辑区域
        self.editor_rect = pygame.Rect(
            20, 70,
            self.screen_width - 40,
            self.screen_height - 160
        )

        # 按钮位置
        self.back_btn = pygame.Rect(10, 10, 40, 40)
        self.save_btn = pygame.Rect(self.screen_width - 110, 10, 100, 40)
        self.add_obstacle_btn = pygame.Rect(self.screen_width - 220, 10, 100, 40)
        self.param_btn = pygame.Rect(self.screen_width - 330, 10, 100, 40)
        self.del_obstacle_btn = pygame.Rect(60, 10, 120, 40)

        # 颜色配置
        self.colors = {
            "bg": (210, 225, 235),
            "btn_normal": (150, 180, 210),
            "btn_hover": (120, 160, 200),
            "text": (50, 70, 90),
            "obstacle": (180, 60, 60),
            "obstacle_selected": (255, 165, 0),
            "editor_bg": (240, 245, 250),
            "editor_border": (100, 140, 180)
        }

    def draw_ui(self):
        self.screen.fill(self.colors["bg"])

        # 标题
        show_text(self.screen, (self.screen_width // 2, 30),
                  "自定义关卡编辑器", self.colors["text"], font_size=24, is_center=True)

        # 绘制编辑区域
        pygame.draw.rect(self.screen, self.colors["editor_bg"], self.editor_rect, 0)
        pygame.draw.rect(self.screen, self.colors["editor_border"], self.editor_rect, 2)

        # 编辑区域提示
        show_text(self.screen, (self.editor_rect.x + 10, self.editor_rect.y + 10),
                  "编辑区域：点击拖拽移动障碍物", self.colors["text"], is_center=False, font_size=16)

        # 绘制障碍物
        for i, (x, y, w, h) in enumerate(self.current_obstacles):
            rect = pygame.Rect(x, y, w, h)
            color = self.colors["obstacle_selected"] if self.dragging_obstacle == i else self.colors["obstacle"]
            pygame.draw.rect(self.screen, color, rect, 0, 3)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1, 3)

        # 绘制按钮
        mx, my = pygame.mouse.get_pos()

        # 返回按钮
        back_color = self.colors["btn_hover"] if self.back_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(self.screen, self.back_btn, '←', back_color)

        # 删除按钮
        del_color = self.colors["btn_hover"] if self.del_obstacle_btn.collidepoint(mx, my) else self.colors[
            "btn_normal"]
        draw_button(self.screen, self.del_obstacle_btn, '删除选中', del_color)

        # 添加障碍物按钮
        add_color = self.colors["btn_hover"] if self.add_obstacle_btn.collidepoint(mx, my) else self.colors[
            "btn_normal"]
        draw_button(self.screen, self.add_obstacle_btn, '添加障碍物', add_color)

        # 参数设置按钮
        param_color = self.colors["btn_hover"] if self.param_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(self.screen, self.param_btn, '关卡参数', param_color)

        # 保存按钮
        save_color = self.colors["btn_hover"] if self.save_btn.collidepoint(mx, my) else self.colors["btn_normal"]
        draw_button(self.screen, self.save_btn, '保存关卡', save_color)

        # 绘制参数弹窗
        self.param_dialog.draw()

        pygame.display.update()

    def handle_events(self) -> Optional[str]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # 如果参数弹窗激活，优先处理弹窗事件
            if self.param_dialog.is_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    result = self.param_dialog.handle_click(event.pos)
                    if result == "confirm":
                        self.edit_params = self.param_dialog.get_params()
                    elif result == "cancel":
                        pass
                elif event.type == pygame.KEYDOWN:
                    result = self.param_dialog.handle_key(event)
                    if result == "cancel":
                        pass
                # 弹窗激活时，不处理其他事件
                continue

            # 正常处理编辑器事件
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # 返回按钮
                if self.back_btn.collidepoint(mx, my):
                    return "LEVEL_SELECT"

                # 保存按钮
                if self.save_btn.collidepoint(mx, my):
                    if self.save_custom_level():
                        return "LEVEL_SELECT"

                # 添加障碍物
                if self.add_obstacle_btn.collidepoint(mx, my):
                    center_x = self.editor_rect.centerx - 20
                    center_y = self.editor_rect.centery - 20
                    self.current_obstacles.append((center_x, center_y, 40, 40))

                # 删除障碍物
                if self.del_obstacle_btn.collidepoint(mx, my):
                    if self.dragging_obstacle is not None:
                        del self.current_obstacles[self.dragging_obstacle]
                        self.dragging_obstacle = None
                    elif self.current_obstacles:
                        self.current_obstacles.pop()

                # 打开参数设置弹窗
                if self.param_btn.collidepoint(mx, my):
                    self.param_dialog.set_params(self.edit_params)

                # 开始拖拽障碍物
                if self.editor_rect.collidepoint(mx, my):
                    self.dragging_obstacle = None
                    for i, (x, y, w, h) in enumerate(self.current_obstacles):
                        obstacle_rect = pygame.Rect(x, y, w, h)
                        if obstacle_rect.collidepoint(mx, my):
                            self.dragging_obstacle = i
                            self.drag_offset = (mx - x, my - y)
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_obstacle = None

            elif event.type == pygame.MOUSEMOTION and self.dragging_obstacle is not None:
                mx, my = event.pos
                idx = self.dragging_obstacle
                x = mx - self.drag_offset[0]
                y = my - self.drag_offset[1]
                # 限制在编辑区域内
                x = max(self.editor_rect.x, min(x, self.editor_rect.right - 40))
                y = max(self.editor_rect.y, min(y, self.editor_rect.bottom - 40))
                self.current_obstacles[idx] = (x, y, 40, 40)

        return None

    def save_custom_level(self):
        """保存自定义关卡"""
        # 检查关卡名称
        if not self.edit_params["name"].strip():
            print("关卡名称不能为空")
            return False

        # 验证参数范围
        if self.edit_params["score_target"] < 100:
            print("分数目标不能小于100")
            return False
        if self.edit_params["time_limit"] < 30:
            print("时间限制不能小于30秒")
            return False
        if not (5 <= self.edit_params["speed"] <= 20):
            print("移动速度必须在5-20之间")
            return False

        level_data = {
            "name": self.edit_params["name"],
            "score_target": self.edit_params["score_target"],
            "time_limit": self.edit_params["time_limit"],
            "speed": self.edit_params["speed"],
            "obstacles": self.current_obstacles.copy()
        }

        success = self.level_manager.add_custom_level(level_data)
        if success:
            print("关卡保存成功！")
            # 重置编辑器状态
            self.current_obstacles = []
            self.edit_params = {
                "name": "自定义关卡",
                "score_target": 500,
                "time_limit": 100,
                "speed": 10
            }
            return True
        else:
            print("关卡保存失败！")
            return False

    def run(self):
        """运行关卡编辑器主循环"""
        clock = pygame.time.Clock()

        while True:
            self.draw_ui()
            next_state = self.handle_events()
            if next_state:
                return next_state
            clock.tick(60)