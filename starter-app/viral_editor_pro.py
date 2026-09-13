"""
Viral Editor PRO - Final Integrated Version
All 3 requested features + original trainable AI

Features:
✓ Trainable viral clip AI (learns YOUR style)
✓ Face-tracking reframe (follows you, not center crop)
✓ Hormozi word-by-word pop captions
✓ Batch mode: Drop folder of 10 long videos -> 50 viral clips overnight
✓ Color grading + silence removal + audio normalize

Run: python viral_editor_pro.py
"""

import customtkinter as ctk
from tkinter import filedialog
import os, subprocess, threading, json
from pathlib import Path
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ViralEditorPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Viral Editor PRO - Private AI Studio")
        self.geometry("1100x750")
        
        self.example_clips = []
        self.long_video = None
        self.batch_input_folder = None
        
        # Main tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabview.add("1. Teach AI")
        self.tabview.add("2. Single Video")
        self.tabview.add("3. Batch Overnight")
        self.tabview.add("4. Settings")
        
        self.build_teach_tab()
        self.build_single_tab()
        self.build_batch_tab()
        self.build_settings_tab()
        
        # Log
        self.log_box = ctk.CTkTextbox(self, height=140)
        self.log_box.pack(fill="x", padx=10, pady=(0,10))
        self.log("PRO Version Ready. Start: Tab 1 -> Teach AI with your best clips (5-20 videos)")

    def log(self, msg):
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")
        print(msg)
        self.update_idletasks()

    # --- TAB 1: TEACH ---
    def build_teach_tab(self):
        tab = self.tabview.tab("1. Teach AI")
        
        ctk.CTkLabel(tab, text="Teach AI Your Viral Style", font=("Arial", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(tab, text="Import 5-20 clips that went viral or represent your ideal excerpt. The AI will learn your hook style, pacing, and energy.", wraplength=700).pack()
        
        btn_frame = ctk.CTkFrame(tab)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Add Example Clips", command=self.add_examples).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Clear", command=self.clear_examples, fg_color="gray").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🧠 Train Style Profile", command=self.train_style, fg_color="#9d4edd", font=("Arial", 14, "bold"), width=200).pack(side="left", padx=15)
        
        self.example_list = ctk.CTkScrollableFrame(tab, height=350)
        self.example_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.teach_status = ctk.CTkLabel(tab, text="No examples yet. Need at least 3-5.", text_color="orange", font=("Arial", 13))
        self.teach_status.pack(pady=5)

    def add_examples(self):
        files = filedialog.askopenfilenames(filetypes=[("Video", "*.mp4 *.mov *.mkv")])
        for f in files:
            self.example_clips.append(f)
            ctk.CTkLabel(self.example_list, text=f"✓ {Path(f).name}", anchor="w").pack(fill="x", padx=5, pady=2)
        self.teach_status.configure(text=f"{len(self.example_clips)} examples loaded")
        self.log(f"Added {len(files)} examples")

    def clear_examples(self):
        self.example_clips = []
        for w in self.example_list.winfo_children():
            w.destroy()
        self.teach_status.configure(text="Cleared")

    def train_style(self):
        if len(self.example_clips) < 3:
            self.log("ERROR: Need at least 3 examples")
            return
        threading.Thread(target=self._train_job, daemon=True).start()

    def _train_job(self):
        self.log("Training... Transcribing examples (2-5 mins)...")
        try:
            from trainable_viral_engine import StyleLearner
            learner = StyleLearner()
            profile = learner.learn_from_examples(self.example_clips, save_path="my_style_profile.json")
            if profile:
                self.log(f"SUCCESS! Style learned. Avg {profile['stats']['avg_words']:.0f} words, Hook rate {profile['stats']['hook_rate']*100:.0f}%")
                self.teach_status.configure(text=f"✓ Trained on {len(self.example_clips)} clips! Ready.", text_color="#2a9d8f")
        except Exception as e:
            self.log(f"Training failed: {e}")
            import traceback; traceback.print_exc()

    # --- TAB 2: SINGLE ---
    def build_single_tab(self):
        tab = self.tabview.tab("2. Single Video")
        
        ctk.CTkLabel(tab, text="Single Long Video -> Viral Clips", font=("Arial", 18, "bold")).pack(pady=10)
        
        top = ctk.CTkFrame(tab)
        top.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(top, text="Import Long Video", command=self.import_long).pack(side="left", padx=5)
        self.long_label = ctk.CTkLabel(top, text="No video loaded")
        self.long_label.pack(side="left", padx=10)
        
        options = ctk.CTkFrame(tab)
        options.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(options, text="Clips:").pack(side="left", padx=5)
        self.num_clips = ctk.CTkOptionMenu(options, values=["3", "5", "10"])
        self.num_clips.pack(side="left", padx=5)
        self.num_clips.set("5")
        
        ctk.CTkLabel(options, text="Format:").pack(side="left", padx=10)
        self.format_opt = ctk.CTkOptionMenu(options, values=["9:16 Vertical (Face-Track)", "9:16 Center Crop", "1:1 Square", "16:9 Original"])
        self.format_opt.pack(side="left", padx=5)
        self.format_opt.set("9:16 Vertical (Face-Track)")
        
        ctk.CTkLabel(options, text="Captions:").pack(side="left", padx=10)
        self.caption_style_opt = ctk.CTkOptionMenu(options, values=["Hormozi Pop Single", "Hormozi Pop Multi (3 words)", "No Captions"])
        self.caption_style_opt.pack(side="left", padx=5)
        
        self.generate_btn = ctk.CTkButton(tab, text="🔥 GENERATE VIRAL CLIPS (Face-Track + Hormozi)", command=self.generate_single, fg_color="#e76f51", height=50, font=("Arial", 16, "bold"))
        self.generate_btn.pack(pady=15, fill="x", padx=20)
        
        self.results_frame = ctk.CTkScrollableFrame(tab, height=300)
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def import_long(self):
        path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.mov *.mkv")])
        if path:
            self.long_video = path
            self.long_label.configure(text=Path(path).name)
            self.log(f"Loaded: {path}")

    def generate_single(self):
        if not self.long_video:
            self.log("Import video first!")
            return
        if not os.path.exists("my_style_profile.json"):
            self.log("Train style first in Tab 1!")
            return
        threading.Thread(target=self._generate_single_job, daemon=True).start()

    def _generate_single_job(self):
        try:
            from trainable_viral_engine import process_long_video
            from face_tracker_reframe import reframe_with_face_tracking
            from hormozi_captions import create_hormozi_video
            
            top_n = int(self.num_clips.get())
            self.log(f"Step 1: Finding top {top_n} viral moments...")
            clips = process_long_video(self.long_video, top_n=top_n)
            
            for w in self.results_frame.winfo_children():
                w.destroy()
            
            self.log(f"Step 2: Rendering {len(clips)} clips with face-track + Hormozi + color...")
            
            for idx, clip in enumerate(clips, 1):
                self.log(f"Rendering clip {idx}/{len(clips)} Score {clip['score']}...")
                
                # Pipeline similar to batch_processor
                from batch_processor import BatchProcessor
                proc = BatchProcessor(
                    input_folder=".", output_folder=str(Path(self.long_video).parent),
                    style_profile="my_style_profile.json",
                    clips_per_video=1,
                    target_ratio="9:16" if "9:16" in self.format_opt.get() else "16:9",
                    use_face_tracking="Face-Track" in self.format_opt.get(),
                    use_hormozi_captions="No Captions" not in self.caption_style_opt.get()
                )
                
                output_folder = Path(self.long_video).parent / f"{Path(self.long_video).stem}_viral"
                output_folder.mkdir(exist_ok=True)
                final_path = proc.render_clip_pipeline(Path(self.long_video), clip, idx, output_folder)
                
                # UI
                frame = ctk.CTkFrame(self.results_frame)
                frame.pack(fill="x", pady=5, padx=5)
                ctk.CTkLabel(frame, text=f"#{idx} Score {clip['score']} | {clip['start']:.1f}s-{clip['end']:.1f}s", font=("Arial", 12, "bold")).pack(anchor="w", padx=5)
                ctk.CTkLabel(frame, text=clip['text'][:120]+"...", wraplength=900, anchor="w").pack(anchor="w", padx=5)
                ctk.CTkLabel(frame, text=f"→ {final_path}", text_color="#2a9d8f", font=("Arial", 10)).pack(anchor="w", padx=5)
            
            self.log(f"✓ DONE! {len(clips)} clips in {output_folder}")
            
        except Exception as e:
            self.log(f"Failed: {e}")
            import traceback; traceback.print_exc()

    # --- TAB 3: BATCH ---
    def build_batch_tab(self):
        tab = self.tabview.tab("3. Batch Overnight")
        
        ctk.CTkLabel(tab, text="Batch Mode - Overnight Factory", font=("Arial", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(tab, text="Drop a folder with 10 long videos (podcasts, courses, etc). Go to sleep. Wake up to 50 viral clips.", wraplength=700).pack()
        
        folder_frame = ctk.CTkFrame(tab)
        folder_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(folder_frame, text="Select Input Folder (Long Videos)", command=self.select_batch_input).pack(side="left", padx=5)
        self.batch_input_label = ctk.CTkLabel(folder_frame, text="No folder selected")
        self.batch_input_label.pack(side="left", padx=10)
        
        folder_frame2 = ctk.CTkFrame(tab)
        folder_frame2.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(folder_frame2, text="Select Output Folder", command=self.select_batch_output).pack(side="left", padx=5)
        self.batch_output_label = ctk.CTkLabel(folder_frame2, text="Will create: ./viral_output/")
        self.batch_output_label.pack(side="left", padx=10)
        self.batch_output_folder = Path("viral_output")
        
        options = ctk.CTkFrame(tab)
        options.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(options, text="Clips per video:").pack(side="left", padx=5)
        self.batch_clips_per = ctk.CTkOptionMenu(options, values=["3", "5", "10"])
        self.batch_clips_per.pack(side="left", padx=5)
        self.batch_clips_per.set("5")
        
        ctk.CTkLabel(options, text="Est. output:").pack(side="left", padx=15)
        self.batch_est_label = ctk.CTkLabel(options, text="0 videos x 5 = 0 clips")
        self.batch_est_label.pack(side="left", padx=5)
        
        self.batch_btn = ctk.CTkButton(tab, text="🌙 START OVERNIGHT BATCH (Face-Track + Hormozi + Color)", command=self.start_batch, fg_color="#2a9d8f", height=60, font=("Arial", 16, "bold"))
        self.batch_btn.pack(pady=20, fill="x", padx=20)
        
        ctk.CTkLabel(tab, text="Features enabled: ✓ Face-Tracking Reframe  ✓ Hormozi Pop Captions  ✓ Vibrant Color Grade  ✓ -14 LUFS Audio  ✓ Resume if power fails", wraplength=700, text_color="#a8dadc").pack(pady=5)

    def select_batch_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.batch_input_folder = Path(folder)
            self.batch_input_label.configure(text=str(folder))
            # Count videos
            exts = [".mp4", ".mov", ".mkv"]
            count = sum(1 for ext in exts for _ in self.batch_input_folder.glob(f"*{ext}"))
            clips_per = int(self.batch_clips_per.get())
            self.batch_est_label.configure(text=f"{count} videos x {clips_per} = {count*clips_per} clips")
            self.log(f"Batch input: {folder} ({count} videos)")

    def select_batch_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.batch_output_folder = Path(folder)
            self.batch_output_label.configure(text=str(folder))

    def start_batch(self):
        if not self.batch_input_folder:
            self.log("Select input folder first!")
            return
        if not os.path.exists("my_style_profile.json"):
            self.log("Train style first in Tab 1!")
            return
        threading.Thread(target=self._batch_job, daemon=True).start()

    def _batch_job(self):
        try:
            from batch_processor import BatchProcessor
            processor = BatchProcessor(
                input_folder=str(self.batch_input_folder),
                output_folder=str(self.batch_output_folder),
                style_profile="my_style_profile.json",
                clips_per_video=int(self.batch_clips_per.get()),
                target_ratio="9:16",
                use_face_tracking=True,
                use_hormozi_captions=True,
                color_grade="vibrant"
            )
            total = processor.run()
            self.log(f"BATCH COMPLETE! {total} clips created in {self.batch_output_folder}")
        except Exception as e:
            self.log(f"Batch failed: {e}")
            import traceback; traceback.print_exc()

    # --- TAB 4: SETTINGS ---
    def build_settings_tab(self):
        tab = self.tabview.tab("4. Settings")
        
        ctk.CTkLabel(tab, text="Pro Settings", font=("Arial", 18, "bold")).pack(pady=10)
        
        # Color
        cf = ctk.CTkFrame(tab)
        cf.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(cf, text="Color Grading:").pack(side="left", padx=10)
        self.color_opt = ctk.CTkOptionMenu(cf, values=["Vibrant (YouTube)", "Warm Podcast", "Cinematic", "Original", "My Custom LUT .cube"])
        self.color_opt.pack(side="left", padx=5)
        
        # Caption
        capf = ctk.CTkFrame(tab)
        capf.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(capf, text="Hormozi Caption:").pack(side="left", padx=10)
        self.cap_detail = ctk.CTkOptionMenu(capf, values=["Single Word Pop (Hormozi)", "3 Words with Yellow Highlight", "2 Words Uppercase"])
        self.cap_detail.pack(side="left", padx=5)
        
        # Face tracking
        ftf = ctk.CTkFrame(tab)
        ftf.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(ftf, text="Face Tracking:").pack(side="left", padx=10)
        self.face_smooth = ctk.CTkSlider(ftf, from_=0.5, to=0.95, number_of_steps=9)
        self.face_smooth.pack(side="left", padx=10)
        self.face_smooth.set(0.85)
        ctk.CTkLabel(ftf, text="Smoothing 0.85 (0.5=fast, 0.95=very smooth)").pack(side="left", padx=5)
        
        # Advanced
        adv = ctk.CTkFrame(tab)
        adv.pack(fill="x", padx=10, pady=15)
        ctk.CTkLabel(adv, text="Advanced:").pack(side="left", padx=10)
        self.silence_check = ctk.CTkCheckBox(adv, text="Auto Remove Silence")
        self.silence_check.pack(side="left", padx=5)
        self.silence_check.select()
        self.loud_check = ctk.CTkCheckBox(adv, text="Normalize -14 LUFS")
        self.loud_check.pack(side="left", padx=10)
        self.loud_check.select()
        
        ctk.CTkLabel(tab, text="\nTips:\n• For best face tracking, download yolov8n-face.pt and put in app folder\n• For custom color, export .cube LUT from Premiere/Lightroom and select 'My Custom LUT'\n• Batch mode resumes automatically if NEPA takes light - progress saved in batch_progress.json", justify="left", wraplength=800).pack(pady=20, padx=10, anchor="w")

if __name__ == "__main__":
    app = ViralEditorPro()
    app.mainloop()
