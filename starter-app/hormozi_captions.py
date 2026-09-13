"""
Hormozi-Style Word-by-Word Captions Generator
Creates that viral pop animation: 1-3 words at a time, bold, centered, current word pops

Style: 
- Montserrat ExtraBold / Impact, all caps, white with thick black stroke
- Centered, slightly above bottom (like 75% height)
- Current word: yellow + scale pop
- Previous words: white

Install: pip install faster-whisper

Usage:
    from hormozi_captions import create_hormozi_video
    create_hormozi_video("input.mp4", "output_captioned.mp4")
"""

import os
import subprocess
import tempfile
from pathlib import Path

def format_ass_time(seconds):
    """Convert seconds to ASS time: H:MM:SS.cc"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)  # centiseconds
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def generate_hormozi_ass(word_segments, output_ass_path, video_width=1080, video_height=1920, style="pop_single"):
    """
    Generate ASS file with Hormozi pop effect
    
    word_segments: list of dicts [{"word": "Hello", "start": 0.1, "end": 0.4}, ...]
    style: "pop_single" = 1 word at a time, "pop_multi" = 3 words with highlight
    """
    
    # ASS Header - Optimized for 1080x1920 vertical, but works for any
    ass_content = f"""[Script Info]
Title: Hormozi Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: {video_width}
PlayResY: {video_height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default, Montserrat ExtraBold, 110, &H00FFFFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 0, 0, 1, 12, 2, 5, 10, 10, 300, 1
Style: Highlight, Montserrat ExtraBold, 120, &H0000FFFF, &H00FFFFFF, &H00000000, &H00000000, -1, 0, 0, 0, 100, 100, 0, 0, 1, 14, 2, 5, 10, 10, 300, 1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # Generate events
    # For Hormozi pop: each word appears with a pop animation
    
    if style == "pop_single":
        # 1 word at a time, centered, big pop
        for w in word_segments:
            word = w["word"].strip().upper()
            if not word:
                continue
            start = format_ass_time(w["start"])
            end = format_ass_time(w["end"])
            
            # Pop animation: scale from 80% to 125% to 100% in first 0.08s
            # {\an5} = center middle, \pos = position, \t = transform
            # Using yellow for emphasis on keywords? We'll make all yellow pop for simplicity, or white
            # Hormozi often: current word is white, but pops. Some versions: keyword yellow
            
            # Decide if this is a keyword to highlight yellow
            keywords = ["NEVER", "SECRET", "STOP", "MISTAKE", "HOW", "WHY", "YOU", "MONEY", "SUCCESS"]
            is_keyword = any(k in word for k in keywords)
            color_tag = r"{\c&H00FFFF&}" if is_keyword else ""  # yellow for keywords
            
            # Position: center, 75% down the screen
            pos_x = video_width // 2
            pos_y = int(video_height * 0.72)
            
            # Pop effect: \fscx and \fscy scale
            text = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{{\\an5\\pos({pos_x},{pos_y})\\fscx80\\fscy80\\t(0,80,\\fscx130\\fscy130)\\t(80,200,\\fscx100\\fscy100)}}{color_tag}{word}"
            ass_content += text + "\n"
    
    elif style == "pop_multi":
        # 3 words at a time, current word highlighted yellow and bigger
        # Group words into phrases
        words_per_line = 3
        for i in range(0, len(word_segments), words_per_line):
            chunk = word_segments[i:i+words_per_line]
            if not chunk:
                continue
            
            start = format_ass_time(chunk[0]["start"])
            end = format_ass_time(chunk[-1]["end"])
            
            # Build line with current word highlighted
            # For simplicity, highlight last word of chunk as it is spoken
            line_parts = []
            for j, w in enumerate(chunk):
                word = w["word"].strip().upper()
                if j == len(chunk)-1:  # last word = current
                    # Yellow + bigger
                    line_parts.append(f"{{\\c&H00FFFF&\\fscx120\\fscy120}}{word}{{\\c&H00FFFFFF&\\fscx100\\fscy100}}")
                else:
                    line_parts.append(word)
            
            full_line = " ".join(line_parts)
            pos_x = video_width // 2
            pos_y = int(video_height * 0.72)
            
            text = f"Dialogue: 0,{start},{end},Default,,0,0,0,,{{\\an5\\pos({pos_x},{pos_y})}}{full_line}"
            ass_content += text + "\n"

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)
    
    print(f"ASS file generated: {output_ass_path} with {len(word_segments)} words")
    return output_ass_path


