"""
Face-Tracking Reframe Engine - 9:16 that follows you
Uses YOLOv8 to track face and smoothly crops to vertical

Install: pip install ultralytics opencv-python
Download model: YOLO will auto-download yolov8n.pt first time
For better face detection: download yolov8n-face.pt from https://github.com/derronqi/yolov8-face

Usage:
    from face_tracker_reframe import reframe_with_face_tracking
    reframe_with_face_tracking("input_clip.mp4", "output_9x16.mp4", target_ratio=9/16)
"""
import cv2
import numpy as np
import subprocess
import os
from pathlib import Path
import tempfile

class FaceTrackerReframer:
    def __init__(self, use_face_model=True):
        self.model = None
        self.use_face_model = use_face_model
        self._load_model()
        
    def _load_model(self):
        try:
            from ultralytics import YOLO
            # Try face-specific model first, fallback to generic
            face_model_path = "yolov8n-face.pt"
            if os.path.exists(face_model_path):
                print(f"Loading face model: {face_model_path}")
                self.model = YOLO(face_model_path)
            else:
                print("Loading YOLOv8n (generic person detection) - will detect person as fallback")
                print("For better face tracking, download yolov8n-face.pt")
                self.model = YOLO("yolov8n.pt")  # auto-downloads
            print("YOLO model loaded")
        except Exception as e:
            print(f"YOLO not available ({e}), falling back to Haar Cascade")
            self.model = None
            # Fallback to OpenCV Haar
            self.haar = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect_face_center(self, frame):
        """Returns x center of main face/person, or None"""
        h, w = frame.shape[:2]
        
        if self.model:
            try:
                results = self.model(frame, verbose=False, conf=0.4)
                boxes = []
                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0]) if hasattr(box, 'cls') else 0
                        # If using generic model, class 0 = person
                        # If face model, all detections are faces
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0])
                        # Prefer larger boxes (closer person) and higher confidence
                        area = (x2-x1)*(y2-y1)
                        boxes.append((x1, y1, x2, y2, conf, area))
                
                if boxes:
                    # Pick biggest + most confident
                    boxes.sort(key=lambda b: b[5]*b[4], reverse=True)
                    x1, y1, x2, y2, _, _ = boxes[0]
                    center_x = (x1 + x2) / 2
                    return center_x
            except Exception as e:
                print(f"YOLO detection error: {e}")
        
        # Fallback Haar
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.haar.detectMultiScale(gray, 1.1, 4)
            if len(faces) > 0:
                # Biggest face
                faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                x, y, fw, fh = faces[0]
                return x + fw/2
        except:
            pass
            
        return None

    def reframe_video(self, input_path, output_path, target_ratio=9/16, smoothing=0.85, detect_every_n_frames=6):
        """
        Main function: Reframes video to follow face
        
        target_ratio: 9/16 for vertical, 1 for square
        smoothing: 0.0 = no smoothing (jittery), 1.0 = very smooth but laggy. 0.85 recommended
        detect_every_n_frames: Detect every N frames for speed (6 = every 0.2s at 30fps)
        """
        input_path = str(input_path)
        output_path = str(output_path)
        
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open {input_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Input: {width}x{height} @ {fps}fps, {total_frames} frames")
        
        # Calculate crop dimensions
        # For 9:16 vertical: keep full height, crop width = height * 9/16
        if target_ratio < 1:  # vertical
            crop_h = height
            crop_w = int(crop_h * target_ratio)
        else:  # square or horizontal
            crop_w = int(height * target_ratio) if target_ratio <= 1 else width
            crop_h = int(crop_w / target_ratio) if target_ratio > 0 else height
            crop_h = min(crop_h, height)
        
        crop_w = min(crop_w, width)
        crop_h = min(crop_h, height)
        
        print(f"Crop size: {crop_w}x{crop_h} (target ratio {target_ratio})")
        
        # Temporary silent video path
        temp_dir = tempfile.gettempdir()
        temp_silent = os.path.join(temp_dir, "temp_cropped_silent.mp4")
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_silent, fourcc, fps, (crop_w, crop_h))
        
        # Tracking state
        last_face_x = width / 2  # start centered
        smoothed_x = width / 2
        face_positions = {}  # frame_idx -> face_x
        
        # First pass: detect faces every N frames
        print("Pass 1: Detecting faces...")
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % detect_every_n_frames == 0:
                face_x = self.detect_face_center(frame)
                if face_x is not None:
                    last_face_x = face_x
                face_positions[frame_idx] = last_face_x
            
            frame_idx += 1
            if frame_idx % 100 == 0:
                print(f"  Detected {frame_idx}/{total_frames}")
        
        cap.release()
        
        # Interpolate missing frames
        print("Interpolating tracking path...")
        all_face_x = []
        last_known = width/2
        for i in range(total_frames):
            if i in face_positions:
                last_known = face_positions[i]
            all_face_x.append(last_known)
        
        # Smooth the path with EMA
        smoothed_path = []
        curr = all_face_x[0] if all_face_x else width/2
        for x in all_face_x:
            curr = smoothing * curr + (1 - smoothing) * x
            smoothed_path.append(curr)
        
        # Second pass: actually crop and write
        print("Pass 2: Rendering cropped video...")
        cap = cv2.VideoCapture(input_path)
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            target_center_x = smoothed_path[frame_idx] if frame_idx < len(smoothed_path) else width/2
            
            # Calculate crop x (left edge)
            crop_x = int(target_center_x - crop_w / 2)
            # Clamp
            crop_x = max(0, min(crop_x, width - crop_w))
            crop_y = 0  # keep top aligned, or center: (height - crop_h)//2
            if crop_h < height:
                crop_y = (height - crop_h) // 2  # center vertically
            
            cropped = frame[crop_y:crop_y+crop_h, crop_x:crop_x+crop_w]
            
            # Resize if needed (should already be correct size)
            if cropped.shape[1] != crop_w or cropped.shape[0] != crop_h:
                cropped = cv2.resize(cropped, (crop_w, crop_h))
            
            out.write(cropped)
            frame_idx += 1
            
            if frame_idx % 100 == 0:
                print(f"  Rendered {frame_idx}/{total_frames}")
        
        cap.release()
        out.release()
        print(f"Silent cropped video saved to {temp_silent}")
        
        # Now mux audio from original
        print("Muxing audio...")
        # Extract audio existence check
        # Use ffmpeg to combine silent video + original audio
        cmd = [
            "ffmpeg", "-y",
            "-i", temp_silent,
            "-i", input_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0", "-map", "1:a:0?",
            "-shortest",
            output_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✓ Final video with audio: {output_path}")
            # Cleanup
            if os.path.exists(temp_silent):
                os.remove(temp_silent)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg mux failed, returning silent video: {e}")
            # Fallback: just rename silent to output (no audio)
            import shutil
            shutil.copy(temp_silent, output_path)
            return output_path


def reframe_with_face_tracking(input_path, output_path, target_ratio=9/16):
    """Convenience function"""
    reframer = FaceTrackerReframer()
    return reframer.reframe_video(input_path, output_path, target_ratio=target_ratio)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python face_tracker_reframe.py input.mp4 output_9x16.mp4")
    else:
        reframe_with_face_tracking(sys.argv[1], sys.argv[2])
