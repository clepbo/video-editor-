# GitHub Actions - Auto Build

This folder contains workflows that auto-build your app.

## build-exe.yml

**Triggers:**
- Every push to `main` branch
- Manual: Go to Actions tab -> Build Windows EXE -> Run workflow

**What it does:**
1. Sets up Windows + Python 3.10 + FFmpeg
2. Installs all dependencies from `requirements_full.txt`
3. Builds 2 EXEs with PyInstaller:
   - `ViralEditorPro.exe` - Full GUI (4 tabs, face-track, Hormozi, batch)
   - `ViralBatchCLI.exe` - CLI for overnight batch (no GUI)
4. Uploads them as artifacts (download from Actions tab)

**To download your EXE:**
1. Go to https://github.com/clepbo/video-editor-/actions
2. Click latest workflow run
3. Scroll down to Artifacts -> Download `ViralEditorPro-Windows-EXE`
4. Unzip -> Run ViralEditorPro.exe (no Python needed!)

**To create a Release:**
```bash
git tag v1.0.0
git push origin v1.0.0
```
This will auto-create a GitHub Release with EXEs attached.

**Build Time:** ~8-12 minutes on GitHub's Windows runner

**Note:** First build will be slow (downloads YOLO models etc). EXE will be ~500MB-800MB because it bundles all AI models libs. You can later optimize by excluding unused libs.