def transcribe_with_words(video_path, model_size="base"):
    """
    Transcribe with word-level timestamps using faster-whisper
    Returns list of words with start/end
    """
    print(f"Transcribing {video_path} with word timestamps (model={model_size})...")
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        segments, info = model.transcribe(video_path, word_timestamps=True, beam_size=5)
        
        all_words = []
        for seg in segments:
            if hasattr(seg, 'words') and seg.words:
                for w in seg.words:
                    all_words.append({
                        "word": w.word,
                        "start": w.start,
                        "end": w.end
                    })
            else:
                # Fallback: split segment text into words with estimated timing
                # Estimate: divide segment duration by word count
                words = seg.text.strip().split()
                if words:
                    dur = seg.end - seg.start
                    per_word = dur / len(words)
                    for idx, word in enumerate(words):
                        all_words.append({
                            "word": word,
                            "start": seg.start + idx*per_word,
                            "end": seg.start + (idx+1)*per_word
                        })
        
        print(f"Transcribed {len(all_words)} words")
        return all_words
        
    except ImportError:
        raise ImportError("pip install faster-whisper")
    except Exception as e:
        print(f"Transcription error: {e}")
        raise


def burn_ass_captions(input_video, ass_path, output_video):
    """Burn ASS captions into video using FFmpeg"""
    print(f"Burning captions: {ass_path} -> {output_video}")
    
    # Escape path for FFmpeg (handle : and special chars)
    # On Windows, need to escape properly
    ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-vf", f"ass={ass_escaped}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        output_video
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✓ Captioned video: {output_video}")
        return output_video
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg burn failed: {e}")
        # Try alternative with subtitles filter
        cmd2 = [
            "ffmpeg", "-y",
            "-i", input_video,
            "-vf", f"subtitles={ass_escaped}:force_style='FontName=Montserrat ExtraBold,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "copy",
            output_video
        ]
        subprocess.run(cmd2, check=True)
        return output_video


def create_hormozi_video(input_video, output_video=None, model_size="base", caption_style="pop_single", keep_ass=False):
    """
    Full pipeline: video -> word transcription -> ASS with pop -> burned video
    
    input_video: path to clip (should already be short viral clip)
    output_video: path for final captioned video
    """
    input_path = Path(input_video)
    if output_video is None:
        output_video = str(input_path.parent / f"{input_path.stem}_hormozi.mp4")
    
    # Temp ASS file
    temp_dir = tempfile.gettempdir()
    ass_path = os.path.join(temp_dir, f"{input_path.stem}_hormozi.ass")
    
    # 1. Transcribe words
    words = transcribe_with_words(input_video, model_size=model_size)
    
    if not words:
        print("No words found!")
        return None
    
    # 2. Get video resolution for ASS positioning
    import cv2
    cap = cv2.VideoCapture(str(input_video))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    if w == 0 or h == 0:
        w, h = 1080, 1920
    
    # 3. Generate ASS
    generate_hormozi_ass(words, ass_path, video_width=w, video_height=h, style=caption_style)
    
    # 4. Burn
    result = burn_ass_captions(input_video, ass_path, output_video)
    
    if not keep_ass and os.path.exists(ass_path):
        os.remove(ass_path)
    
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python hormozi_captions.py input_clip.mp4 [output.mp4]")
        print("Styles: pop_single (1 word pop), pop_multi (3 words highlight)")
    else:
        inp = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else None
        create_hormozi_video(inp, out, caption_style="pop_single")
