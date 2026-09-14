"""
Viral Editor - SERMON MODE V3
For church services: Creates MEANINGFUL reels, not just cuts

New in V3:
- Complete sentences, not cut words
- Skips scripture quoting unless crucial
- Non-sequential composition: Combines different parts that support same point
- Structure: Hook -> Illustration/Explanation -> Action/Ponder
- Meaningful standalone message for viewers who didn't attend service
- 1:30-2:15 long, attention retaining

Run: python starter-app/viral_editor_sermon_mode.py
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os, subprocess, threading, json, time
from pathlib import Path
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Import sermon composer
try:
    from sermon_reel_composer import SermonReelComposer, compose_sermon_reels
    from sermon_reel_renderer import render_all_sermon_reels, render_sermon_reel
    HAS_SERMON = True
except Exception as e:
    print(f"Sermon composer not available: {e}")
    HAS_SERMON = False

class SermonEditorV3(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Viral Editor SERMON MODE V3 - Meaningful Reels (Hook->Illustration->Action)")
        self.geometry("1450x950")
        
        self.long_video = None
        self.composed_reels = []
        self.example_clips = []
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_top_bar()
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Left - Sermon info
        self.left_panel = ctk.CTkFrame(self.main_frame, width=300)
        self.left_panel.grid(row=0, column=0, sticky="nswe", padx=5, pady=5)
        self.left_panel.grid_propagate(False)
        self.create_left_panel()
        
        # Center - Preview + Reels list
        self.center_panel = ctk.CTkFrame(self.main_frame)
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.center_panel.grid_rowconfigure(1, weight=1)
        self.center_panel.grid_columnconfigure(0, weight=1)
        self.create_center_panel()
        
        # Right - Composition settings
        self.right_panel = ctk.CTkFrame(self.main_frame, width=360)
        self.right_panel.grid(row=0, column=2, sticky="nswe", padx=5, pady=5)
        self.right_panel.grid_propagate(False)
        self.create_right_panel()
        
        # Log
        self.log_box = ctk.CTkTextbox(self, height=110)
        self.log_box.grid(row=2, column=0, sticky="ew", padx=5, pady=(0,5))
        self.log("SERMON MODE V3 Ready - Creates MEANINGFUL reels, not just cuts")
        self.log("Features: Complete sentences, skips scripture unless crucial, non-sequential Hook->Illustration->Action, 1:30-2:15")

    def log(self, msg):
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.log_box.see("end")
        print(msg)
        self.update_idletasks()

    def create_top_bar(self):
        top = ctk.CTkFrame(self, height=45)
        top.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(top, text="SERMON MODE V3", font=("Arial", 16, "bold"), text_color="#e9c46a").pack(side="left", padx=10)
        ctk.CTkLabel(top, text="| Meaningful Reels | Hook→Illustration→Action | Complete Sentences | Skip Scripture | Non-Sequential | 1:30-2:15", 
                     font=("Arial", 10), text_color="#aaa").pack(side="left", padx=10)
        
        ctk.CTkButton(top, text="Import Sermon Video", command=self.import_long, width=160, fg_color="#2a9d8f", font=("Arial", 12, "bold")).pack(side="right", padx=5)
        ctk.CTkButton(top, text="Switch to Viral Mode", command=self.switch_to_viral, width=140, fg_color="#555").pack(side="right", padx=5)

    def create_left_panel(self):
        ctk.CTkLabel(self.left_panel, text="SERMON PROJECT", font=("Arial", 12, "bold"), text_color="#aaa").pack(anchor="w", padx=10, pady=(10,5))
        
        self.left_tabview = ctk.CTkTabview(self.left_panel)
        self.left_tabview.pack(fill="both", expand=True, padx=5, pady=5)
        self.left_tabview.add("Sermon")
        self.left_tabview.add("Teach AI")
        
        # Sermon tab
        sermon_tab = self.left_tabview.tab("Sermon")
        ctk.CTkLabel(sermon_tab, text="Source Sermon Video", font=("Arial", 11, "bold")).pack(anchor="w", padx=5, pady=5)
        self.media_label = ctk.CTkLabel(sermon_tab, text="No sermon loaded\n\nImport long sermon\n(30min - 3hrs)\n\nFor meaningful reels", justify="center", wraplength=220, height=110, fg_color="#1a1a1a", corner_radius=8)
        self.media_label.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(sermon_tab, text="📁 Import Sermon", command=self.import_long, fg_color="#2a9d8f").pack(fill="x", padx=5, pady=5)
        
        self.media_info = ctk.CTkLabel(sermon_tab, text="Duration: --\nSize: --\nMain points: --", justify="left", font=("Arial", 10), text_color="#888")
        self.media_info.pack(anchor="w", padx=10, pady=10)
        
        ctk.CTkLabel(sermon_tab, text="What Makes V3 Different?", font=("Arial", 11, "bold"), text_color="#e9c46a").pack(anchor="w", padx=5, pady=(10,5))
        info_text = """• Complete sentences, not cut words
