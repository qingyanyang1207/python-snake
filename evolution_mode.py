# evolution_mode.py - 贪吃蛇进化模式
import pygame
import random
from ui import show_text, draw_button


class EvolutionMode:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        # 进化阶段定义
        self.evolution_stages = [
            {
                "name": "幼蛇",
                "color": (100, 200, 100),
                "speed": 8,
                "ability": None,
                "food_required": 5
            },
            {
                "name": "成长蛇",
                "color": (50, 150, 50),
                "speed": 10,
                "ability": "加速",
                "food_required": 10
            },
            {
                "name": "敏捷蛇",
                "color": (0, 100, 200),
                "speed": 12,
                "ability": "穿墙",
                "food_required": 15
            },
            {
                "name": "火焰蛇",
                "color": (255, 100, 0),
                "speed": 14,
                "ability": "烧毁障碍",
                "food_required": 20
            },
            {
                "name": "雷霆蛇",
                "color": (200, 200, 0),
                "speed": 16,
                "ability": "闪电移动",
                "food_required": 25
            },
            {
                "name": "神龙",
                "color": (150, 0, 200),
                "speed": 18,
                "ability": "无敌",
                "food_required": 30
            }
        ]

        # 特殊食物类型
        self.special_foods = [
            {
                "type": "加速果实",
                "color": (255, 255, 0),
                "effect": "speed_boost",
                "duration": 300
            },
            {
                "type": "护盾果实",
                "color": (0, 200, 255),
                "effect": "shield",
                "duration": 200
            },
            {
                "type": "分身果实",
                "color": (200, 100, 255),
                "effect": "clone",
                "duration": 150
            },
            {
                "type": "磁力果实",
                "color": (255, 100, 100),
                "effect": "magnet",
                "duration": 250
            }
        ]

        # 游戏状态
        self.current_stage = 0
        self.food_eaten = 0
        self.special_ability_active = False
        self.ability_timer = 0
        self.active_effects = []

        # 颜色配置
        self.colors = {
            "bg": (210, 225, 235),
            "btn_normal": (150, 180, 210),
            "btn_hover": (120, 160, 200),
            "text_primary": (50, 70, 90),
            "evolution_panel": (180, 200, 220, 200)
        }

    def draw_evolution_ui(self, snake_body):
        """绘制进化模式UI"""
        current_stage = self.evolution_stages[self.current_stage]
        next_stage = self.evolution_stages[self.current_stage + 1] if self.current_stage < len(
            self.evolution_stages) - 1 else None

        # 进化进度面板
        panel_rect = pygame.Rect(10, 10, 300, 120)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.colors["evolution_panel"])
        self.screen.blit(panel_surface, (panel_rect.x, panel_rect.y))
        pygame.draw.rect(self.screen, (120, 160, 200), panel_rect, 2, 5)

        # 当前阶段信息
        show_text(self.screen, (panel_rect.x + 10, panel_rect.y + 15),
                  f"当前: {current_stage['name']}", self.colors["text_primary"],
                  is_center=False, font_size=20)

        if current_stage['ability']:
            show_text(self.screen, (panel_rect.x + 10, panel_rect.y + 40),
                      f"能力: {current_stage['ability']}", self.colors["text_primary"],
                      is_center=False, font_size=16)

        # 进化进度条
        if next_stage:
            progress = min(1.0, self.food_eaten / next_stage['food_required'])
            progress_bg = pygame.Rect(panel_rect.x + 10, panel_rect.y + 65, 280, 20)
            progress_fill = pygame.Rect(panel_rect.x + 10, panel_rect.y + 65, 280 * progress, 20)

            pygame.draw.rect(self.screen, (180, 180, 180), progress_bg, 0, 3)
            pygame.draw.rect(self.screen, current_stage['color'], progress_fill, 0, 3)

            show_text(self.screen, (panel_rect.x + 150, panel_rect.y + 75),
                      f"{self.food_eaten}/{next_stage['food_required']}",
                      self.colors["text_primary"], font_size=14)

            show_text(self.screen, (panel_rect.x + 10, panel_rect.y + 95),
                      f"下一阶段: {next_stage['name']}", self.colors["text_primary"],
                      is_center=False, font_size=14)

        # 绘制特殊效果图标
        effect_y = 140
        for effect in self.active_effects:
            effect_rect = pygame.Rect(10, effect_y, 200, 25)
            effect_surface = pygame.Surface((effect_rect.width, effect_rect.height), pygame.SRCALPHA)
            effect_surface.fill((200, 230, 255, 180))
            self.screen.blit(effect_surface, (effect_rect.x, effect_rect.y))

            show_text(self.screen, (effect_rect.x + 10, effect_rect.y + 12),
                      f"{effect['name']}: {effect['timer']}帧",
                      self.colors["text_primary"], is_center=False, font_size=12)
            effect_y += 30

        # 根据当前阶段改变蛇的外观
        self.draw_evolved_snake(snake_body, current_stage)

    def draw_evolved_snake(self, snake_body, stage):
        """绘制进化后的蛇"""
        for i, rect in enumerate(snake_body):
            # 根据阶段改变颜色和外观
            if i == 0:  # 蛇头
                pygame.draw.rect(self.screen, stage['color'], rect, 0, 5)
                # 添加特殊效果
                if stage['ability'] == '火焰蛇':
                    # 火焰效果
                    flame_rect = pygame.Rect(rect.x - 2, rect.y - 2, rect.width + 4, rect.height + 4)
                    pygame.draw.rect(self.screen, (255, 150, 0), flame_rect, 2, 5)
                elif stage['ability'] == '雷霆蛇':
                    # 闪电效果
                    for j in range(3):
                        spark_x = rect.x + random.randint(0, rect.width)
                        spark_y = rect.y + random.randint(0, rect.height)
                        pygame.draw.circle(self.screen, (255, 255, 0), (spark_x, spark_y), 2)
            else:  # 蛇身
                color_variation = random.randint(-20, 20)
                body_color = (
                    max(0, min(255, stage['color'][0] + color_variation)),
                    max(0, min(255, stage['color'][1] + color_variation)),
                    max(0, min(255, stage['color'][2] + color_variation))
                )
                pygame.draw.rect(self.screen, body_color, rect, 0, 3)

    def check_evolution(self):
        """检查是否进化到下一阶段"""
        if self.current_stage < len(self.evolution_stages) - 1:
            current_stage = self.evolution_stages[self.current_stage]
            next_stage = self.evolution_stages[self.current_stage + 1]

            # 检查是否达到下一阶段的要求
            if self.food_eaten >= next_stage['food_required']:
                self.current_stage += 1
                self.food_eaten = 0  # 重置食物计数
                print(f"进化到: {self.evolution_stages[self.current_stage]['name']}")
                # 立即应用新阶段的特殊能力
                self.apply_special_ability()
                return True
        return False


    def apply_special_ability(self):
        """应用特殊能力"""
        current_stage = self.evolution_stages[self.current_stage]
        ability = current_stage['ability']

        if ability == "加速":
            self.active_effects.append({
                "name": "加速",
                "timer": 180,
                "type": "speed_boost"
            })
        elif ability == "穿墙":
            # 在handle_playing中处理穿墙逻辑
            pass
        elif ability == "烧毁障碍":
            # 可以烧毁碰到的障碍物
            pass
        elif ability == "闪电移动":
            self.active_effects.append({
                "name": "闪电移动",
                "timer": 120,
                "type": "lightning_move"
            })
        elif ability == "无敌":
            self.active_effects.append({
                "name": "无敌",
                "timer": 300,
                "type": "invincible"
            })

    def update_effects(self):
        """更新特殊效果计时器"""
        for effect in self.active_effects[:]:
            effect['timer'] -= 1
            if effect['timer'] <= 0:
                self.active_effects.remove(effect)

    def get_current_speed(self):
        """获取当前速度（考虑加速效果）"""
        base_speed = self.evolution_stages[self.current_stage]['speed']
        for effect in self.active_effects:
            if effect['type'] == 'speed_boost':
                return base_speed + 4
        return base_speed