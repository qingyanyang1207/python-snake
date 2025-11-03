import time


class TimeManager:
    def __init__(self):
        self.start_time = 0
        self.pause_time = 0
        self.paused = False
        self.elapsed = 0

    def start(self):
        """开始计时"""
        self.start_time = time.time()
        self.paused = False
        self.elapsed = 0

    def pause(self):
        """暂停计时"""
        if not self.paused:
            self.pause_time = time.time()
            self.elapsed += self.pause_time - self.start_time
            self.paused = True

    def resume(self):
        """恢复计时"""
        if self.paused:
            self.start_time = time.time()
            self.paused = False

    def get_elapsed(self):
        """获取已流逝的秒数"""
        if self.paused:
            return int(self.elapsed)
        else:
            return int(self.elapsed + (time.time() - self.start_time))

    def get_formatted_time(self):
        """获取格式化的时间（分:秒）"""
        seconds = self.get_elapsed()
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_game_end_time(self):
        """获取游戏结束的时间字符串"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
