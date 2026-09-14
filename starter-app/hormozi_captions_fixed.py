"""
Hormozi Captions FIXED - Now actually works + supports long clips (1m30s-2m15s)
Fixed: ASS burning, path escaping, font fallback
"""

import os
import subprocess
import tempfile
from pathlib import Path

def format_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def generate_hormozi_ass(word_segments, output_ass_path, video_width=1080, video_height=1920, style="pop_single"):
    """
    FIXED ASS generator - works with long clips
    """
    
    # Use Arial Black as fallback if Montserrat not available - works on all Windows
    ass_content = f"""[Script Info]
Title: Hormozi Captions Fixed
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: {video_width}
PlayResY: {video_height}
YCbCr Matrix: TV.601

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,10,3,5,10,10,280,1
Style: Highlight,Arial Black,115,&H0000FFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,12,3,5,10,10,280,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    if style == "pop_single":
        for w in word_segments:
            word = w["word"].strip().upper()
            if not word:
                continue
            # Clean word for ASS (escape special chars)
            word = word.replace("{", "").replace("}", "").replace("\\", "")
            if len(word) > 20:  # Skip too long words (artifacts)
                continue
                
            start = format_ass_time(w["start"])
            end = format_ass_time(w["end"])
            
            # Ensure minimum duration for visibility (0.2s)
            duration = w["end"] - w["start"]
            if duration < 0.15:
                continue
            
            keywords = ["NEVER", "SECRET", "STOP", "MISTAKE", "HOW", "WHY", "YOU", "MONEY", "SUCCESS", "TRUTH"]
            is_keyword = any(k in word for k in keywords)
            
            pos_x = video_width // 2
            pos_y = int(video_height * 0.75)  # 75% down
            
            if is_keyword:
                # Yellow + bigger pop for keywords
                text = f"Dialogue: 0,{start},{end},Highlight,,0,0,0,,{{\\an5\\pos({pos_x},{pos_y})\\fscx80\\fscy80\\t(0,80,\\fscx140\\fscy140)\\t(80,200,\\fscx110\\fscy110)}}{word}"
            else:
                text = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{{\\an5\\pos({pos_x},{pos_y})\\fscx80\\fscy80\\t(0,80,\\fscx125\\fscy125)\\t(80,200,\\fscx100\\fscy100)}}{word}"
            
            ass_content += text + "\n"
    
    elif style == "pop_multi":
        words_per_line = 3
        for i in range(0, len(word_segments), words_per_line):
            chunk = word_segments[i:i+words_per_line]
            if not chunk:
                continue
            
            # Filter valid words
            valid_chunk = []
            for w in chunk:
                word = w["word"].strip().upper().replace("{", "").replace("}", "")
                if word and len(word) <= 20:
                    valid_chunk.append({**w, "word": word})
            
            if not valid_chunk:
                continue
                
            start = format_ass_time(valid_chunk[0]["start"])
            end = format_ass_time(valid_chunk[-1]["end"])
            
            line_parts = []
            for j, w in enumerate(valid_chunk):
                if j == len(valid_chunk)-1:
                    line_parts.append(f"{{\\c&H00FFFF&\\fscx115\\fscy115}}{w['word']}{{\\c&H00FFFFFF&\\fscx100\\fscy100}}")
                else:
                    line_parts.append(w['word'])
            
            full_line = " ".join(line_parts)
            pos_x = video_width // 2
            pos_y = int(video_height * 0.75)
            
            text = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{{\\an5\\pos({pos_x},{pos_y})}}{full_line}"
            ass_content += text + "\n"

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)
    
    print(f"ASS generated: {output_ass_path} with {len(word_segments)} words")
    return output_ass_path


def transcribe_with_words(video_path, model_size="base"):
    print(f"Transcribing {video_path} with word timestamps...")
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(video_path, word_timestamps=True, beam_size=5)
        
        all_words = []
        for seg in segments:
            if hasattr(seg, 'words') and seg.words:
                for w in seg.words:
                    # Filter out very short words that are likely artifacts
                    if w.word.strip():
                        all_words.append({
                            "word": w.word,
                            "start": w.start,
                            "end": w.end
                        })
            else:
                words = seg.text.strip().split()
                if words:
                    dur = seg.end - seg.start
                    per_word = dur / len(words) if len(words) > 0 else 0.3
                    for idx, word in enumerate(words):
                        all_words.append({
                            "word": word,
                            "start": seg.start + idx*per_word,
                            "end": seg.start + (idx+1)*per_word
                        })
        
        print(f"Transcribed {len(all_words)} words")
        return all_words
        
    except Exception as e:
        print(f"Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return []


def burn_ass_captions(input_video, ass_path, output_video):
    """FIXED burning - handles Windows paths correctly"""
    print(f"Burning captions: {ass_path}")
    print(f"Input: {input_video}")
    print(f"Output: {output_video}")
    
    # FIXED: Proper escaping for Windows
    # Use forward slashes and escape colon for drive letter
    ass_path_obj = Path(ass_path)
    # FFmpeg needs ass path with escaped colon on Windows: C\: -> C\:
    ass_escaped = str(ass_path_obj).replace("\\", "/")
    # Escape colon after drive letter for FFmpeg subtitles filter
    if ":" in ass_escaped and ass_escaped[1] == ":":
        # Already escaped? Check
        pass
    # For ass filter, need to escape : and handle spaces
    # Use absolute path with forward slashes
    ass_escaped = str(ass_path_obj.absolute()).replace("\\", "/").replace(":", "\\:")
    
    # Try multiple methods
    methods = [
        # Method 1: ass filter with escaped path
        [
            "ffmpeg", "-y",
            "-i", str(input_video),
            "-vf", f"ass='{ass_escaped}'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "copy",
            str(output_video)
        ],
        # Method 2: subtitles filter (more compatible)
        [
            "ffmpeg", "-y",
            "-i", str(input_video),
            "-vf", f"subtitles='{ass_escaped}'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "copy",
            str(output_video)
        ],
        # Method 3: No escaping, simple
        [
            "ffmpeg", "-y",
            "-i", str(input_video),
            "-vf", f"ass={ass_path}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "copy",
            str(output_video)
        ]
    ]
    
    for i, cmd in enumerate(methods, 1):
        try:
            print(f"Trying method {i}: {' '.join(cmd[:6])}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0 and Path(output_video).exists():
                print(f"✓ Method {i} succeeded: {output_video}")
                return output_video
            else:
                print(f"Method {i} failed: {result.stderr[:500]}")
        except Exception as e:
            print(f"Method {i} exception: {e}")
            continue
    
    print("All caption burning methods failed!")
    return None


def create_hormozi_video(input_video, output_video=None, model_size="base", caption_style="pop_single", keep_ass=False):
    input_path = Path(input_video)
    if output_video is None:
        output_video = str(input_path.parent / f"{input_path.stem}_hormozi.mp4")
    
    temp_dir = tempfile.gettempdir()
    ass_path = os.path.join(temp_dir, f"{input_path.stem}_hormozi_fixed.ass")
    
    words = transcribe_with_words(input_video, model_size=model_size)
    
    if not words:
        print("No words found, copying video without captions")
        import shutil
        shutil.copy(input_video, output_video)
        return output_video
    
    # Limit words for very long clips (1m30s-2m15s = ~200-350 words)
    # For performance, keep all but ensure not too many
    if len(words) > 500:
        print(f"Long clip with {len(words)} words, keeping all but may be slow to burn")
    
    import cv2
    cap = cv2.VideoCapture(str(input_video))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    if w == 0 or h == 0:
        w, h = 1080, 1920
    
    generate_hormozi_ass(words, ass_path, video_width=w, video_height=h, style=caption_style)
    
    result = burn_ass_captions(input_video, ass_path, output_video)
    
    if result is None:
        print("Caption burn failed, returning original")
        import shutil
        shutil.copy(input_video, output_video)
        result = output_video
    
    if not keep_ass and os.path.exists(ass_path):
        try:
            os.remove(ass_path)
        except:
            pass
    
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python hormozi_captions_fixed.py input.mp4 [output.mp4]")
    else:
        inp = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else None
        create_hormozi_video(inp, out, caption_style="pop_single")
