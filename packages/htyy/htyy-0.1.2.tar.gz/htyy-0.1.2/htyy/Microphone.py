import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import threading

class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.fs = 44100  # 采样率
        self.recording = None  # 存储录音数据
        self.stream = None

    def start_recording(self):
        """开始录音"""
        self.is_recording = True
        self.recording = []
        
        def callback(indata, frames, time, status):
            if self.is_recording:
                self.recording.append(indata.copy())
        
        self.stream = sd.InputStream(
            samplerate=self.fs,
            channels=1,
            callback=callback
        )
        self.stream.start()

    def stop_recording(self):
        """停止录音"""
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        if self.recording:
            self.recording = np.concatenate(self.recording, axis=0)

    def save_recording(self, filename):
        """保存录音到文件"""
        if self.recording is not None:
            write(filename, self.fs, self.recording)

class App:
    def __init__(self, root):
        self.root = root
        self.recorder = AudioRecorder()
        self.setup_ui()
        
    def setup_ui(self):
        """初始化用户界面"""
        self.root.title("音频录制工具")
        self.root.geometry("300x200")
        self.root.configure(bg="#f0f0f0")

        style = ttk.Style()
        style.configure("TButton", 
                        padding=6, 
                        relief="flat",
                        background="#4CAF50",
                        foreground="white")

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True)

        self.record_btn = ttk.Button(
            main_frame, 
            text="开始录制",
            command=self.toggle_recording
        )
        self.record_btn.pack(pady=5, fill=tk.X)

        self.play_btn = ttk.Button(
            main_frame,
            text="播放录音",
            command=self.play_recording,
            state=tk.DISABLED
        )
        self.play_btn.pack(pady=5, fill=tk.X)

        self.download_btn = ttk.Button(
            main_frame,
            text="下载录音",
            command=self.download_recording,
            state=tk.DISABLED
        )
        self.download_btn.pack(pady=5, fill=tk.X)

    def toggle_recording(self):
        """切换录音状态"""
        if not self.recorder.is_recording:
            # 处理已有录音的覆盖提示
            if self.recorder.recording is not None:
                response = messagebox.askyesnocancel(
                    "新录音",
                    "当前存在未保存的录音，是否保存？"
                )
                if response is None:  # 取消操作
                    return
                elif response:  # 保存录音
                    self.download_recording()
                # 清空现有录音数据
                self.recorder.recording = None
                self.play_btn.config(state=tk.DISABLED)
                self.download_btn.config(state=tk.DISABLED)

            # 开始新录音
            self.record_btn.config(text="停止录制")
            self.recorder.start_recording()
        else:
            # 停止录音
            self.recorder.stop_recording()
            self.record_btn.config(text="开始录制")
            # 启用功能按钮
            if self.recorder.recording is not None:
                self.play_btn.config(state=tk.NORMAL)
                self.download_btn.config(state=tk.NORMAL)

    def play_recording(self):
        """播放录音"""
        if self.recorder.recording is not None:
            self.play_btn.config(state=tk.DISABLED)
            threading.Thread(target=self._play_audio).start()

    def _play_audio(self):
        """实际播放音频的线程方法"""
        try:
            sd.play(self.recorder.recording, self.recorder.fs)
            sd.wait()
        except Exception as e:
            messagebox.showerror("播放错误", str(e))
        finally:
            self.root.after(0, lambda: self.play_btn.config(state=tk.NORMAL))

    def download_recording(self):
        """下载录音文件"""
        if self.recorder.recording is None:
            messagebox.showerror("错误", "没有可保存的录音")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV 文件", "*.wav")]
        )
        if file_path:
            try:
                self.recorder.save_recording(file_path)
                messagebox.showinfo("成功", f"录音已保存到：{file_path}")
            except Exception as e:
                messagebox.showerror("保存失败", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()