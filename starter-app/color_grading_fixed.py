"""
Color Grading FIXED - Now actually works and is visible
"""

import subprocess
from pathlib import Path

def apply_color_grading(input_video, output_video, style="vibrant"):
    """
    Apply color grading that is actually visible
    
    Styles:
    - vibrant: YouTube pop (contrast + saturation)
    - warm: Podcast warm tone
    - cinematic: Movie look (teal & orange-ish)
    - cold: Cool tone
    - custom LUT: path to .cube file
    """
    
    print(f"Applying color grading: {style}")
    print(f"Input: {input_video}")
    
    # Define visible filters - stronger than before
    filters = {
        "vibrant": "eq=contrast=1.15:brightness=0.03:saturation=1.35:gamma=1.05,unsharp=5:5:0.8:3:3:0.4",
        "warm": "eq=contrast=1.08:brightness=0.04:saturation=1.2,colorbalance=rs=0.08:gs=-0.02:bs=-0.12:rm=0.05:gm=0.02:bm=-0.05",
        "cinematic": "eq=contrast=1.18:brightness=-0.03:saturation=0.92:gamma=1.1,colorbalance=rs=-0.05:gs=0.02:bs=0.08:rm=0.08:gm=0.03:bm=0.12,curves=preset=darker",
        "cold": "eq=contrast=1.1:brightness=0.02:saturation=1.1,colorbalance=rs=-0.08:gs=0.02:bs=0.12",
        "original": "null",
        "youtube": "eq=contrast=1.12:brightness=0.02:saturation=1.25,unsharp=5:5:0.7:3:3:0.3",
        "podcast": "eq=contrast=1.06:brightness=0.05:saturation=1.15,colorbalance=rs=0.06:bs=-0.08",
    }
    
    if style.endswith(".cube"):
        # Custom LUT
        lut_path = Path(style)
        if not lut_path.exists():
            print(f"LUT not found: {style}, using vibrant")
            vf = filters["vibrant"]
        else:
            # Escape LUT path
            lut_escaped = str(lut_path).replace("\\", "/").replace(":", "\\:")
            vf = f"lut3d='{lut_escaped}'"
    else:
        vf = filters.get(style.lower(), filters["vibrant"])
    
    if vf == "null":
        print("Original (no grading) - copying")
        import shutil
        shutil.copy(input_video, output_video)
        return output_video
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_video),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        str(output_video)
    ]
    
    print(f"FFmpeg filter: {vf}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✓ Color graded: {output_video}")
            return output_video
        else:
            print(f"Color grading failed: {result.stderr[:1000]}")
            # Fallback copy
            import shutil
            shutil.copy(input_video, output_video)
            return output_video
    except Exception as e:
        print(f"Exception in color grading: {e}")
        import shutil
        shutil.copy(input_video, output_video)
        return output_video


def apply_color_grading_with_preview(input_video, output_video, style="vibrant"):
    """
    Apply grading + create side-by-side preview for comparison
    """
    import tempfile
    import os
    
    # First grade
    temp_graded = str(Path(output_video).parent / f"temp_graded_{Path(output_video).name}")
    graded = apply_color_grading(input_video, temp_graded, style)
    
    # Create preview: original | graded side by side (first 5 seconds)
    preview_path = str(Path(output_video).parent / f"preview_{style}_{Path(input_video).stem}.mp4")
    
    try:
        # Take first 5 seconds of both and stack horizontally
        cmd_preview = [
            "ffmpeg", "-y",
            "-ss", "2", "-t", "5",
            "-i", str(input_video),
            "-ss", "2", "-t", "5",
            "-i", graded,
            "-filter_complex", "[0:v]scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2[orig];[1:v]scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2[graded];[orig][graded]hstack=inputs=2",
            "-c:v", "libx264", "-preset", "fast",
            "-an",
            preview_path
        ]
        subprocess.run(cmd_preview, capture_output=True, timeout=60)
        print(f"Preview (original | graded): {preview_path}")
    except:
        pass
    
    # Move graded to final output
    import shutil
    if Path(temp_graded).exists():
        shutil.move(temp_graded, output_video)
    
    return output_video


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python color_grading_fixed.py input.mp4 vibrant|warm|cinematic|original")
        print("Example: python color_grading_fixed.py input.mp4 vibrant")
    else:
        apply_color_grading(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "output_graded.mp4", sys.argv[2] if len(sys.argv) > 2 else "vibrant")
