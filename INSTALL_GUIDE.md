# Step-by-Step Installation Guide - Viral Editor PRO (Windows)

This guide takes you from **zero** to generating viral clips, even if you've never installed Python before.

---

### STEP 1: Install Python 3.10+ (5 mins)

1.  Go to **https://www.python.org/downloads/**
2.  Click **Download Python 3.11.x** (or 3.10+) - big yellow button
3.  **IMPORTANT:** Run the installer. On the FIRST screen, check **TWO boxes**:
    - ✅ `Add python.exe to PATH` (bottom left)
    - ✅ `Use admin privileges when installing py.exe` (if you see it)
4.  Click **Install Now**
5.  Wait for install to finish -> Click **Close**
6.  **Verify:** Press `Win + R` -> Type `cmd` -> Enter -> Type:
    ```bash
    python --version
    ```
    Should show `Python 3.11.x`. If it says `'python' is not recognized`, you forgot to check Add to PATH - uninstall and reinstall with box checked.

---

### STEP 2: Install FFmpeg (The Video Engine) (5 mins)

FFmpeg does all video cutting/cropping. Without it, nothing works.

**Option A - Easiest (Recommended):**
1. Go to **https://www.gyan.dev/ffmpeg/builds/**
2. Under **release builds**, download **ffmpeg-release-essentials.zip** (~80MB)
3. Extract the zip to `C:\` so you get `C:\ffmpeg-7.1.1-essentials_build\`
4. Inside that folder, go to `bin` -> You should see `ffmpeg.exe`, `ffprobe.exe`
5. **Add to PATH:**
   - Press `Win + S` -> Search `Edit the system environment variables` -> Open it
   - Click **Environment Variables** (bottom right)
   - Under **System variables**, find `Path` -> Click **Edit**
   - Click **New** -> Paste: `C:\ffmpeg-7.1.1-essentials_build\bin` (adjust version number)
   - Click OK -> OK -> OK
6. **Verify:** Close CMD and open new CMD -> Type:
   ```bash
   ffmpeg -version
   ```
   Should show ffmpeg version. If not, restart PC and try again.

**Option B - With Chocolatey (if you have it):**
```bash
choco install ffmpeg
```

---

### STEP 3: Download This Project (2 mins)

**Option A - With Git (if you have git):**
```bash
git clone https://github.com/clepbo/video-editor-.git
cd video-editor-
```

**Option B - Without Git (Easiest):**
1. Go to **https://github.com/clepbo/video-editor-**
2. Click green **Code** button -> **Download ZIP**
3. Extract ZIP to `C:\video-editor-` or `D:\video-editor-\`
4. Open that folder

You should see folders: `starter-app`, `.github`, and files `README.md`, `CONTEXT.md`, etc.

---

### STEP 4: Open CMD in This Folder and Create Virtual Environment (Recommended)

1.  Inside the `video-editor-` folder, click address bar at top -> Type `cmd` -> Press Enter. CMD opens in that folder.
2.  Create virtual environment (keeps dependencies clean):
    ```bash
    python -m venv venv
    ```
3.  Activate it:
    ```bash
    venv\Scripts\activate
    ```
    You should see `(venv)` at start of line. If you see it, you're in venv.

**If you skip venv, it's okay - just install globally. But venv is cleaner.**

---

### STEP 5: Install Dependencies (5-10 mins, needs internet)

With `(venv)` active and CMD in project folder, run:

```bash
pip install --upgrade pip
pip install -r starter-app/requirements_full.txt
```

This installs:
- `customtkinter` - Modern GUI
- `faster-whisper` - Offline transcription
- `sentence-transformers` - Learns your style
- `ultralytics` - YOLOv8 face tracking
- `opencv-python` - Video processing
- `scikit-learn`, `librosa`, etc.

**First time will take 5-10 mins** - it downloads ~1GB of libs. Be patient.

**If you have slow internet in PH:** Run this at night, or use:
```bash
pip install customtkinter faster-whisper sentence-transformers scikit-learn ultralytics opencv-python librosa python-mpv PySceneDetect --no-cache-dir
```

**Verify install:**
```bash
python -c "import customtkinter, faster_whisper, ultralytics; print('All OK')"
```
Should print `All OK` with no errors.

---

### STEP 6: Optional - Download Better Face Model (1 min)

For better face-tracking (follows face, not just person):

1.  Go to **https://github.com/derronqi/yolov8-face** -> Releases -> Download `yolov8n-face.pt` (6MB)
2.  Or direct: Search `yolov8n-face.pt download` on Google
3.  Place `yolov8n-face.pt` inside `starter-app/` folder, next to `viral_editor_pro.py`

If you skip this, app will still work - it will detect person instead of face (still good, but face is better).

---

### STEP 7: Run The PRO App (30 seconds)

Still in CMD with `(venv)` active:

```bash
python starter-app/viral_editor_pro.py
```

A window should open: **Viral Editor PRO - Private AI Studio** with 4 tabs.

**If error `No module named customtkinter`:** You forgot to activate venv or install requirements. Run Step 5 again.

**If error `ffmpeg not found`:** FFmpeg not in PATH - redo Step 2 and restart CMD.

---

### STEP 8: Teach AI Your Style (First Time Only - 5 mins)

This is the magic - you teach it what YOU consider viral.

1.  **Prepare 5-20 example clips:** Find your best viral excerpts (15-40s each) - clips that performed well or that you wish you made. Put them in one folder like `D:\MyBestClips\`

2.  In app, **Tab 1: Teach AI Your Style**
    - Click **Add Example Clips** -> Select your 5-20 clips
    - You should see list: `✓ my_best_clip1.mp4` etc.
    - Click **🧠 Train Style Profile** (purple button)

3.  **Wait 3-5 mins:** It transcribes each clip offline (first time downloads whisper model ~150MB). Log at bottom shows progress.

4.  **Success:** Status turns green: `✓ Trained on 10 clips! Ready.` It creates `my_style_profile.json` in app folder (your style fingerprint).

**Tip:** Use consistent niche - all motivational, or all teaching. If you have 2 styles (funny vs serious), train 2 separate profiles and rename file: `funny_style.json`, `serious_style.json`

---

### STEP 9: Generate Viral Clips - Single Video Test (2-10 mins)

1.  **Tab 2: Single Video**
    - Click **Import Long Video** -> Select a 30min - 2hr podcast/course (mp4)
    - Choose:
      - Clips: `5`
      - Format: `9:16 Vertical (Face-Track)` (follows you)
      - Captions: `Hormozi Pop Single` (1 word pop)
    - Click **🔥 GENERATE VIRAL CLIPS**

2.  **What happens:**
    - Step 1: Transcribes long video with timestamps (3 min on GPU, 15 min on CPU for 1hr video)
    - Step 2: Creates 100-200 candidates, scores vs YOUR style
    - Step 3: For each top clip: Cut -> Face-track reframe -> Vibrant color -> Hormozi captions -> Save

3.  **Output:** Folder next to your source video: `YourVideo_viral/` with 5 final mp4s like `YourVideo_viral_1_score92.5_FINAL.mp4`

Play them - they should have face-tracking 9:16 and pop captions.

---

### STEP 10: Batch Overnight Mode - 10 Videos -> 50 Clips (Overnight)

This is for when you have many long videos.

1.  **Prepare folders:**
    - Input: `D:\LongVideos\` with 10 long videos (e.g., `podcast1.mp4`, `podcast2.mp4`...)
    - Output: `D:\ViralOutput\` (create empty folder)

2.  **Tab 3: Batch Overnight**
    - Click **Select Input Folder** -> Choose `D:\LongVideos\`
    - Click **Select Output Folder** -> Choose `D:\ViralOutput\`
    - Clips per video: `5`
    - Shows: `10 videos x 5 = 50 clips`
    - Click **🌙 START OVERNIGHT BATCH**

3.  **Go to sleep:** It processes one by one. Log shows progress. For 10x 1hr videos:
    - With NVIDIA GPU: ~2-4 hours
    - CPU only: ~6-10 hours

4.  **Resume if NEPA takes light:** Progress saved in `batch_progress.json`. Just restart app and click Start Batch again - it skips done videos.

5.  **Morning:** Check `D:\ViralOutput\`:
    - Each video has subfolder: `podcast1/` with 5 clips
    - `viral_clips_summary.csv` - All 50 clips with score, text, file path - open in Excel to pick best

---

### STEP 11: (Optional) Build EXE So You Don't Need Python Next Time

If you want single .exe that runs on any PC without installing Python:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ViralEditorPro starter-app/viral_editor_pro.py
```

