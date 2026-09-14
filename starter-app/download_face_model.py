"""
Auto-download yolov8n-face.pt (6MB) for better face tracking
Run: python starter-app/download_face_model.py

This will download the face-specific YOLO model that tracks faces (not just persons)
Much more accurate for 9:16 vertical reframe.

If download fails, app will still work with generic person detection.
"""

import os
import sys
from pathlib import Path

# URLs for yolov8n-face.pt - try multiple mirrors
MODEL_URLS = [
    "https://github.com/derronqi/yolov8-face/releases/download/v1.0/yolov8n-face.pt",
    "https://huggingface.co/derronqi/yolov8-face/resolve/main/yolov8n-face.pt",
]

def download_file(url, dest_path):
    """Download with progress bar"""
    try:
        import requests
        from tqdm import tqdm
        
        print(f"Downloading from {url}...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(dest_path, 'wb') as f, tqdm(
            desc=Path(dest_path).name,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
        
        print(f"✓ Downloaded to {dest_path}")
        return True
        
    except ImportError:
        # Fallback without tqdm/requests - use urllib
        print("requests/tqdm not found, using urllib...")
        try:
            import urllib.request
            urllib.request.urlretrieve(url, dest_path)
            print(f"✓ Downloaded to {dest_path}")
            return True
        except Exception as e:
            print(f"Failed with urllib: {e}")
            return False
    except Exception as e:
        print(f"Download failed from {url}: {e}")
        return False

def main():
    # Determine where to save - same folder as this script and also project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Try to save in multiple places for compatibility
    possible_dests = [
        script_dir / "yolov8n-face.pt",
        project_root / "yolov8n-face.pt",
        Path.cwd() / "yolov8n-face.pt",
    ]
    
    # Use first dest as primary
    dest = possible_dests[0]
    
    if dest.exists():
        size_mb = dest.stat().st_size / 1024 / 1024
        print(f"✓ Model already exists: {dest} ({size_mb:.1f} MB)")
        print("You are good to go! Face tracking will use face model.")
        return
    
    print("Downloading yolov8n-face.pt (6MB) for better face tracking...")
    print("This model detects faces specifically, not just persons.")
    print("")
    
    # Try each URL
    for url in MODEL_URLS:
        if download_file(url, dest):
            # Also copy to other locations
            try:
                import shutil
                for other_dest in possible_dests[1:]:
                    if not other_dest.exists():
                        shutil.copy(dest, other_dest)
                        print(f"  Also copied to {other_dest}")
            except:
                pass
            
            print("")
            print("="*60)
            print("SUCCESS! Face model installed.")
            print(f"Location: {dest}")
            print("Your 9:16 reframe will now track FACES (more accurate)")
            print("="*60)
            return
    
    print("")
    print("="*60)
    print("All download attempts failed.")
    print("")
    print("Manual download options:")
    print("1. Go to: https://github.com/derronqi/yolov8-face")
    print("   -> Releases -> Download yolov8n-face.pt")
    print("2. Or: https://huggingface.co/derronqi/yolov8-face")
    print("3. Place the file in:")
    for d in possible_dests:
        print(f"   - {d}")
    print("")
    print("App will still work without it (uses person detection fallback)")
    print("="*60)

if __name__ == "__main__":
    main()
