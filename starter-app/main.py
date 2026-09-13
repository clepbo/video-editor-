"""
Local AI Video Editor - Starter GUI
Run: pip install -r requirements.txt
Then: python main.py
Requires: ffmpeg.exe in PATH or in same folder
"""
import customtkinter as ctk
import os, subprocess, json, threading
from tkinter import filedialog
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VideoEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("My Local AI Editor - Private Build")
        self.geometry("900x600")
        self.video_path = None

        # UI Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top bar
        top = ctk.CTkFrame(self)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkButton(top, text="Import Video", command=self.import_video).pack(side="left", padx=5)
        ctk.CTkLabel(top, text="| AI Tools:").pack(side="left", padx=10)
        ctk.CTkButton(top, text="✂️ Auto-Remove Silence", command=self.run_silence_removal, fg_color="#2a9d8f").pack(side="left", padx=5)
        ctk.CTkButton(top, text="💬 Auto Captions", command=self.run_captions, fg_color="#e76f51").pack(side="left", padx=5)
        ctk.CTkButton(top, text="🔥 Viral Clips 9:16", command=self.run_viral, fg_color="#9d4edd").pack(side="left", padx=5)

        # Center - preview + log
        self.preview_label = ctk.CTkLabel(self, text="Import a video to start\n\nThis is your private editor.\nAll AI runs offline.", font=("Arial", 18), justify="center")
        self.preview_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.log_box = ctk.CTkTextbox(self, height=150)
        self.log_box.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,10))
        self.log("Ready. Import a video...")

    def log(self, msg):
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")
        print(msg)

    def import_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.mov *.mkv *.avi")])
        if path:
            self.video_path = path
            self.preview_label.configure(text=f"Loaded:\n{Path(path).name}\n\nSize: {os.path.getsize(path)/1024/1024:.1f} MB")
            self.log(f"Loaded: {path}")

    def run_in_thread(self, func):
        if not self.video_path:
            self.log("ERROR: Import video first!")
            return
        threading.Thread(target=func, daemon=True).start()

    def run_silence_removal(self):
        self.run_in_thread(self._silence_job)

    def run_captions(self):
        self.run_in_thread(self._caption_job)

    def run_viral(self):
        self.run_in_thread(self._viral_job)

    # --- AI JOBS (Replace with real logic) ---
    def _silence_job(self):
        self.log("Starting Auto Silence Removal...")
        # Example FFmpeg command for silence detection
        # Real implementation would use silero-vad or pydub for better accuracy
        output = str(Path(self.video_path).with_name("output_nosilence.mp4"))
        cmd = [
            "ffmpeg", "-y", "-i", self.video_path,
            "-af", "silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-40dB",
            "-c:v", "libx264", "-preset", "fast",
            output
        ]
        try:
            subprocess.run(cmd, check=True)
            self.log(f"DONE! Saved: {output}")
        except Exception as e:
            self.log(f"FFmpeg error: {e}. Make sure ffmpeg is installed.")

    def _caption_job(self):
        self.log("Starting Auto Captions with Faster-Whisper (offline)...")
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel("base", device="cpu", compute_type="int8") # change to "cuda" if you have NVIDIA GPU
            segments, info = model.transcribe(self.video_path, beam_size=5)
            srt_path = str(Path(self.video_path).with_suffix(".srt"))
            with open(srt_path, "w", encoding="utf-8") as f:
                for i, seg in enumerate(segments, 1):
                    f.write(f"{i}\n{self._to_srt_time(seg.start)} --> {self._to_srt_time(seg.end)}\n{seg.text.strip()}\n\n")
            self.log(f"Transcript saved: {srt_path}")
            
            # Burn in
            output = str(Path(self.video_path).with_name("output_captioned.mp4"))
            # Simple burn-in, you can style it later
            vf = f"subtitles={srt_path.replace(':', r'\\:')}"
            subprocess.run(["ffmpeg", "-y", "-i", self.video_path, "-vf", vf, "-c:a", "copy", output], check=True)
            self.log(f"DONE! Captioned video: {output}")

        except ImportError:
            self.log("Please install: pip install faster-whisper")
        except Exception as e:
            self.log(f"Error: {e}")

    def _viral_job(self):
        self.log("Viral Clip (Auto Reframe to 9:16) - Demo: center crop")
        output = str(Path(self.video_path).with_name("output_viral_9x16.mp4"))
        # Center crop to 9:16 - Real version would use YOLO face tracking
        cmd = [
            "ffmpeg", "-y", "-i", self.video_path,
            "-vf", "crop=ih*9/16:ih",
            "-c:a", "copy", output
        ]
        try:
            subprocess.run(cmd, check=True)
            self.log(f"DONE! Viral version: {output} - Next step: add face tracking with YOLOv8")
        except Exception as e:
            self.log(f"Error: {e}")

    def _to_srt_time(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

if __name__ == "__main__":
    app = VideoEditorApp()
    app.mainloop()
