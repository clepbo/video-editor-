# Trainable Viral Clip AI - How It Works (Your Custom Version)

You don't want random viral clips. You want clips that *look like the examples you give it*. That's called **Few-Shot Style Learning** and you can build it 100% offline.

---

### The Core Idea: Teach It Your Style

Most apps use a generic "virality score". Yours will work like this:

1.  **You feed it 5-20 clips you LOVE** (your best excerpts)
2.  It analyzes them and learns: 
    - What kind of sentences you like (hooks, questions, punchlines)
    - How long your clips are (15s? 30s? 60s?)
    - Your energy level (fast cuts, loud, calm?)
    - Your visual style (face close-up, text on screen?)
3.  Then when you give it a 2-hour video, it finds moments that *match that learned style*

No training a huge AI needed. Just smart similarity search.

### The Full Pipeline (Long Video -> Viral Excerpts)

```
LONG VIDEO (2 hours)
      |
      v
[1] TRANSCRIBE + DIARIZE (faster-whisper)
    -> Every word with timestamp + who spoke
      |
      v
[2] CHUNK INTO CANDIDATES
    -> Use PySceneDetect + silence detection to create 100-300 possible clips (10-60s each)
      |
      v
[3] EXTRACT FEATURES FOR EACH CANDIDATE (The Brain)
    For each candidate clip, calculate:
    
    a) TEXT FEATURE (Most Important - 60% of score)
       - Embedding: sentence-transformers/all-MiniLM-L6-v2 (384-dim vector, runs on CPU)
       - Hook Score: Does it start with "The reason...", "How I...", "Stop doing...", Question?
       - Value Score: Does it contain numbers, steps, "secret", "mistake"?
       - Sentiment/Emotion: High emotion = more viral
    
    b) AUDIO FEATURE (20% of score)
       - Energy: Loudness, speech speed (fast = more engaging)
       - No silence inside
       - Laughter / emphasis detection
    
    c) VISUAL FEATURE (20% of score)
       - Face present? (YOLOv8 face)
       - Motion / scene change?
       - Centered subject?
      |
      v
[4] STYLE MATCHING (Your Custom Part)
    - You have your 5-20 example clips -> transcribe them -> embed them -> average them = YOUR STYLE VECTOR
    - For each candidate, calculate Cosine Similarity to YOUR STYLE VECTOR
    - Score = (0.6 * TextSimilarity) + (0.2 * AudioEnergy) + (0.2 * HookScore) + StyleBonus
    
    Example: If your examples are all "motivational punchlines", a candidate that says "You will never succeed unless..." will score 0.92 similarity.
      |
      v
[5] RANK + SELECT TOP 5-10
    - Pick top scoring clips, but ensure they don't overlap
    - Add 0.3s padding at start/end
      |
      v
[6] AUTO-EDIT EACH CLIP (Your other features)
    a) Silence Removal: Trim internal pauses >0.4s
    b) Auto-Reframe: YOLOv8 tracks face, crop to 9:16 / 1:1 / 16:9
    c) Captions: Burn word-by-word captions (like Alex Hormozi style) with faster-whisper
    d) Color Grading: Auto-grade
       - Option 1: FFmpeg auto: eq=contrast=1.1:brightness=0.05:saturation=1.2
       - Option 2: Apply your custom LUT (.cube file) - you can export LUT from Lightroom/Premiere
       - Option 3: Auto white balance with OpenCV
    e) Audio Polish: Loudness normalize to -14 LUFS (YouTube standard) + noise reduce
      |
      v
    FINAL VIRAL CLIPS READY
```

### How You "Teach" It - The UI

**Tab 1: TEACH AI YOUR STYLE**
- Button: "Import Example Clips (5-20 videos)"
- App transcribes them in background
- Shows you what it learned: "Your style: Avg 28s, Hook type: Questions (70%), Energy: High"
- Saves to `my_style_profile.json` -> Contains embeddings + stats

**Tab 2: CREATE VIRAL CLIPS**
- Import long video
- Choose: How many clips? (5), Length? (15-45s), Platform? (9:16, 16:9)
- Click "Generate" -> It scores and renders

### Tech Stack (All Local, No Internet)

```
pip install faster-whisper sentence-transformers scikit-learn
pip install ultralytics opencv-python librosa
```

- **Embedding Model:** `all-MiniLM-L6-v2` - 80MB, runs on CPU, very fast
- **Transcription:** `faster-whisper base` or `small` - 1 hour video ~3 min on GPU, ~15 min on CPU
- **Face Tracking:** `yolov8n-face` - 6MB model
- **Vector Comparison:** Just `sklearn.metrics.pairwise.cosine_similarity` - no database needed for <1000 clips

### Color Grading - How to Add It

You wanted color grading too. 3 levels:

**Level 1 - Auto Fix (Free, easy):**
```python
# FFmpeg filter
vf = "eq=contrast=1.08:brightness=0.02:saturation=1.15,unsharp=5:5:0.8:3:3:0.4"
```

**Level 2 - Your Custom LUT:**
Export a .cube LUT from any editing app, then apply:
```
ffmpeg -i input.mp4 -vf lut3d=my_look.cube output.mp4
```
You can have multiple looks: "My Podcast Look", "My Vlog Look"

**Level 3 - AI Auto-Grade (Advanced):**
Use `MiAlgo` or OpenCV auto white balance + exposure.

### What Makes Yours Better Than OpusClip/CapCut?

| Feature | OpusClip / CapCut | YOUR Custom App |
|---------|-------------------|-----------------|
| Learns YOUR taste | No, generic viral | YES, from your 5-20 examples |
| Runs offline | No, cloud + pay per minute | YES, 100% local |
| Custom captions style | Limited templates | Any style you code |
| Color grading | Basic filters | Your own LUTs |
| Cost | $15-50/month | $0 after building |
| Privacy | Uploads your video to cloud | Never leaves your PC |

### Data You Need to Provide

To make it learn well, collect:
- 10 clips that performed well for you (or that you wish you made)
- Try to keep them similar niche: e.g., all motivational, or all teaching moments
- The more consistent your examples, the better it learns

If you have different styles (e.g., sometimes funny, sometimes serious), create 2 profiles: "Funny Style" and "Serious Style"

### Next Steps to Build MVP (2-3 weeks for this feature)

**Week 1:** Build the TEACH part - import examples -> transcribe -> save embeddings
**Week 2:** Build SCORING - long video -> candidates -> score vs your style
**Week 3:** Build RENDERING - auto-reframe + captions + color + export

I have coded the core engine for you in `trainable_viral_engine.py`