EXE will be in `dist/ViralEditorPro.exe` (~600MB because it bundles AI libs). Double-click to run.

**Easier:** Use GitHub Actions - every push auto-builds EXE. Go to https://github.com/clepbo/video-editor-/actions -> Download artifact.

---

### STEP 12: Using GitHub Actions EXE (No Python Install Needed)

If you don't want to install Python at all:

1. Go to **https://github.com/clepbo/video-editor-/actions**
2. Click latest **Build Windows EXE** run (green check)
3. Scroll to **Artifacts** -> Download **ViralEditorPro-Windows-EXE**
4. Extract ZIP -> Run `ViralEditorPro.exe`
5. Still need FFmpeg installed (Step 2) - EXE needs ffmpeg.exe in PATH

---

### Troubleshooting

| Error | Fix |
|-------|-----|
| `python not recognized` | Reinstall Python with Add to PATH checked |
| `ffmpeg not found` | Add ffmpeg bin to PATH and restart CMD/PC |
| `No module named customtkinter` | Run `pip install -r starter-app/requirements_full.txt` with venv activated |
| `YOLO model download fails` | No internet? App will fallback to Haar face detection - still works |
| `CUDA out of memory` | In `trainable_viral_engine.py` change `device="cuda"` to `device="cpu"` |
| Face tracking slow | In `face_tracker_reframe.py` set `detect_every_n_frames=12` (was 6) |
| Captions not burning | Make sure video path has no spaces or special chars - move to `C:\videos\` |
| Batch stuck | Check `batch_log.txt` in output folder for error |

### Hardware Recommendations

- **Minimum:** Intel i5, 8GB RAM, SSD (HDD will be very slow)
- **Recommended:** 16GB RAM + NVIDIA GTX 1660+ (6GB VRAM) - 5x faster transcription
- **Storage:** 10GB free for models + temp files

### Offline Usage

After first install, **100% offline**:
- Models downloaded once (~1GB)
- No API keys, no internet needed to generate clips
- Perfect for unstable internet in Port Harcourt

---

### Quick Command Reference

```bash
# Activate venv
venv\Scripts\activate

# Run PRO app
python starter-app/viral_editor_pro.py

# Run single module tests
python starter-app/face_tracker_reframe.py input.mp4 output_9x16.mp4
python starter-app/hormozi_captions.py input_clip.mp4 output_captioned.mp4
python starter-app/batch_processor.py D:/long_videos --output D:/viral_output --clips 5

# Build EXE locally
pyinstaller --onefile --windowed --name ViralEditorPro starter-app/viral_editor_pro.py
```

---

**Need help?** Open an issue at https://github.com/clepbo/video-editor-/issues or check `CONTEXT.md` for latest updates.

**Enjoy your private viral factory!** 🚀
