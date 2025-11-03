import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.eat_sound = None
        self.death_sound = None
        self.bgm_sound = None  # BGM音频对象
        self.bgm_playing = False  # BGM播放状态标记

        try:
            # 加载吃食物音效
            if os.path.exists("souces/eat.wav"):
                self.eat_sound = pygame.mixer.Sound("souces/eat.wav")
                self.eat_sound.set_volume(0.3)
            # 加载死亡音效
            if os.path.exists("souces/death.wav"):
                self.death_sound = pygame.mixer.Sound("souces/death.wav")
                self.death_sound.set_volume(0.3)
            # 加载BGM
            if os.path.exists("souces/bgm.mp3"):
                self.bgm_sound = pygame.mixer.Sound("souces/bgm.mp3")
                self.bgm_sound.set_volume(0.5)  # 调整BGM音量
        except pygame.error as e:
            print(f"加载音频失败: {e}")

    def play_eat_sound(self):
        """播放吃食物音效"""
        if self.eat_sound:
            self.eat_sound.play()

    def play_death_sound(self):
        """播放死亡音效"""
        if self.death_sound:
            self.death_sound.play()

    def play_bgm(self):
        """播放BGM（无限循环）"""
        if self.bgm_sound and not self.bgm_playing:
            self.bgm_sound.play(-1)  # -1表示循环播放
            self.bgm_playing = True

    def pause_bgm(self):
        """暂停BGM"""
        if self.bgm_sound and self.bgm_playing:
            self.bgm_sound.stop()  # 替代pause方法，停止当前播放
            self.bgm_playing = False

    def toggle_bgm(self):
        """切换BGM播放/暂停状态"""
        if self.bgm_playing:
            self.pause_bgm()
        else:
            self.play_bgm()

    def is_bgm_playing(self):
        """获取BGM当前播放状态"""
        return self.bgm_playing

    def is_bgm_loaded(self):
        """判断BGM是否加载成功"""
        return self.bgm_sound is not None