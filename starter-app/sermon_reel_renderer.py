"""
Sermon Reel Renderer - Renders meaningful non-sequential reels
Takes composed reel (multiple non-sequential segments) and renders into one coherent video

Handles:
- Cutting multiple segments from different parts
- Concatenating in logical order (Hook->Illustration->Action) even if non-sequential in original
- Adding smooth transitions
- Captions + Color grading
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import List, Dict
import json

def render_sermon_reel(source_video: str, reel: Dict, output_path: str, 
                       use_face_tracking=True, use_captions=True, color_style="warm",
                       add_transitions=True) -> str:
    """
    Render a meaningful sermon reel composed of non-sequential segments
    
    reel: {
        "theme": "Faith",
        "sentences": [  # In logical order Hook->Illustration->Action
            {"start": 600, "end": 625, "text": "Have you ever wondered..."},
            {"start": 1530, "end": 1580, "text": "Let me tell you a story..."},
            {"start": 3000, "end": 3030, "text": "So today I want you to..."},
        ],
        "total_duration": 105,
        "combined_text": "Have you ever... Let me tell you..."
    }
    
    Process:
    1. Cut each sentence segment from source
    2. Concat in logical order (even if non-sequential)
    3. Apply face-tracking, color, captions
    """
    
    source_video = Path(source_video)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\nRendering sermon reel: {reel['theme']}")
    print(f"  Segments: {len(reel['sentences'])} (non-sequential: {reel.get('is_non_sequential', False)})")
    print(f"  Total duration: {reel['total_duration']:.0f}s")
    print(f"  Structure: Hook({len(reel.get('hook', []))}) -> Ill({len(reel.get('illustration', []))}) -> Action({len(reel.get('action', []))})")
    
    temp_dir = Path(tempfile.gettempdir()) / f"sermon_reel_{output_path.stem}"
    temp_dir.mkdir(exist_ok=True)
    
    # Step 1: Cut each segment
    segment_files = []
    for idx, sent in enumerate(reel["sentences"]):
        seg_file = temp_dir / f"seg_{idx:02d}_{sent['start']:.0f}_{sent['end']:.0f}.mp4"
        
        # Add small padding (0.2s) to avoid cutting words
        start = max(0, sent["start"] - 0.15)
        duration = (sent["end"] - sent["start"]) + 0.3
        
        cmd_cut = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", str(source_video),
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k",
            str(seg_file)
        ]
        
        try:
            subprocess.run(cmd_cut, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            segment_files.append(seg_file)
            print(f"  Cut segment {idx+1}/{len(reel['sentences'])}: {sent['start']:.1f}s-{sent['end']:.1f}s ({sent['text'][:40]}...)")
        except Exception as e:
            print(f"  Failed to cut segment {idx}: {e}")
            continue
    
    if not segment_files:
        print("No segments cut!")
        return None
    
    # Step 2: Create concat file for FFmpeg
    concat_file = temp_dir / "concat_list.txt"
    with open(concat_file, "w") as f:
        for seg_file in segment_files:
            # Escape path for concat demuxer
            f.write(f"file '{seg_file.absolute()}'\n")
    
    # Step 3: Concat segments in logical order (Hook->Ill->Action)
    concatenated = temp_dir / "concatenated.mp4"
    
    # Use concat demuxer with transitions if requested
    if add_transitions and len(segment_files) > 1:
        # For transitions, we need to use filter_complex with xfade
        # For simplicity, use simple concat for now, but add small crossfade via filter if possible
        # Simple concat:
        cmd_concat = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(concatenated)
        ]
    else:
        cmd_concat = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(concatenated)
        ]
    
    try:
        subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  Concatenated {len(segment_files)} segments -> {concatenated}")
    except Exception as e:
        print(f"Concat failed: {e}, trying re-encode concat")
        # Fallback: re-encode concat
        cmd_concat_reencode = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac",
            str(concatenated)
        ]
        subprocess.run(cmd_concat_reencode, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    current_path = concatenated
    
    # Step 4: Apply color grading (warm is good for sermons)
    if color_style and color_style != "original":
        try:
            from color_grading_fixed import apply_color_grading
            graded = temp_dir / "graded.mp4"
            apply_color_grading(str(current_path), str(graded), style=color_style)
            if graded.exists():
                current_path = graded
                print(f"  Applied color grading: {color_style}")
        except Exception as e:
            print(f"  Color grading failed: {e}")
    
    # Step 5: Face-tracking reframe to 9:16 (for reels)
    if use_face_tracking:
        try:
            from face_tracker_reframe import reframe_with_face_tracking
            reframed = temp_dir / "reframed.mp4"
            reframe_with_face_tracking(str(current_path), str(reframed), target_ratio=9/16)
            if reframed.exists():
                current_path = reframed
                print(f"  Applied face-tracking reframe 9:16")
        except Exception as e:
            print(f"  Face tracking failed: {e}, using center crop")
            cropped = temp_dir / "cropped.mp4"
            cmd_crop = ["ffmpeg", "-y", "-i", str(current_path), "-vf", "crop=ih*9/16:ih", "-c:a", "copy", str(cropped)]
            try:
                subprocess.run(cmd_crop, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                current_path = cropped
            except:
                pass
    
    # Step 6: Captions - FIXED (must be last)
    if use_captions:
        try:
            from hormozi_captions_fixed import create_hormozi_video
            # For sermons, use pop_multi (3 words) which is more readable for longer messages
            result = create_hormozi_video(str(current_path), str(output_path), caption_style="pop_multi")
            if result and Path(result).exists():
                print(f"  Applied Hormozi captions")
                current_path = Path(result)
            else:
                # Copy without captions
                import shutil
                shutil.copy(str(current_path), str(output_path))
                current_path = output_path
        except Exception as e:
            print(f"  Captions failed: {e}")
            import shutil
            shutil.copy(str(current_path), str(output_path))
            current_path = output_path
    else:
        import shutil
        shutil.copy(str(current_path), str(output_path))
        current_path = output_path
    
    # Cleanup temp
    try:
        import shutil
        shutil.rmtree(temp_dir)
    except:
        pass
    
    print(f"✓ Final sermon reel: {output_path} ({reel['total_duration']:.0f}s, theme: {reel['theme']})")
    return str(output_path)


def render_all_sermon_reels(source_video: str, reels: List[Dict], output_folder: str, **kwargs) -> List[str]:
    """Render all composed reels"""
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    source_name = Path(source_video).stem
    rendered = []
    
    for idx, reel in enumerate(reels, 1):
        output_path = output_folder / f"{source_name}_sermon_reel_{idx:02d}_{reel['theme'][:20].replace(' ', '_')}_{reel['total_duration']:.0f}s_FINAL.mp4"
        
        try:
            result = render_sermon_reel(source_video, reel, str(output_path), **kwargs)
            if result:
                rendered.append(result)
        except Exception as e:
            print(f"Failed to render reel {idx}: {e}")
            import traceback
            traceback.print_exc()
    
    # Save summary JSON
    summary_path = output_folder / f"{source_name}_reels_summary.json"
    summary_data = []
    for reel, path in zip(reels, rendered):
        summary_data.append({
            "theme": reel["theme"],
            "duration": reel["total_duration"],
            "meaningfulness": reel["meaningfulness_score"],
            "is_non_sequential": reel["is_non_sequential"],
            "hook": reel["hook"][0]["text"] if reel["hook"] else "",
            "illustration": reel["illustration"][0]["text"] if reel["illustration"] else "",
            "action": reel["action"][0]["text"] if reel["action"] else "",
            "combined_text": reel["combined_text"],
            "file": path,
            "segments": [{"start": s["start"], "end": s["end"], "text": s["text"], "role": s["dominant_role"]} for s in reel["sentences"]]
        })
    
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nRendered {len(rendered)}/{len(reels)} sermon reels to {output_folder}")
    print(f"Summary: {summary_path}")
    
    return rendered


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python sermon_reel_renderer.py long_sermon.mp4")
        print("This will compose and render meaningful reels")
    else:
        from sermon_reel_composer import compose_sermon_reels
        
        video = sys.argv[1]
        reels = compose_sermon_reels(video, num_reels=5, target_duration=105)
        
        if reels:
            output_folder = Path(video).parent / f"{Path(video).stem}_sermon_reels"
            render_all_sermon_reels(video, reels, str(output_folder), use_face_tracking=True, use_captions=True, color_style="warm")