• Skips scripture quoting unless crucial
• Non-sequential: combines different parts that support SAME point
• Structure: Hook (joke/viral) → Illustration/Story → Action/Ponder
• Meaningful standalone - viewers who didn't attend can understand
• Gains & retains attention"""
        ctk.CTkLabel(sermon_tab, text=info_text, justify="left", font=("Arial", 9), text_color="#aaa", wraplength=250).pack(anchor="w", padx=10, pady=5)
        
        # Teach AI tab (for sermon style)
        teach_tab = self.left_tabview.tab("Teach AI")
        ctk.CTkLabel(teach_tab, text="Teach Your Sermon Style", font=("Arial", 12, "bold")).pack(pady=5)
        ctk.CTkLabel(teach_tab, text="Import 5-10 of your best sermon reels. AI learns your preaching style, hook style, illustration style.", wraplength=220, font=("Arial", 10), text_color="#aaa").pack(pady=5)
        
        ctk.CTkButton(teach_tab, text="Add Example Reels", command=self.add_examples).pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(teach_tab, text="Clear", command=self.clear_examples, fg_color="gray", height=28).pack(fill="x", padx=5, pady=2)
        ctk.CTkButton(teach_tab, text="🧠 Train Sermon Style", command=self.train_style, fg_color="#9d4edd", height=36).pack(fill="x", padx=5, pady=10)
        
        self.example_list = ctk.CTkScrollableFrame(teach_tab, height=150)
        self.example_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.teach_status = ctk.CTkLabel(teach_tab, text="Optional - works without training", text_color="#888", font=("Arial", 9))
        self.teach_status.pack(pady=5)

    def create_center_panel(self):
        # Header
        header = ctk.CTkFrame(self.center_panel, height=35)
        header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(header, text="COMPOSED MEANINGFUL REELS", font=("Arial", 12, "bold"), text_color="#aaa").pack(side="left", padx=10)
        self.reels_info = ctk.CTkLabel(header, text="No reels yet - Import sermon and compose", font=("Arial", 10), text_color="#888")
        self.reels_info.pack(side="left", padx=20)
        
        # Reels list - main area
        self.reels_scroll = ctk.CTkScrollableFrame(self.center_panel)
        self.reels_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        self.reels_placeholder = ctk.CTkLabel(self.reels_scroll, text="🎬 Sermon Reels Will Appear Here\n\nEach reel is:\n• 1:30-2:15 long (meaningful, not too short)\n• Complete sentences (no cut words)\n• Non-sequential composition (different parts that support same point)\n• Structure: Hook (joke/viral word) → Illustration/Story → Action/Ponder\n• Skips scripture quoting unless crucial to point\n• Standalone meaningful - viewers who didn't attend can understand\n• Attention retaining\n\nImport sermon video and click 'Compose Meaningful Reels'", 
                                          font=("Arial", 12), justify="center", text_color="#555")
        self.reels_placeholder.pack(pady=30, padx=20)
        
        # Controls
        controls = ctk.CTkFrame(self.center_panel, height=45)
        controls.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        ctk.CTkButton(controls, text="📁 Open Output Folder", width=150, command=self.open_output_folder, fg_color="#555").pack(side="left", padx=5)
        ctk.CTkButton(controls, text="📊 Open Summary JSON", width=150, command=lambda: self.log("Summary JSON has hook/illustration/action breakdown"), fg_color="#555").pack(side="left", padx=5)
        ctk.CTkButton(controls, text="🎬 Compose Meaningful Reels (1:30-2:15)", width=300, fg_color="#e9c46a", text_color="black", font=("Arial", 13, "bold"), command=self.compose_reels).pack(side="right", padx=5)

    def create_right_panel(self):
        ctk.CTkLabel(self.right_panel, text="COMPOSITION SETTINGS", font=("Arial", 12, "bold"), text_color="#aaa").pack(anchor="w", padx=10, pady=(10,5))
        
        self.right_tabview = ctk.CTkTabview(self.right_panel)
        self.right_tabview.pack(fill="both", expand=True, padx=5, pady=5)
        self.right_tabview.add("Structure")
        self.right_tabview.add("Filters")
        self.right_tabview.add("Style")
        
        # Structure tab
        struct_tab = self.right_tabview.tab("Structure")
        ctk.CTkLabel(struct_tab, text="Reel Structure: Hook → Illustration → Action", font=("Arial", 11, "bold"), text_color="#e9c46a").pack(anchor="w", padx=5, pady=5)
        
        ctk.CTkLabel(struct_tab, text="Target Duration:", font=("Arial", 10)).pack(anchor="w", padx=5, pady=(10,2))
        dur_frame = ctk.CTkFrame(struct_tab)
        dur_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(dur_frame, text="Min:").pack(side="left", padx=5)
        self.min_dur = ctk.CTkOptionMenu(dur_frame, values=["60s", "90s (1:30)", "105s (1:45)"])
        self.min_dur.pack(side="left", padx=2)
        self.min_dur.set("90s (1:30)")
        ctk.CTkLabel(dur_frame, text="Max:").pack(side="left", padx=5)
        self.max_dur = ctk.CTkOptionMenu(dur_frame, values=["120s (2:00)", "135s (2:15)", "150s (2:30)"])
        self.max_dur.pack(side="left", padx=2)
        self.max_dur.set("135s (2:15)")
        
        ctk.CTkLabel(struct_tab, text="Number of reels:").pack(anchor="w", padx=5, pady=(10,2))
        self.num_reels = ctk.CTkOptionMenu(struct_tab, values=["3", "5", "7", "10"])
        self.num_reels.pack(fill="x", padx=5, pady=2)
        self.num_reels.set("5")
        
        ctk.CTkLabel(struct_tab, text="Composition Model:", font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=(15,5))
        self.model_opt = ctk.CTkOptionMenu(struct_tab, values=["Hook → Illustration → Action (Recommended)", "Hook → Explanation → Ponder", "Problem → Story → Solution", "Question → Answer → Action"])
        self.model_opt.pack(fill="x", padx=5, pady=2)
        self.model_opt.set("Hook → Illustration → Action (Recommended)")
        
        ctk.CTkLabel(struct_tab, text="This model is applied where applicable. Not all reels must follow same pattern, but AI considers it.", wraplength=300, font=("Arial", 9), text_color="#888").pack(padx=5, pady=5)
        
        # Filters tab
        filter_tab = self.right_tabview.tab("Filters")
        ctk.CTkLabel(filter_tab, text="Content Filters", font=("Arial", 11, "bold")).pack(anchor="w", padx=5, pady=5)
        
        self.skip_scripture = ctk.CTkCheckBox(filter_tab, text="Skip scripture quoting unless crucial to point")
        self.skip_scripture.pack(anchor="w", padx=10, pady=5)
        self.skip_scripture.select()
        
        self.complete_sentences = ctk.CTkCheckBox(filter_tab, text="Only complete sentences/phrases (no cut words)")
        self.complete_sentences.pack(anchor="w", padx=10, pady=5)
        self.complete_sentences.select()
        
        self.non_sequential = ctk.CTkCheckBox(filter_tab, text="Allow non-sequential composition (different parts)")
        self.non_sequential.pack(anchor="w", padx=10, pady=5)
        self.non_sequential.select()
        
        self.meaningful = ctk.CTkCheckBox(filter_tab, text="Ensure meaningful standalone message")
        self.meaningful.pack(anchor="w", padx=10, pady=5)
        self.meaningful.select()
        
        ctk.CTkLabel(filter_tab, text="Scripture Detection:", font=("Arial", 10, "bold")).pack(anchor="w", padx=5, pady=(15,5))
        ctk.CTkLabel(filter_tab, text="Detects: 'John 3:16 says', 'The Bible says', 'In the book of...', chapter:verse\nSkips unless it contains keywords of main point", wraplength=300, font=("Arial", 9), text_color="#888", justify="left").pack(padx=10, pady=5)
        
        # Style tab
        style_tab = self.right_tabview.tab("Style")
        ctk.CTkLabel(style_tab, text="Visual Style", font=("Arial", 11, "bold")).pack(anchor="w", padx=5, pady=5)
        
        ctk.CTkLabel(style_tab, text="Format:").pack(anchor="w", padx=5, pady=2)
        self.format_opt = ctk.CTkOptionMenu(style_tab, values=["9:16 Vertical (Reels) - Face-Track", "9:16 Center Crop", "1:1 Square", "16:9 Original"])
        self.format_opt.pack(fill="x", padx=5, pady=2)
        self.format_opt.set("9:16 Vertical (Reels) - Face-Track")
        
        ctk.CTkLabel(style_tab, text="Captions:").pack(anchor="w", padx=5, pady=(10,2))
        self.caption_opt = ctk.CTkOptionMenu(style_tab, values=["Hormozi Pop Multi (3 words) - Readable for sermons", "Hormozi Pop Single (1 word)", "No Captions"])
        self.caption_opt.pack(fill="x", padx=5, pady=2)
        self.caption_opt.set("Hormozi Pop Multi (3 words) - Readable for sermons")
        
        ctk.CTkLabel(style_tab, text="Color:").pack(anchor="w", padx=5, pady=(10,2))
        self.color_opt = ctk.CTkOptionMenu(style_tab, values=["Warm (Sermon - Recommended)", "Vibrant (YouTube Pop)", "Cinematic", "Original"])
        self.color_opt.pack(fill="x", padx=5, pady=2)
        self.color_opt.set("Warm (Sermon - Recommended)")
        
        ctk.CTkLabel(style_tab, text="Warm is good for church lighting, makes skin tones natural", wraplength=300, font=("Arial", 9), text_color="#888").pack(padx=5, pady=5)
        
        # Compose button
        ctk.CTkButton(style_tab, text="🎬 Compose Meaningful Reels\nHook→Illustration→Action\n1:30-2:15", 
                      command=self.compose_reels, fg_color="#e9c46a", text_color="black", height=70, 
                      font=("Arial", 12, "bold")).pack(fill="x", padx=5, pady=15)
        
        self.progress_label = ctk.CTkLabel(style_tab, text="Ready", font=("Arial", 10), text_color="#888")
        self.progress_label.pack(pady=5)
        self.progress_bar = ctk.CTkProgressBar(style_tab, width=300)
        self.progress_bar.pack(fill="x", padx=5, pady=5)
        self.progress_bar.set(0)

    def add_examples(self):
        files = filedialog.askopenfilenames(filetypes=[("Video", "*.mp4 *.mov *.mkv")])
        for f in files:
            self.example_clips.append(f)
            ctk.CTkLabel(self.example_list, text=f"✓ {Path(f).name}", anchor="w", font=("Arial", 9)).pack(fill="x", padx=5, pady=2)
        self.teach_status.configure(text=f"{len(self.example_clips)} examples")
        self.log(f"Added {len(files)} sermon reel examples")

    def clear_examples(self):
        self.example_clips = []
        for w in self.example_list.winfo_children():
            w.destroy()

    def train_style(self):
        if len(self.example_clips) < 3:
            self.log("Need at least 3 examples for sermon style")
            return
        threading.Thread(target=self._train_job, daemon=True).start()

    def _train_job(self):
        try:
            from trainable_viral_engine_v2 import StyleLearner
            learner = StyleLearner()
            profile = learner.learn_from_examples(self.example_clips, save_path="my_sermon_style.json")
            if profile:
                self.log(f"Sermon style trained! {len(self.example_clips)} examples")
                self.teach_status.configure(text=f"✓ Trained!", text_color="#2a9d8f")
        except Exception as e:
            self.log(f"Train failed: {e}")

    def import_long(self):
        path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.mov *.mkv")])
        if path:
            self.long_video = path
            self.media_label.configure(text=f"Loaded:\n{Path(path).name}\n\n{Path(path).stat().st_size/1024/1024:.1f} MB\n\nReady to compose\nmeaningful reels")
            self.log(f"Loaded sermon: {path}")
            try:
                import cv2
                cap = cv2.VideoCapture(path)
                fps = cap.get(cv2.CAP_PROP_FPS) or 30
                frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                dur = frames / fps if fps else 0
                cap.release()
                m = int(dur // 60)
                s = int(dur % 60)
                self.media_info.configure(text=f"Duration: {m}:{s:02d} ({dur:.0f}s)\nSize: {Path(path).stat().st_size/1024/1024:.1f} MB\nWill extract main points\nand compose 1:30-2:15 reels")
            except:
                pass

    def get_duration(self, text):
        if "90" in text:
            return 90
        elif "60" in text:
            return 60
        elif "105" in text:
            return 105
        elif "120" in text:
            return 120
        elif "135" in text:
            return 135
        elif "150" in text:
            return 150
        return 90

    def compose_reels(self):
        if not self.long_video:
            self.log("Import sermon video first!")
            messagebox.showwarning("No Video", "Import a long sermon video first")
            return
        if not HAS_SERMON:
            self.log("Sermon composer not available - check dependencies")
            messagebox.showerror("Missing", "Sermon composer not installed. pip install faster-whisper sentence-transformers scikit-learn")
            return
        
        threading.Thread(target=self._compose_job, daemon=True).start()

    def _compose_job(self):
        try:
            min_dur = self.get_duration(self.min_dur.get())
            max_dur = self.get_duration(self.max_dur.get())
            num_reels = int(self.num_reels.get())
            target = (min_dur + max_dur) // 2
            
            self.log(f"Composing {num_reels} meaningful sermon reels {min_dur}-{max_dur}s...")
            self.log("Steps: Transcribe -> Complete sentences -> Extract points -> Compose Hook->Ill->Action (non-sequential allowed)")
            self.progress_bar.set(0.1)
            self.progress_label.configure(text="Transcribing sermon...")
            
            composer = SermonReelComposer()
            reels = composer.compose_all_reels(
                self.long_video, 
                target_duration=target,
                num_reels=num_reels,
                min_duration=min_dur,
                max_duration=max_dur
            )
            
            self.composed_reels = reels
            self.progress_bar.set(0.5)
            self.progress_label.configure(text=f"Composed {len(reels)} reels, rendering...")
            
            # Clear placeholder
            for w in self.reels_scroll.winfo_children():
                w.destroy()
            
            # Render each reel
            output_folder = Path(self.long_video).parent / f"{Path(self.long_video).stem}_sermon_reels_V3"
            output_folder.mkdir(exist_ok=True)
            
            rendered = []
            for idx, reel in enumerate(reels, 1):
                self.progress_label.configure(text=f"Rendering reel {idx}/{len(reels)}: {reel['theme']}")
                self.progress_bar.set(0.5 + 0.5 * idx / len(reels))
                
                # Create UI card for this reel
                card = ctk.CTkFrame(self.reels_scroll, fg_color="#1a1a1a", corner_radius=8)
                card.pack(fill="x", padx=5, pady=5)
                
                # Header
                header = ctk.CTkFrame(card, fg_color="transparent")
                header.pack(fill="x", padx=10, pady=5)
                ctk.CTkLabel(header, text=f"#{idx} {reel['theme']}", font=("Arial", 13, "bold"), text_color="#e9c46a").pack(side="left")
                ctk.CTkLabel(header, text=f"{reel['total_duration']:.0f}s | Score {reel['meaningfulness_score']:.2f} | Non-seq: {reel['is_non_sequential']}", 
                             font=("Arial", 10), text_color="#888").pack(side="left", padx=10)
                
                # Structure badges
                badges = ctk.CTkFrame(card, fg_color="transparent")
                badges.pack(fill="x", padx=10, pady=2)
                if reel['hook']:
                    ctk.CTkLabel(badges, text="HOOK", fg_color="#e76f51", text_color="white", font=("Arial", 8, "bold"), corner_radius=4, width=40).pack(side="left", padx=2)
                if reel['illustration']:
                    ctk.CTkLabel(badges, text="ILLUSTRATION", fg_color="#2a9d8f", text_color="white", font=("Arial", 8, "bold"), corner_radius=4, width=80).pack(side="left", padx=2)
                if reel['action']:
                    ctk.CTkLabel(badges, text="ACTION", fg_color="#9d4edd", text_color="white", font=("Arial", 8, "bold"), corner_radius=4, width=50).pack(side="left", padx=2)
                ctk.CTkLabel(badges, text=f"{len(reel['sentences'])} segments from different parts", font=("Arial", 9), text_color="#666").pack(side="left", padx=10)
                
                # Combined text preview
                text_preview = ctk.CTkLabel(card, text=reel['combined_text'][:200] + "...", 
                                           wraplength=800, justify="left", font=("Arial", 10), text_color="#ddd", anchor="w")
                text_preview.pack(fill="x", padx=10, pady=5)
                
                # Segments breakdown
                segs_frame = ctk.CTkFrame(card, fg_color="#111", corner_radius=6)
                segs_frame.pack(fill="x", padx=10, pady=5)
                
                for s_idx, sent in enumerate(reel['sentences']):
                    role_color = {"hook": "#e76f51", "illustration": "#2a9d8f", "explanation": "#2a9d8f", "action": "#9d4edd"}.get(sent['dominant_role'], "#555")
                    seg_line = ctk.CTkFrame(segs_frame, fg_color="transparent")
                    seg_line.pack(fill="x", padx=5, pady=2)
                    ctk.CTkLabel(seg_line, text=sent['dominant_role'].upper(), fg_color=role_color, text_color="white", 
                                font=("Arial", 7, "bold"), corner_radius=3, width=70).pack(side="left", padx=2)
                    ctk.CTkLabel(seg_line, text=f"{sent['start']:.0f}s-{sent['end']:.0f}s", font=("Arial", 8), text_color="#666", width=80).pack(side="left", padx=5)
                    ctk.CTkLabel(seg_line, text=sent['text'][:70] + "...", font=("Arial", 9), text_color="#aaa", wraplength=500, anchor="w").pack(side="left", padx=5, fill="x", expand=True)
                
                # Render actual video
                try:
                    from sermon_reel_renderer import render_sermon_reel
                    
                    color_map = {
                        "Warm (Sermon - Recommended)": "warm",
                        "Vibrant (YouTube Pop)": "vibrant",
                        "Cinematic": "cinematic",
                        "Original": "original"
                    }
                    color_style = color_map.get(self.color_opt.get(), "warm")
                    
                    output_path = output_folder / f"{Path(self.long_video).stem}_reel_{idx:02d}_{reel['theme'][:20].replace(' ', '_')}_{reel['total_duration']:.0f}s.mp4"
                    
                    result = render_sermon_reel(
                        self.long_video, 
                        reel, 
                        str(output_path),
                        use_face_tracking="Face-Track" in self.format_opt.get(),
                        use_captions="No Captions" not in self.caption_opt.get(),
                        color_style=color_style
                    )
                    
                    if result:
                        rendered.append(result)
                        ctk.CTkLabel(card, text=f"✓ Saved: {Path(result).name}", font=("Arial", 9), text_color="#2a9d8f").pack(anchor="w", padx=10, pady=2)
                        self.log(f"Reel {idx} rendered: {Path(result).name}")
                
                except Exception as e:
                    self.log(f"Reel {idx} render failed: {e}")
                    import traceback
                    traceback.print_exc()
                    ctk.CTkLabel(card, text=f"✗ Render failed: {e}", font=("Arial", 9), text_color="#e76f51").pack(anchor="w", padx=10, pady=2)
            
            self.progress_bar.set(1.0)
            self.progress_label.configure(text=f"Done! {len(rendered)}/{len(reels)} meaningful reels")
            self.reels_info.configure(text=f"{len(rendered)} meaningful reels | 1:30-2:15 | Hook→Illustration→Action | Non-sequential")
            self.log(f"✓ All done! {len(rendered)} meaningful sermon reels in {output_folder}")
            
            # Save summary
            try:
                import json
                summary_path = output_folder / "sermon_reels_summary.json"
                with open(summary_path, "w", encoding="utf-8") as f:
                    json.dump([{
                        "theme": r["theme"],
                        "duration": r["total_duration"],
                        "meaningfulness": r["meaningfulness_score"],
                        "is_non_sequential": r["is_non_sequential"],
                        "combined_text": r["combined_text"],
                        "segments": len(r["sentences"])
                    } for r in reels], f, indent=2, ensure_ascii=False)
                self.log(f"Summary: {summary_path}")
            except:
                pass
            
        except Exception as e:
            self.log(f"Compose failed: {e}")
            import traceback
            traceback.print_exc()
            self.progress_label.configure(text=f"Failed: {e}")

    def open_output_folder(self):
        if self.long_video:
            folder = Path(self.long_video).parent / f"{Path(self.long_video).stem}_sermon_reels_V3"
            if folder.exists():
                os.startfile(folder) if os.name == 'nt' else subprocess.run(['xdg-open', str(folder)])
                self.log(f"Opened {folder}")
            else:
                # Try old folders
                for suffix in ["_sermon_reels", "_viral_V2", "_viral"]:
                    f = Path(self.long_video).parent / f"{Path(self.long_video).stem}{suffix}"
                    if f.exists():
                        os.startfile(f) if os.name == 'nt' else subprocess.run(['xdg-open', str(f)])
                        return
                self.log("No output folder yet - compose reels first")
        else:
            self.log("Import sermon video first")

    def switch_to_viral(self):
        self.log("Switching to Viral Mode - close this and run viral_editor_pro_v2.py")
        messagebox.showinfo("Switch Mode", "Close this window and run:\n\npython starter-app/viral_editor_pro_v2.py\n\nFor generic viral clips (continuous cuts)")

if __name__ == "__main__":
    if not HAS_SERMON:
        print("Sermon composer dependencies missing!")
        print("Install: pip install faster-whisper sentence-transformers scikit-learn")
    
    app = SermonEditorV3()
    app.mainloop()
