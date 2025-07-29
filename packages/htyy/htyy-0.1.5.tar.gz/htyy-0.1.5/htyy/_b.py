import os
import tkinter as tk
from tkinter import ttk, filedialog
import pygame
from mutagen.mp3 import MP3
import ctypes

class SimpleMusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Media Player")
        self.root.geometry("500x300")
        
        # 初始化参数
        self.current_file = None
        self.playing = False
        self.paused = False
        self.duration = 0
        self.seeking = False  # 拖动进度条标志
        
        # 初始化界面
        self.create_widgets()
        pygame.mixer.init()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_widgets(self):
        # 主布局容器
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部控制栏
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        self.btn_open = ttk.Button(top_frame, text="打开文件", command=self.open_file)
        self.btn_open.pack(side=tk.LEFT, padx=5)
        
        # 进度条区域
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.time_current = ttk.Label(progress_frame, text="00:00", width=6)
        self.time_current.pack(side=tk.LEFT)
        
        self.progress = ttk.Scale(
            progress_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL,
            command=self.on_progress_drag
        )
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.time_total = ttk.Label(progress_frame, text="00:00", width=6)
        self.time_total.pack(side=tk.LEFT)
        
        # 播放控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        self.btn_play = ttk.Button(control_frame, text="▶", width=3, command=self.toggle_play)
        self.btn_stop = ttk.Button(control_frame, text="⏹", width=3, command=self.stop)
        
        self.btn_play.pack(side=tk.LEFT, padx=5)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        # 音量控制
        volume_frame = ttk.Frame(main_frame)
        volume_frame.pack(pady=5)
        
        ttk.Label(volume_frame, text="音量:").pack(side=tk.LEFT)
        self.volume = ttk.Scale(
            volume_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL,
            command=lambda v: pygame.mixer.music.set_volume(float(v)/100)
        )
        self.volume.set(75)
        self.volume.pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status = ttk.Label(main_frame, text="就绪", relief=tk.SUNKEN)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 定时更新进度
        self.update_progress()
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("音频文件", "*.mp3 *.wav *.mid"), ("All Files", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.load_file(file_path)
            self.play()
    
    def load_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext in ('.mp3', '.wav'):
                if ext == '.mp3':
                    audio = MP3(file_path)
                    self.duration = audio.info.length
                else:  # WAV
                    sound = pygame.mixer.Sound(file_path)
                    self.duration = sound.get_length()
                
                self.status.config(text=f"正在播放: {os.path.basename(file_path)}")
                pygame.mixer.music.load(file_path)
                self.time_total.config(text=self.format_time(self.duration))
                
            elif ext == '.mid':
                self.duration = 180  # MIDI默认估计时长（实际需解析）
                self.status.config(text=f"MIDI播放: {os.path.basename(file_path)}")
            
            self.progress.config(to=100)
            self.progress.set(0)
            
        except Exception as e:
            self.status.config(text=f"错误: {str(e)}")
    
    def toggle_play(self):
        if self.playing:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
                self.btn_play.config(text="▶")
            else:
                pygame.mixer.music.pause()
                self.paused = True
                self.btn_play.config(text="⏸")
        else:
            self.play()
    
    def play(self):
        if not self.current_file:
            return
        
        ext = os.path.splitext(self.current_file)[1].lower()
        try:
            if ext == '.mid':
                # MIDI播放使用Windows API
                self.stop()  # 停止现有播放
                result = ctypes.windll.winmm.mciSendStringW(
                    f'open "{self.current_file}" alias midi', None, 0, None)
                if result != 0:
                    raise RuntimeError(f"MIDI播放失败，错误代码：{result}")
                ctypes.windll.winmm.mciSendStringW("play midi", None, 0, None)
            else:
                pygame.mixer.music.play()
            
            self.playing = True
            self.paused = False
            self.btn_play.config(text="⏸")
            
        except Exception as e:
            self.status.config(text=f"播放错误: {str(e)}")
    
    def stop(self):
        if self.current_file and os.path.splitext(self.current_file)[1].lower() == '.mid':
            ctypes.windll.winmm.mciSendStringW("close midi", None, 0, None)
        else:
            pygame.mixer.music.stop()
        
        self.playing = False
        self.paused = False
        self.btn_play.config(text="▶")
        self.progress.set(0)
        self.time_current.config(text="00:00")
    
    def on_progress_drag(self, value):
        if not self.playing or self.seeking:
            return
        
        self.seeking = True
        position = float(value) * self.duration / 100
        
        try:
            if self.current_file.endswith('.mid'):
                # MIDI跳转需要特殊处理
                ctypes.windll.winmm.mciSendStringW(f"seek midi to {int(position*1000)}", None, 0, None)
                ctypes.windll.winmm.mciSendStringW("play midi", None, 0, None)
            else:
                pygame.mixer.music.set_pos(position)
                
            self.time_current.config(text=self.format_time(position))
        finally:
            self.seeking = False
    
    def format_time(self, seconds):
        return f"{int(seconds//60):02d}:{int(seconds%60):02d}"
    
    def update_progress(self):
        if self.playing and not self.paused and not self.seeking:
            if self.current_file.endswith('.mid'):
                # MIDI进度无法直接获取，使用估算
                current = pygame.mixer.music.get_pos()/1000 % self.duration
            else:
                current = pygame.mixer.music.get_pos()/1000
                
            if current > 0:
                progress = (current / self.duration) * 100
                self.progress.set(progress)
                self.time_current.config(text=self.format_time(current))
        
        self.root.after(500, self.update_progress)
    
    def on_close(self):
        self.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    player = SimpleMusicPlayer(root)
    root.mainloop()