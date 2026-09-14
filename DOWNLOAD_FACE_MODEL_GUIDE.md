# How to Download and Install yolov8n-face.pt (Face Tracking Model)

This model makes your 9:16 vertical reframe **10x more accurate** - it tracks FACES, not just persons.

- **Without it:** App detects person (body) and crops around body - still works, but can be off-center if you move
- **With it:** App detects face specifically and keeps face centered - much better for podcasts/talking head

**Size:** 6MB only
**Required:** No, optional - app works without it (fallback to person detection)

---

### Option 1: Auto-Download (Easiest - 1 Command) ✅ Recommended

You already have the script in your repo:

```cmd
(venv) C:\Users\Teasoo Consulting 3\video-editor->python starter-app/download_face_model.py
```

What it does:
- Downloads from GitHub releases (6MB)
- Saves to `starter-app/yolov8n-face.pt` and also to project root
- Shows progress bar

Expected output:
```
Downloading from https://github.com/derronqi/yolov8-face/releases/download/v1.0/yolov8n-face.pt...
yolov8n-face.pt: 100%|████| 6.21M/6.21M [00:02<00:00, 2.5MB/s]
✓ Downloaded to C:\...\starter-app\yolov8n-face.pt
SUCCESS! Face model installed.
```

If it says `Model already exists`, you're done!

---

### Option 2: Manual Download (If Auto Fails)

**Step 1:** Go to one of these links in your browser:

- **GitHub:** https://github.com/derronqi/yolov8-face
  - Click **Releases** on right side -> Find `yolov8n-face.pt` -> Download
  
- **Direct link (try this):** 
  https://github.com/derronqi/yolov8-face/releases/download/v1.0/yolov8n-face.pt
  - Browser will download `yolov8n-face.pt` (6MB)

- **HuggingFace Mirror:**
  https://huggingface.co/derronqi/yolov8-face/blob/main/yolov8n-face.pt
  - Click Download icon

**Step 2:** Place the file in **BOTH** of these locations (copy to both):

1. `C:\Users\Teasoo Consulting 3\video-editor-\starter-app\yolov8n-face.pt`
2. `C:\Users\Teasoo Consulting 3\video-editor-\yolov8n-face.pt`

**How to place:**
- After download, file is in `Downloads` folder
- Open File Explorer -> Go to Downloads -> Find `yolov8n-face.pt`
- Copy (Ctrl+C)
- Go to `C:\Users\Teasoo Consulting 3\video-editor-\starter-app\` -> Paste (Ctrl+V)
- Go to `C:\Users\Teasoo Consulting 3\video-editor-\` -> Paste again

**Step 3:** Verify:

```cmd
dir starter-app\yolov8n-face.pt
```

Should show ~6,200,000 bytes.

---

### Option 3: Using Python (If Browser Download Blocked)

In CMD with venv active:

```cmd
python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/derronqi/yolov8-face/releases/download/v1.0/yolov8n-face.pt', 'starter-app/yolov8n-face.pt'); print('Downloaded')"
```

Or:

```cmd
pip install gdown
gdown https://github.com/derronqi/yolov8-face/releases/download/v1.0/yolov8n-face.pt -O starter-app/yolov8n-face.pt
```

---

### Option 4: Let YOLO Auto-Download (Fallback)

If you don't download face model, the app will:

1. First try to load `yolov8n-face.pt` (face-specific)
2. If not found, auto-download `yolov8n.pt` (generic person detection, 6MB) via ultralytics
3. If that fails, use OpenCV Haar Cascade (built-in, no download)

So even without face model, face-tracking reframe still works - just less accurate.

You can force generic model by deleting face model - app will fallback.

---

### How to Know Which Model Is Being Used?

Run your app and check log at bottom:

- **With face model:**
  ```
  Loading face model: yolov8n-face.pt
  YOLO model loaded
  ```

- **Without face model (fallback):**
  ```
  Loading YOLOv8n (generic person detection) - will detect person as fallback
  For better face tracking, download yolov8n-face.pt
  ```

Both work, but face model is better for talking-head videos.

---

### Where Exactly to Place? (Visual)

```
C:\Users\Teasoo Consulting 3\video-editor-\
├── starter-app\
│   ├── viral_editor_pro.py
│   ├── face_tracker_reframe.py
│   ├── yolov8n-face.pt  <-- PUT HERE (1)
│   └── ...
├── yolov8n-face.pt      <-- AND HERE (2) - for safety
├── README.md
└── ...
```

Put in both places to be safe - code checks both.

---

### Troubleshooting

| Problem | Fix |
|---------|-----|
| Download stuck at 0% | Try manual browser download, or use HuggingFace mirror |
| `File not found` after download | Check you placed in `starter-app/` folder, not just Downloads |
| Still says "generic person detection" | Restart app after placing file. Check filename is exactly `yolov8n-face.pt` (lowercase, hyphen) |
| `yolov8n-face.pt is not a valid model` | File corrupted - delete and re-download (should be ~6.2MB) |
| Want to test face tracking? | Run: `python starter-app/face_tracker_reframe.py test_input.mp4 test_output_9x16.mp4` |

---

### Test Face Tracking After Install

1. Place model as above
2. Run:
```cmd
python starter-app/download_face_model.py
# Should say "Model already exists"

python -c "from starter-app.face_tracker_reframe import FaceTrackerReframer; r=FaceTrackerReframer(); print('Face model loaded OK')"
```

3. In app, generate a 9:16 clip - log should say `Loading face model: yolov8n-face.pt`

Enjoy better face tracking! 🎯
