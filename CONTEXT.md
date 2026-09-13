# Context - Auto Updated

This file tracks the evolution of this project. The agent will always update this context on every change.

## Current State (2026-09-13)

**Goal:** Private, local, trainable video editor for desktop that learns YOUR viral style.

**Status:** ✅ Initial PRO version pushed

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

**Tech Stack:**
- Python 3.10+, CustomTkinter, FFmpeg
- faster-whisper, sentence-transformers, ultralytics, opencv

**Next Planned:**
- [ ] Auto B-roll insertion
- [ ] Voice cloning for dubbing
- [ ] Auto chapter detection
- [ ] Export to .exe with PyInstaller

**Repo:** https://github.com/clepbo/video-editor-
**Last Updated:** 2026-09-13 21:30 UTC
