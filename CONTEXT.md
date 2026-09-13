# Context - Auto Updated

This file tracks the evolution of this project. The agent will always update this context on every change.

## Current State (2026-09-13 21:42 UTC)

**Goal:** Private, local, trainable video editor for desktop that learns YOUR viral style.

**Status:** ✅ PRO version + Auto EXE Build Action added

**Implemented Features:**
1. ✅ Trainable Viral AI Engine (`trainable_viral_engine.py`)
   - Learns from 5-20 example clips
   - Embeddings with all-MiniLM-L6-v2
   - Style profile: my_style_profile.json

2. ✅ Face-Tracking Reframe (`face_tracker_reframe.py`)
   - YOLOv8 face tracking with EMA smoothing 0.85
   - 9:16 vertical that follows speaker
   - Fallback to Haar cascade

3. ✅ Hormozi Pop Captions (`hormozi_captions.py`)
   - Word-level timestamps with faster-whisper
   - ASS with pop animation: fscx80->130->100
   - Yellow keyword highlight

4. ✅ Batch Overnight Factory (`batch_processor.py`)
   - Folder in -> 50 clips out
   - Resume on power failure
   - Summary CSV

5. ✅ Integrated PRO GUI (`viral_editor_pro.py`)
   - 4 Tabs: Teach, Single, Batch, Settings
   - Color grading, audio normalize, silence removal

6. ✅ GitHub Actions Auto-Build (.github/workflows/build-exe.yml)
   - Triggers on every push to main
   - Builds ViralEditorPro.exe (GUI) + ViralBatchCLI.exe (CLI)
   - Uploads as artifact (30 days retention)
   - Auto-release on git tag
   - Download from: Actions tab -> Latest run -> Artifacts

**Tech Stack:**
- Python 3.10+, CustomTkinter, FFmpeg
- faster-whisper, sentence-transformers, ultralytics, opencv
- PyInstaller for EXE

**Build Instructions:**
- Local: `pyinstaller --onefile --windowed starter-app/viral_editor_pro.py`
- GitHub: Push to main, wait 8-12 min, download artifact from Actions

**Next Planned:**
- [ ] Auto B-roll insertion
- [ ] Voice cloning for dubbing
- [ ] Auto chapter detection
- [ ] Reduce EXE size (currently ~600MB)

**Repo:** https://github.com/clepbo/video-editor-
**Actions:** https://github.com/clepbo/video-editor-/actions
**Last Updated:** 2026-09-13 21:42 UTC
