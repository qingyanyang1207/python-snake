import pygame
from game_state import GameState        #创建并封装gamestate类用于管理游戏状态如暂停继续等
from config import SCREEN_X, SCREEN_Y   #创建封装config类管理屏幕大小及文本字体显示等

def main():

    pygame.init()
    pygame.display.set_caption("yqy的python贪吃蛇游戏")

    screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))

    game = GameState(screen)
    game.run()

if __name__ == "__main__":
    main()