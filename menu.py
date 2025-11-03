import sys
import pygame
from ui import show_text, draw_button

def draw_main_menu(screen):

    screen_width, screen_height = screen.get_size()

    screen.fill((210, 225, 235))

    show_text(screen, (screen_width // 2, 100), '贪吃蛇',
              (50, 70, 90), is_center=True, font_size=70)

    button_width, button_height = 200, 60
    start_btn = pygame.Rect(
        (screen_width - button_width) // 2,
        screen_height // 2 - 70,
        button_width,
        button_height
    )
    rank_btn = pygame.Rect(
        (screen_width - button_width) // 2,
        screen_height // 2 + 20,
        button_width,
        button_height
    )

    # 鼠标hover检测
    mx, my = pygame.mouse.get_pos()
    start_btn_color = (120, 160, 200) if start_btn.collidepoint(mx, my) else (150, 180, 210)
    rank_btn_color = (120, 160, 200) if rank_btn.collidepoint(mx, my) else (150, 180, 210)

    draw_button(screen, start_btn, '开始游戏', start_btn_color)
    draw_button(screen, rank_btn, '排行榜', rank_btn_color)

    pygame.display.update()

def handle_menu_events(screen):
    """处理菜单事件"""
    screen_width, screen_height = screen.get_size()
    button_width, button_height = 200, 60

    # 按钮区域定义
    start_btn = pygame.Rect(
        (screen_width - button_width) // 2,
        screen_height // 2 - 70,
        button_width,
        button_height
    )
    rank_btn = pygame.Rect(
        (screen_width - button_width) // 2,
        screen_height // 2 + 20,
        button_width,
        button_height
    )

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if start_btn.collidepoint(mx, my):
                return "PLAYING"
            if rank_btn.collidepoint(mx, my):
                return "RANKING"
    return "MAIN_MENU"

def run_main_menu(screen):
    """运行主菜单循环"""
    while True:
        draw_main_menu(screen)
        next_state = handle_menu_events(screen)
        if next_state != "MAIN_MENU":
            return next_state
        pygame.time.Clock().tick(60)
