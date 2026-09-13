# Video Editor - Private AI Viral Studio

Private, local, trainable video editor that learns YOUR viral style and converts long videos into viral excerpts.

**100% Offline | No API Costs | Your Style, Not Generic**

## 🚀 Features

### 1. Trainable Viral AI (Your Custom Style)
- Feed it 5-20 clips you LOVE
- It learns your hook style, pacing, energy via embeddings (`all-MiniLM-L6-v2`)
- Scores new videos against YOUR style, not generic virality

### 2. Face-Tracking Reframe 9:16
- YOLOv8 face tracking that follows you, not center crop
- Smooth EMA tracking (0.85 smoothing)
- Fallback to person detection if face model not present
- File: `starter-app/face_tracker_reframe.py`

### 3. Hormozi-Style Pop Captions
- Word-by-word pop animation with scale effect
- Yellow highlight for keywords (STOP, SECRET, NEVER, HOW)
- Montserrat ExtraBold, white with thick black stroke
- File: `starter-app/hormozi_captions.py`

### 4. Batch Overnight Factory
- Drop 10 long videos in folder -> Get 50 viral clips by morning
- Resume if power fails (progress saved in `batch_progress.json`)
- Full pipeline: cut + face-track + color grade + captions + audio normalize
- File: `starter-app/batch_processor.py`

### 5. Other Pro Features
- Auto silence removal
- Auto color grading (Vibrant, Warm, Cinematic, Custom LUT .cube)
- Audio loudness normalize to -14 LUFS
- Trainable style profiles

## 📁 Project Structure

```
/local-ai-video-editor-plan.md      - Initial blueprint for custom editor
/viral-clip-ai-blueprint.md         - Trainable viral AI architecture
/starter-app/
  ├── viral_editor_pro.py           - MAIN APP (integrated all features)
  ├── main.py                       - Simple starter GUI
  ├── enhanced_main_with_teaching.py - Teach + Generate UI
  ├── trainable_viral_engine.py     - Brain: learns your style
  ├── face_tracker_reframe.py       - Face-tracking 9:16 reframe
  ├── hormozi_captions.py           - Hormozi pop captions generator
  ├── batch_processor.py            - Overnight batch processor
  ├── requirements.txt              - Dependencies
  └── README_PRO.md                 - Detailed PRO guide
```

## 🛠️ Installation

### Windows

1. Install Python 3.10+ from python.org (check "Add to PATH")
2. Install FFmpeg from https://ffmpeg.org - add to PATH
3. Install dependencies:

```bash
pip install customtkinter faster-whisper sentence-transformers scikit-learn ultralytics opencv-python librosa python-mpv
```

4. Optional for better face tracking: Download `yolov8n-face.pt` from https://github.com/derronqi/yolov8-face and place in app folder

## 🎯 Quick Start

### 1. Teach Your Style (First Time)

```bash
python starter-app/viral_editor_pro.py
```

- Tab 1: Add 5-20 of your best viral excerpts -> Click "Train Style Profile"
- Wait 3-5 mins - creates `my_style_profile.json`

### 2. Single Video Test

- Tab 2: Import long video (1-2hr podcast)
- Choose Format: `9:16 Vertical (Face-Track)` and Captions: `Hormozi Pop Single`
- Click Generate -> Get 5 viral clips with full pipeline

### 3. Batch Overnight (10 videos -> 50 clips)

- Tab 3: Select Input Folder (with long videos) and Output Folder
- Clips per video: 5
- Click "START OVERNIGHT BATCH"
- Go to sleep - wakes up to 50 clips + `viral_clips_summary.csv`

### Command Line Batch (Headless)

```bash
python starter-app/batch_processor.py D:/long_videos --output D:/viral_output --clips 5
```

## 🧠 How Trainable AI Works

```
Your 10 Example Clips
        ↓
Transcribe (faster-whisper) + Embed (MiniLM) = Your Style Vector
        ↓
Long Video -> 150 Candidates (20-45s each)
        ↓
Score Each Candidate:
  60% Style Similarity to YOUR vector
  25% Hook Score (question, "how to", "secret")
  10% Audio Energy
  5% Visual (face present)
        ↓
Top 5 Non-Overlapping -> Full Render Pipeline
```

## 🎨 Customization

- **Color Grading:** Tab 4 -> Choose Vibrant/Warm/Cinematic or load custom .cube LUT from Premiere
- **Caption Style:** Edit `hormozi_captions.py` - FontSize, colors, pop animation timing
- **Face Smoothing:** Tab 4 slider 0.5-0.95 (0.85 = sweet spot)

## 📊 What Makes This Better Than OpusClip/CapCut?

| Feature | OpusClip/CapCut | This App |
|---------|----------------|----------|
| Learns YOUR taste | No, generic | YES |
| Offline | No, cloud | YES, 100% local |
| Cost | $15-50/month | $0 |
| Face-track 9:16 | Basic | YOLOv8 + smoothing |
| Hormozi captions | Template | Full custom pop |
| Privacy | Uploads to cloud | Never leaves PC |

## 🔧 Troubleshooting

- `ffmpeg not found` -> Install FFmpeg and add to PATH
- `No module named ultralytics` -> pip install ultralytics
- Face tracking slow? -> In `face_tracker_reframe.py` set `detect_every_n_frames=12`
- Batch resume? -> Progress saved in `batch_progress.json` - just restart

## 📝 License

Private use - for your own PC as requested. All dependencies are open-source.

## 🙏 Credits

Built with: FFmpeg, faster-whisper, sentence-transformers, ultralytics YOLOv8, OpenCV, CustomTkinter

---

**Author:** clepbo
**Repo:** https://github.com/clepbo/video-editor-
