# Viral Editor PRO - All 3 Features Implemented

You asked for:
1. Face-tracking reframe (follows you, not center)
2. Word-by-word Hormozi captions (pop animation)
3. Batch mode (10 long videos -> 50 viral clips overnight)

All done. Here's how to run.

## Installation (Windows)

1. Install Python 3.10+ from python.org (check "Add to PATH")
2. Install FFmpeg: Download from https://ffmpeg.org, extract, add ffmpeg.exe folder to PATH
3. Open CMD in this folder and run:

```bash
pip install customtkinter faster-whisper sentence-transformers scikit-learn ultralytics opencv-python librosa python-mpv
```

4. Optional but recommended for better face tracking:
Download yolov8n-face.pt (6MB) from: https://github.com/derronqi/yolov8-face
Place it in this folder. If not present, it will use generic person detection (still works).

## How to Use

### First Time: Teach Your Style

```bash
python viral_editor_pro.py
```

Tab 1: Add 5-20 of your best viral excerpts (mp4). Click "Train Style Profile". Wait 3-5 mins. It creates `my_style_profile.json`

### Single Video Mode

Tab 2: Import a 1-2 hour podcast/course. Choose:
- Format: 9:16 Vertical (Face-Track) 
- Captions: Hormozi Pop Single
- Click Generate. It will:
  1. Find top 5 moments matching YOUR style
  2. Cut them
  3. Face-track reframe to 9:16 (smooth follow)
  4. Apply vibrant color grade
  5. Burn Hormozi pop captions (word-by-word, yellow keywords)
  6. Save to folder

### Batch Overnight Mode (Your Request)

Tab 3: 
1. Select Input Folder: e.g., `D:\My Podcasts\` containing 10 long videos
2. Select Output Folder: e.g., `D:\Viral Output\`
3. Clips per video: 5
4. Click "START OVERNIGHT BATCH"

Go to sleep. It will:
- Process each video one by one
- For each, generate 5 viral clips with full pipeline
- Save to `viral_output/VideoName/`
- Create `viral_clips_summary.csv` with all clips, scores, texts
- Save progress to `batch_progress.json` - if light goes off, it resumes where it stopped

For 10 videos x 5 clips = 50 clips, expect 2-4 hours on GPU, 6-10 hours on CPU.

## Files Explained

- `trainable_viral_engine.py` - Brain that learns your style
- `face_tracker_reframe.py` - Face-tracking 9:16 (follows face with smoothing 0.85)
- `hormozi_captions.py` - Generates ASS with pop animation and burns it
- `batch_processor.py` - Overnight factory, can also run headless: `python batch_processor.py long_videos/ --clips 5`
- `viral_editor_pro.py` - Final GUI integrating all

## Test Without GUI (Command Line)

```bash
# 1. Learn style
python -c "from trainable_viral_engine import StyleLearner; l=StyleLearner(); l.learn_from_examples(['clip1.mp4','clip2.mp4','clip3.mp4'])"

# 2. Face-track reframe only
python face_tracker_reframe.py input.mp4 output_9x16.mp4

# 3. Hormozi captions only
python hormozi_captions.py input_clip.mp4 output_captioned.mp4

# 4. Batch overnight
python batch_processor.py D:/long_videos --output D:/viral_output --clips 5
```

## Customization

- **Color Grading:** In Tab 4, choose Vibrant/Warm/Cinematic. Or export your own .cube LUT from Premiere and place as `my_look.cube`, then modify code to use `lut3d=my_look.cube`
- **Caption Style:** Edit `hormozi_captions.py` line 35 - change FontSize, colors. Yellow is &H00FFFF&, white &H00FFFFFF&
- **Face Smoothing:** In Tab 4 slider - 0.85 is sweet spot. Lower = more responsive but jittery, higher = super smooth but lags behind.

## Troubleshooting

- "No module named ultralytics" -> pip install ultralytics
- "ffmpeg not found" -> Install FFmpeg and add to PATH, restart CMD
- Face tracking slow? -> In face_tracker_reframe.py change `detect_every_n_frames=12` (detects every 0.4s instead of 0.2s)
- Captions not burning? -> Make sure ASS file path has no special characters, try moving videos to simple path like C:\videos\

Enjoy your private viral factory!
