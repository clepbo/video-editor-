"""
Trainable Viral Clip Engine - The Brain
This is how you teach AI your excerpt style.

Install: pip install faster-whisper sentence-transformers scikit-learn librosa
"""
import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict

# --- 1. STYLE LEARNER: Learn from your example clips ---

class StyleLearner:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print(f"Loading embedding model {model_name}... (first time downloads ~80MB)")
        try:
            from sentence_transformers import SentenceTransformer
            self.embed_model = SentenceTransformer(model_name)
        except ImportError:
            print("ERROR: pip install sentence-transformers")
            self.embed_model = None
        
        self.style_profile = None

    def transcribe_clip(self, video_path: str) -> str:
        """Transcribe a single example clip to text"""
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
        """
        Feed it 5-20 clips you LOVE.
        It will create your style profile.
        """
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
            print("No embeddings created. Check your videos.")
            return None

        # Average embedding = your style vector
        style_vector = np.mean(embeddings, axis=0)
        
        # Calculate stats
        avg_length = np.mean([len(t.split()) for t in texts]) # avg words
        
        # Hook analysis
        hook_keywords = ["how", "why", "stop", "never", "secret", "mistake", "reason", "?", "you"]
        hook_count = sum(1 for t in texts if any(k in t.lower() for k in hook_keywords))
        
        self.style_profile = {
            "style_vector": style_vector.tolist(),
            "example_texts": texts,
            "stats": {
                "avg_words": float(avg_length),
                "avg_duration_estimate": float(avg_length / 2.5), # ~2.5 words/sec
                "hook_rate": hook_count / len(texts) if texts else 0,
                "num_examples": len(texts)
            }
        }
        
        # Save
        with open(save_path, "w") as f:
            json.dump(self.style_profile, f, indent=2)
        
        print(f"\nSTYLE PROFILE SAVED to {save_path}")
        print(f"Your style: Avg {avg_length:.0f} words (~{avg_length/2.5:.0f}s), Hook rate: {hook_count/len(texts)*100:.0f}%")
        return self.style_profile

    def load_profile(self, path="my_style_profile.json"):
        with open(path, "r") as f:
            self.style_profile = json.load(f)
        return self.style_profile


# --- 2. VIRAL SCORER: Score new candidates against your style ---

class ViralScorer:
    def __init__(self, style_profile_path="my_style_profile.json"):
        from sentence_transformers import SentenceTransformer
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        with open(style_profile_path, "r") as f:
            profile = json.load(f)
        self.style_vector = np.array(profile["style_vector"])
        self.style_stats = profile["stats"]
        
        # Hook patterns that are generally viral
        self.viral_hooks = [
            "how to", "how i", "why you", "stop doing", "never", "secret", 
            "mistake", "the reason", "this is why", "if you", "you need to",
            "?", "you're doing it wrong", "truth about"
        ]

    def score_candidate(self, candidate_text: str, audio_energy: float = 0.5, has_face: bool = True) -> Dict:
        """
        Score a single candidate clip (15-60s chunk from long video)
        Returns score 0-100
        """
        if not candidate_text or len(candidate_text.split()) < 5:
            return {"score": 0, "reason": "too short"}

        # 1. Style Similarity (60% weight) - How close to YOUR examples?
        candidate_emb = self.embed_model.encode(candidate_text)
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity([candidate_emb], [self.style_vector])[0][0] # 0 to 1
        
        # 2. Hook Score (25% weight) - Does it start strong?
        text_lower = candidate_text.lower()
        hook_score = 0
        for hook in self.viral_hooks:
            if hook in text_lower:
                hook_score += 1
        hook_score = min(hook_score / 2, 1.0) # normalize 0-1
        
        # Bonus if first 10 words contain hook
        first_words = " ".join(text_lower.split()[:10])
        if any(h in first_words for h in self.viral_hooks):
            hook_score += 0.3

        # 3. Length Score (5% weight) - Close to your avg length?
        word_count = len(candidate_text.split())
        ideal = self.style_stats["avg_words"]
        length_diff = abs(word_count - ideal) / ideal
        length_score = max(0, 1 - length_diff) # 1 if perfect length

        # 4. Audio/Visual (10% weight) - Placeholder, you can add librosa + YOLO later
        av_score = 0.5
        if has_face:
            av_score += 0.3
        av_score = min(av_score + audio_energy*0.2, 1.0)

        # Final weighted score
        final_score = (similarity * 0.6 + hook_score * 0.25 + length_score * 0.05 + av_score * 0.1) * 100

        return {
            "score": round(final_score, 1),
            "similarity": round(similarity*100, 1),
            "hook_score": round(hook_score*100, 1),
            "text": candidate_text,
            "word_count": word_count
        }


# --- 3. FULL PIPELINE: Long Video -> Candidates -> Top Clips ---

def process_long_video(long_video_path: str, style_profile="my_style_profile.json", top_n=5):
    """
    Main function you will call:
    1. Transcribe long video with timestamps
    2. Create candidates
    3. Score them
    4. Return top N
    """
    print(f"\nProcessing long video: {long_video_path}")
    
    # Step 1: Transcribe with timestamps
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(long_video_path, beam_size=5)
    
    # Convert to list with start/end
    timed_segments = [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments]
    
    # Step 2: Create candidates - sliding window 15-60s
    # Simple version: group segments into 20-40 second chunks
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
        # If chunk is 20-45 seconds, make it a candidate
        if 20 <= chunk_duration <= 45:
            candidates.append({
                "start": chunk_start,
                "end": seg["end"],
                "text": current_text.strip(),
                "duration": chunk_duration
            })
            # Start new chunk with 30% overlap for better coverage
            overlap_idx = len(current_chunk) // 3
            current_chunk = current_chunk[overlap_idx:]
            if current_chunk:
                current_text = " ".join([s["text"] for s in current_chunk])
                chunk_start = current_chunk[0]["start"]
            else:
                current_text = ""
    
    print(f"Created {len(candidates)} candidate clips")
    
    # Step 3: Score them
    scorer = ViralScorer(style_profile)
    scored = []
    for cand in candidates:
        score_data = scorer.score_candidate(cand["text"])
        scored.append({**cand, **score_data})
    
    # Sort by score
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    # Step 4: Pick top N non-overlapping
    top_clips = []
    for cand in scored:
        # Check overlap with already picked
        overlap = any(not (cand["end"] < picked["start"] or cand["start"] > picked["end"]) for picked in top_clips)
        if not overlap:
            top_clips.append(cand)
        if len(top_clips) >= top_n:
            break
    
    print(f"\nTOP {len(top_clips)} VIRAL CLIPS (based on YOUR style):")
    for i, clip in enumerate(top_clips, 1):
        print(f"{i}. Score {clip['score']} | {clip['start']:.1f}s-{clip['end']:.1f}s | {clip['text'][:80]}...")
    
    return top_clips


# --- Example Usage ---
if __name__ == "__main__":
    # 1. First time: Teach it your style
    # examples = ["my_best_clip1.mp4", "my_best_clip2.mp4", "my_best_clip3.mp4"]
    # learner = StyleLearner()
    # learner.learn_from_examples(examples)
    
    # 2. Then: Generate viral clips from long video
    # clips = process_long_video("my_long_podcast.mp4", top_n=5)
    
    print("Engine ready. See blueprint for usage.")
