# Fix for Python 3.14 + Path with Spaces

You have 2 issues:

### Issue 1: Python 3.14 Too New (Main Problem)

Your log shows `cp314` - you're on Python 3.14, released Oct 2025. Most AI libs (PySceneDetect, ultralytics, etc) don't have wheels for 3.14 yet.

**ERROR:**
```
ERROR: No matching distribution found for PySceneDetect>=0.6.2
...
Requires-Python >=3.7,<=3.11
```

Many libs only support up to Python 3.11.

### Solution A: Recommended - Install Python 3.11 (Best)

1. **Keep Python 3.14, but install 3.11 alongside:**
   - Go to https://www.python.org/downloads/release/python-3119/
   - Download **Windows installer (64-bit)**
   - Run installer -> Check **Add to PATH** -> Choose **Customize installation**
   - On next screen, check everything -> Next
   - **IMPORTANT:** Change install path to `C:\Python311\` (no spaces)
   - Install

2. **Use Python 3.11 for this project:**
   ```powershell
   # In your project folder C:\Users\Teasoo Consulting 3\video-editor-
   # Delete old venv
   rmdir /s /q venv

   # Create venv with Python 3.11 specifically
   C:\Python311\python.exe -m venv venv

   # Activate
   .\venv\Scripts\Activate.ps1

   # Now python should be 3.11
   python --version
   # Should show Python 3.11.9

   # Install - should work now
   pip install --upgrade pip
   pip install -r starter-app/requirements_full.txt
   ```

### Solution B: Quick Fix - Stay on 3.14 but Use Minimal Requirements

If you don't want to install Python 3.11, use minimal requirements that work on 3.14:

```powershell
# In project folder, with venv activated
pip install --upgrade pip
pip install -r starter-app/requirements_minimal.txt

# If that works, then try full fixed
pip install -r starter-app/requirements_fixed.txt
```

Or install one by one:

```powershell
pip install customtkinter opencv-python "numpy<2.0" Pillow tqdm
pip install faster-whisper
pip install sentence-transformers scikit-learn
pip install scenedetect
pip install ultralytics  # if fails, skip - app will fallback to Haar face detection
```

### Issue 2: Path with Spaces

Your path: `C:\Users\Teasoo Consulting 3\video-editor-`
Spaces in `Teasoo Consulting 3` can break some Python tools.

**Fix:**
Move project to `C:\video-editor-` (no spaces):

```powershell
# Close VS Code / CMD
# In File Explorer, copy folder C:\Users\Teasoo Consulting 3\video-editor-
# Paste to C:\video-editor-
# Then open CMD in C:\video-editor-\
```

Or use quotes always:
```powershell
cd "C:\Users\Teasoo Consulting 3\video-editor-"
```

### Complete Fix - Step by Step (Do This Now)

```powershell
# 1. Close all CMD windows

# 2. Install Python 3.11 to C:\Python311 (from python.org)

# 3. Move project to C:\video-editor- to avoid spaces
# (Copy folder via File Explorer)

# 4. Open PowerShell as Admin, run:
cd C:\video-editor-
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue

# 5. Create venv with Python 3.11
C:\Python311\python.exe -m venv venv

# 6. Activate (PowerShell may need execution policy)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\venv\Scripts\Activate.ps1

# 7. Verify Python version
python --version
# MUST show 3.11.x, not 3.14

# 8. Install
python -m pip install --upgrade pip
pip install -r starter-app/requirements_full.txt

# If still fails, use:
pip install -r starter-app/requirements_minimal.txt
pip install -r starter-app/requirements_fixed.txt

# 9. Test
python -c "import customtkinter, faster_whisper; print('All OK')"

# 10. Run
python starter-app/viral_editor_pro.py
```

### If You Still Get Errors

Paste the new error log and I'll fix it. The key is Python 3.11, not 3.14.

### Why This Happens

- Python 3.14 is bleeding edge (released Oct 2025)
- AI libs like PyTorch, ultralytics, scenedetect take 3-6 months to release wheels for new Python
- Python 3.11 is the sweet spot: stable, all libs support it, still fast
- Python 3.12/3.13 also mostly work, but 3.11 is safest

### Alternative: Use GitHub Actions EXE (No Python Needed)

If you don't want to fix Python, just download the pre-built EXE:

1. Go to https://github.com/clepbo/video-editor-/actions
2. Latest Build Windows EXE -> Artifacts -> Download
3. Run ViralEditorPro.exe (still needs FFmpeg installed)

This bypasses Python install entirely.
