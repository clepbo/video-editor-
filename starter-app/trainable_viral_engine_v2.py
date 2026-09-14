"""
Trainable Viral Engine V2 - Fixed for longer clips (1m30s - 2m15s) + improved scoring
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict

class StyleLearner:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print(f"Loading embedding model {model_name}...")
        try:
            from sentence_transformers import SentenceTransformer
            self.embed_model = SentenceTransformer(model_name)
        except ImportError:
            print("ERROR: pip install sentence-transformers")
            self.embed_model = None
        self.style_profile = None

    def transcribe_clip(self, video_path: str) -> str:
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(video_path)
            full_text = " ".join([s.text for s in segments])
            return full_text.strip()
        except Exception as e:
            print(f"Transcription failed for {video_path}: {e}")
            return ""

    def learn_from_examples(self, example_video_paths: List[str], save_path="my_style_profile.json"):
        print(f"Learning from {len(example_video_paths)} example clips...")
        texts = []
        embeddings = []
        for path in example_video_paths:
            text = self.transcribe_clip(path)
            if text:
                texts.append(text)
                if self.embed_model:
                    emb = self.embed_model.encode(text)
                    embeddings.append(emb)
                print(f"  Learned: {Path(path).name} -> {text[:60]}...")

        if not embeddings:
            print("No embeddings created.")
            return None

        style_vector = np.mean(embeddings, axis=0)
        avg_length = np.mean([len(t.split()) for t in texts])
        
        hook_keywords = ["how", "why", "stop", "never", "secret", "mistake", "reason", "?", "you"]
        hook_count = sum(1 for t in texts if any(k in t.lower() for k in hook_keywords))
        
        self.style_profile = {
            "style_vector": style_vector.tolist(),
            "example_texts": texts,
            "stats": {
                "avg_words": float(avg_length),
                "avg_duration_estimate": float(avg_length / 2.5),
                "hook_rate": hook_count / len(texts) if texts else 0,
                "num_examples": len(texts)
            }
        }
        
        with open(save_path, "w") as f:
            json.dump(self.style_profile, f, indent=2)
        
        print(f"\nSTYLE PROFILE SAVED to {save_path}")
        print(f"Your style: Avg {avg_length:.0f} words (~{avg_length/2.5:.0f}s)")
        return self.style_profile

    def load_profile(self, path="my_style_profile.json"):
        with open(path, "r") as f:
            self.style_profile = json.load(f)
        return self.style_profile


class ViralScorer:
    def __init__(self, style_profile_path="my_style_profile.json"):
        from sentence_transformers import SentenceTransformer
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        with open(style_profile_path, "r") as f:
            profile = json.load(f)
        self.style_vector = np.array(profile["style_vector"])
        self.style_stats = profile["stats"]
        self.viral_hooks = [
            "how to", "how i", "why you", "stop doing", "never", "secret", 
            "mistake", "the reason", "this is why", "if you", "you need to",
            "?", "you're doing it wrong", "truth about"
        ]

    def score_candidate(self, candidate_text: str, audio_energy: float = 0.5, has_face: bool = True) -> Dict:
        if not candidate_text or len(candidate_text.split()) < 10:
            return {"score": 0, "reason": "too short"}

        candidate_emb = self.embed_model.encode(candidate_text)
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity([candidate_emb], [self.style_vector])[0][0]
        
        text_lower = candidate_text.lower()
        hook_score = 0
        for hook in self.viral_hooks:
            if hook in text_lower:
                hook_score += 1
        hook_score = min(hook_score / 2, 1.0)
        first_words = " ".join(text_lower.split()[:15])
        if any(h in first_words for h in self.viral_hooks):
            hook_score += 0.3

        word_count = len(candidate_text.split())
        ideal = self.style_stats["avg_words"]
        length_diff = abs(word_count - ideal) / max(ideal, 1)
        length_score = max(0, 1 - length_diff*0.5)

        av_score = 0.5
        if has_face:
            av_score += 0.3
        av_score = min(av_score + audio_energy*0.2, 1.0)

        final_score = (similarity * 0.6 + hook_score * 0.25 + length_score * 0.05 + av_score * 0.1) * 100

        return {
            "score": round(final_score, 1),
            "similarity": round(similarity*100, 1),
            "hook_score": round(hook_score*100, 1),
            "text": candidate_text,
            "word_count": word_count
        }


def process_long_video(long_video_path: str, style_profile="my_style_profile.json", top_n=5, min_duration=90, max_duration=135):
    """
    V2 - Supports longer clips: 90-135 seconds (1m30s - 2m15s)
    min_duration, max_duration in seconds
    """
    print(f"\nProcessing long video: {long_video_path}")
    print(f"Target clip length: {min_duration}s - {max_duration}s ({min_duration/60:.1f}m - {max_duration/60:.1f}m)")
    
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(long_video_path, beam_size=5)
    
    timed_segments = [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments]
    
    if not timed_segments:
        print("No transcription found!")
        return []
    
    # Create candidates with NEW longer duration logic
    candidates = []
    current_chunk = []
    current_text = ""
    chunk_start = 0
    
    for seg in timed_segments:
        if not current_chunk:
            chunk_start = seg["start"]
        current_chunk.append(seg)
        current_text += " " + seg["text"]
        
        chunk_duration = seg["end"] - chunk_start
        
        # V2: Target 90-135 seconds (1m30s - 2m15s)
        if min_duration <= chunk_duration <= max_duration:
            candidates.append({
                "start": chunk_start,
                "end": seg["end"],
                "text": current_text.strip(),
                "duration": chunk_duration
            })
            # Overlap 20% for better coverage
            overlap_idx = len(current_chunk) // 5
            current_chunk = current_chunk[overlap_idx:]
            if current_chunk:
                current_text = " ".join([s["text"] for s in current_chunk])
                chunk_start = current_chunk[0]["start"]
            else:
                current_text = ""
        elif chunk_duration > max_duration:
            # If too long, force cut and start new
            candidates.append({
                "start": chunk_start,
                "end": seg["end"],
                "text": current_text.strip(),
                "duration": chunk_duration
            })
            current_chunk = []
            current_text = ""
    
    print(f"Created {len(candidates)} candidate clips ({min_duration}-{max_duration}s each)")
    
    if not candidates:
        # Fallback: if no candidates in desired range, create them with fixed window
        print(f"No candidates in {min_duration}-{max_duration}s range, using sliding window fallback...")
        total_duration = timed_segments[-1]["end"] if timed_segments else 0
        window_size = (min_duration + max_duration) / 2  # e.g., 112.5s
        step = window_size * 0.7  # 30% overlap
        
        current_start = 0
        while current_start + min_duration <= total_duration:
            # Find segments in this window
            window_end = current_start + window_size
            window_text = ""
            window_segments = []
            for seg in timed_segments:
                if seg["start"] >= current_start and seg["end"] <= window_end:
                    window_text += " " + seg["text"]
                    window_segments.append(seg)
            
            if window_text.strip():
                candidates.append({
                    "start": current_start,
                    "end": window_end,
                    "text": window_text.strip(),
                    "duration": window_size
                })
            
            current_start += step
    
    # Score them
    scorer = ViralScorer(style_profile)
    scored = []
    for cand in candidates:
        score_data = scorer.score_candidate(cand["text"])
        scored.append({**cand, **score_data})
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    # Pick top N non-overlapping
    top_clips = []
    for cand in scored:
        overlap = any(not (cand["end"] < picked["start"] or cand["start"] > picked["end"]) for picked in top_clips)
        if not overlap:
            top_clips.append(cand)
        if len(top_clips) >= top_n:
            break
    
    print(f"\nTOP {len(top_clips)} VIRAL CLIPS ({min_duration}-{max_duration}s):")
    for i, clip in enumerate(top_clips, 1):
        print(f"{i}. Score {clip['score']} | {clip['start']:.1f}s-{clip['end']:.1f}s ({clip['duration']:.0f}s) | {clip['text'][:80]}...")
    
    return top_clips
