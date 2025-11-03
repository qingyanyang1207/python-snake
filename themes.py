# themes.py - 简化主题颜色，只保留游戏运行相关颜色
import pygame
import json
import os

THEMES = {
    "CLASSIC": {
        "name": "经典蓝调",
        "colors": {
            # 游戏运行相关颜色
            "game_bg": (220, 230, 240),
            "snake_body": (120, 160, 200),
            "snake_head": (90, 140, 190),
            "food_color": (251, 192, 45),
            "obstacle": (180, 60, 60),
        }
    },
    "DARK": {
        "name": "深邃夜空",
        "colors": {
            # 游戏运行相关颜色
            "game_bg": (50, 55, 70),
            "snake_body": (100, 160, 200),
            "snake_head": (80, 140, 180),
            "food_color": (255, 195, 90),
            "obstacle": (200, 100, 100),
        }
    },
    "FOREST": {
        "name": "自然森林",
        "colors": {
            # 游戏运行相关颜色
            "game_bg": (70, 110, 90),
            "snake_body": (120, 160, 140),
            "snake_head": (100, 140, 120),
            "food_color": (255, 180, 80),
            "obstacle": (180, 100, 80),
        }
    }
}

# 主题设置文件
THEME_FILE = "theme_settings.json"

def load_theme_settings():
    """加载主题设置"""
    global CURRENT_THEME
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                CURRENT_THEME = settings.get("current_theme", "CLASSIC")
        except:
            CURRENT_THEME = "CLASSIC"
    else:
        CURRENT_THEME = "CLASSIC"
    return CURRENT_THEME

def save_theme_settings():
    """保存主题设置"""
    try:
        with open(THEME_FILE, 'w', encoding='utf-8') as f:
            json.dump({"current_theme": CURRENT_THEME}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存主题设置失败: {e}")

# 初始化当前主题
CURRENT_THEME = load_theme_settings()

def get_current_theme():
    """获取当前主题颜色"""
    return THEMES[CURRENT_THEME]["colors"]

def set_theme(theme_name):
    """设置主题"""
    global CURRENT_THEME
    if theme_name in THEMES:
        CURRENT_THEME = theme_name
        save_theme_settings()
        print(f"主题已切换到: {THEMES[theme_name]['name']}")
        return True
    return False