import pygame


def show_text(screen, pos, text, color, is_center=True, font_size=30):
    # 如果颜色为None，使用默认颜色
    if color is None:
        color = (50, 70, 90)  # 默认文字颜色

    pygame.font.init()
    try:
        font = pygame.font.Font("souces/simfang.ttf", font_size)
    except:
        font = pygame.font.SysFont(["SimFang", "Microsoft YaHei", "Arial"], font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if is_center:
        text_rect.center = pos
    else:
        text_rect.topleft = pos
    screen.blit(text_surface, text_rect)


def draw_button(screen, rect, text, color, text_color=None):
    # 如果颜色为None，使用默认颜色
    if color is None:
        color = (150, 180, 210)  # 默认按钮颜色

    if text_color is None:
        text_color = (50, 70, 90)  # 默认文字颜色

    # 绘制按钮背景
    pygame.draw.rect(screen, color, rect, 0, 5)

    # 绘制按钮边框
    pygame.draw.rect(screen, (120, 160, 200), rect, 1, 5)

    # 绘制按钮文字
    show_text(screen, rect.center, text, text_color, font_size=24)