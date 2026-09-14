"""
Sermon Reel Composer - Creates MEANINGFUL message reels, not just cuts
For church services: Non-sequential, complete sentences, Hook->Illustration->Action

This is different from viral clip extractor:
- Old: Cut continuous 90s section
- New: Compose meaningful message from different parts that buttress same point

Example: Preacher makes point about "Faith" at 10:00, illustrates at 25:30, gives action at 50:00
-> Compose reel: Hook from 10:00 + Illustration from 25:30 + Action from 50:00 = 1:30-2:15 meaningful reel
Even though non-sequential, it tells complete story.

Features:
- Complete sentence/phrase detection (no cut words)
- Scripture quoting detection (skip unless crucial)
- Non-sequential composition
- Hook -> Illustration -> Action structure
- Meaningful standalone message
"""

import re
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

# Bible books for scripture detection
BIBLE_BOOKS = [
    "genesis", "exodus", "leviticus", "numbers", "deuteronomy", "joshua", "judges", "ruth",
    "1 samuel", "2 samuel", "1 kings", "2 kings", "1 chronicles", "2 chronicles",
    "ezra", "nehemiah", "esther", "job", "psalm", "psalms", "proverbs", "ecclesiastes", "song of solomon",
    "isaiah", "jeremiah", "lamentations", "ezekiel", "daniel", "hosea", "joel", "amos", "obadiah", "jonah", "micah", "nahum", "habakkuk", "zephaniah", "haggai", "zechariah", "malachi",
    "matthew", "mark", "luke", "john", "acts", "romans", "1 corinthians", "2 corinthians", "galatians", "ephesians", "philippians", "colossians",
    "1 thessalonians", "2 thessalonians", "1 timothy", "2 timothy", "titus", "philemon", "hebrews", "james", "1 peter", "2 peter", "1 john", "2 john", "3 john", "jude", "revelation"
]

SCRIPTURE_PATTERNS = [
    r"\b(?:genesis|exodus|leviticus|numbers|deuteronomy|joshua|judges|ruth|samuel|kings|chronicles|ezra|nehemiah|esther|job|psalm|proverbs|ecclesiastes|isaiah|jeremiah|ezekiel|daniel|hosea|joel|amos|obadiah|jonah|micah|nahum|habakkuk|zephaniah|haggai|zechariah|malachi|matthew|mark|luke|john|acts|romans|corinthians|galatians|ephesians|philippians|colossians|thessalonians|timothy|titus|philemon|hebrews|james|peter|jude|revelation)\s+\d+:\d+",
    r"\b\d+:\d+\s*(?:says|declares|states)",
    r"(?:the bible says|scripture says|word of god says|it is written|as it is written)",
    r"(?:in the book of|according to)\s+\w+",
    r"\bchapter\s+\d+\s+verse\s+\d+",
]

HOOK_PATTERNS = [
    r"\b(have you ever|do you know|let me tell you|listen to this|imagine|what if|can i be honest|let me be real)\b",
    r"\b(joke|funny|laugh|hilarious)\b",
    r"^(you know what|the truth is|here's the thing|the problem is|the reason)",
    r"\b(viral|shocking|secret|mistake|never|stop|why you)\b",
    r"\?",
]

ILLUSTRATION_PATTERNS = [
    r"\b(for example|for instance|like when|imagine|story|illustration|there was a man|there was a woman|i remember|i knew someone|let me give you an example)\b",
    r"\b(because|so that|that is why|this means|in other words|what i mean is)\b",
]

ACTION_PATTERNS = [
    r"\b(you need to|you must|you should|i want you to|go and|you have to|it's time to|today|now is the time|i challenge you|i encourage you|will you|can you)\b",
    r"\b(ponder|think about|consider|remember|don't forget|hold on to)\b",
    r"\b(amen|hallelujah|praise god)\s*[.!?]*$",
]

class ScriptureDetector:
    def __init__(self):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in SCRIPTURE_PATTERNS]
        self.bible_books_pattern = re.compile(r'\b(' + '|'.join(BIBLE_BOOKS) + r')\b', re.IGNORECASE)
    
    def is_scripture_quote(self, text: str) -> Tuple[bool, float, str]:
        """
        Detect if text is scripture quoting
        Returns: (is_scripture, confidence, reason)
        """
        text_lower = text.lower()
        confidence = 0
        reasons = []
        
        # Check explicit patterns
        for pattern in self.patterns:
            if pattern.search(text):
                confidence += 0.4
                reasons.append(f"Pattern: {pattern.pattern[:30]}")
        
        # Check bible book + chapter:verse
        if re.search(r'\b\d+:\d+\b', text):
            if self.bible_books_pattern.search(text_lower):
                confidence += 0.5
                reasons.append("Bible book + verse")
            elif "says" in text_lower or "verse" in text_lower:
                confidence += 0.3
                reasons.append("Verse reference")
        
        # Check if text sounds like scripture (formal, thee/thou, etc) - lower confidence
        scripture_words = ["thou", "thee", "thy", "verily", "behold"]
        if any(w in text_lower for w in scripture_words):
            confidence += 0.2
            reasons.append("Scripture language")
        
        is_scripture = confidence >= 0.5
        return is_scripture, min(confidence, 1.0), "; ".join(reasons)


class SentenceSegmenter:
    """Ensures complete sentences/phrases, not cut words"""
    
    def __init__(self):
        # Simple sentence boundary detection - can be enhanced with spaCy
        self.sentence_endings = re.compile(r'[.!?]+["\']*\s+')
    
    def segment_into_sentences(self, timed_segments: List[Dict]) -> List[Dict]:
        """
        Convert whisper segments into complete sentences with accurate timestamps
        timed_segments: [{"start": 0.0, "end": 2.5, "text": "Hello world"}, ...]
        Returns: [{"start": 0.0, "end": 5.2, "text": "Hello world. This is complete.", "words": [...]}, ...]
        """
        # Combine all text
        full_text = " ".join([s["text"] for s in timed_segments])
        
        # Split into sentences using regex
        # Keep delimiters
        sentences = []
        last_end = 0
        
        # Use whisper word timestamps if available for better accuracy
        # For now, approximate by distributing time
        for seg in timed_segments:
            text = seg["text"].strip()
            if not text:
                continue
            
            # Split this segment's text into sentences
            parts = re.split(r'(?<=[.!?])\s+', text)
            
            seg_duration = seg["end"] - seg["start"]
            total_chars = len(text)
            current_time = seg["start"]
            
            for part in parts:
                part = part.strip()
                if not part or len(part) < 5:
                    continue
                
                # Estimate duration based on char length
                part_duration = (len(part) / total_chars) * seg_duration if total_chars > 0 else seg_duration / len(parts)
                
                sentences.append({
                    "start": current_time,
                    "end": current_time + part_duration,
                    "text": part,
                    "is_complete": self.is_complete_sentence(part),
                    "word_count": len(part.split())
                })
                
                current_time += part_duration
        
        # Merge very short sentences (< 8 words) with next to make meaningful phrases
        merged = []
        i = 0
        while i < len(sentences):
            curr = sentences[i]
            # If short and not complete, merge with next
            if curr["word_count"] < 8 and not curr["is_complete"] and i+1 < len(sentences):
                next_sent = sentences[i+1]
                merged.append({
                    "start": curr["start"],
                    "end": next_sent["end"],
                    "text": curr["text"] + " " + next_sent["text"],
                    "is_complete": next_sent["is_complete"],
                    "word_count": curr["word_count"] + next_sent["word_count"]
                })
                i += 2
            else:
                merged.append(curr)
                i += 1
        
        # Filter to only meaningful sentences (at least 8 words, complete)
        meaningful = [s for s in merged if s["word_count"] >= 8 and len(s["text"]) >= 20]
        
        print(f"Segmented {len(timed_segments)} whisper segments -> {len(meaningful)} meaningful sentences")
        return meaningful
    
    def is_complete_sentence(self, text: str) -> bool:
        """Check if text is complete sentence (starts capital, ends punctuation, has verb)"""
        text = text.strip()
        if len(text) < 10:
            return False
        
        # Starts with capital or "I"
        if not (text[0].isupper() or text.startswith("I ")):
            # Could still be complete if continuing, but lower confidence
            pass
        
        # Ends with punctuation
        if text[-1] not in ".!?":
            return False
        
        # Has at least 3 words and looks like sentence
        words = text.split()
        if len(words) < 5:
            return False
        
        return True


class SermonPointExtractor:
    """Extracts main points/topics from sermon"""
    
    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("Embedding model loaded for point extraction")
        except:
            self.embed_model = None
            print("No embedding model - using keyword clustering")
    
    def extract_points(self, sentences: List[Dict], num_points=5) -> List[Dict]:
        """
        Cluster sentences into main points/topics
        Returns: [{"point_id": 0, "theme": "Faith", "sentences": [...], "keywords": [...]}, ...]
        """
        if not sentences:
            return []
        
        # If embedding model available, use semantic clustering
        if self.embed_model and len(sentences) > 10:
            return self._extract_with_embeddings(sentences, num_points)
        else:
            return self._extract_with_keywords(sentences, num_points)
    
    def _extract_with_embeddings(self, sentences: List[Dict], num_points: int) -> List[Dict]:
        try:
            from sklearn.cluster import KMeans
            
            texts = [s["text"] for s in sentences]
            embeddings = self.embed_model.encode(texts)
            
            # KMeans clustering
            n_clusters = min(num_points, len(sentences)//3, 10)
            if n_clusters < 2:
                n_clusters = 2
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
            
            points = []
            for cluster_id in range(n_clusters):
                cluster_sentences = [s for s, label in zip(sentences, labels) if label == cluster_id]
                if not cluster_sentences:
                    continue
                
                # Extract theme keywords from cluster
                all_text = " ".join([s["text"] for s in cluster_sentences])
                keywords = self._extract_keywords(all_text)
                
                points.append({
                    "point_id": cluster_id,
                    "theme": ", ".join(keywords[:3]) if keywords else f"Point {cluster_id+1}",
                    "sentences": cluster_sentences,
                    "keywords": keywords,
                    "total_duration": sum(s["end"]-s["start"] for s in cluster_sentences),
                    "representative_text": cluster_sentences[len(cluster_sentences)//2]["text"] if cluster_sentences else ""
                })
            
            # Sort by total duration (main points are longer)
            points.sort(key=lambda x: x["total_duration"], reverse=True)
            return points[:num_points]
            
        except Exception as e:
            print(f"Embedding clustering failed: {e}, fallback to keywords")
            return self._extract_with_keywords(sentences, num_points)
    
    def _extract_with_keywords(self, sentences: List[Dict], num_points: int) -> List[Dict]:
        # Simple keyword-based grouping
        # Group by common important words
        keyword_groups = defaultdict(list)
        
        # Extract important words from each sentence
        for sent in sentences:
            keywords = self._extract_keywords(sent["text"])
            for kw in keywords[:2]:  # Top 2 keywords per sentence
                keyword_groups[kw].append(sent)
        
        # Create points from largest groups
        sorted_groups = sorted(keyword_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        points = []
        used_sentences = set()
        
        for kw, sents in sorted_groups[:num_points]:
            # Avoid duplicate sentences
            unique_sents = [s for s in sents if id(s) not in used_sentences]
            if len(unique_sents) < 3:
                continue
            
            for s in unique_sents:
                used_sentences.add(id(s))
            
            points.append({
                "point_id": len(points),
                "theme": kw,
                "sentences": unique_sents,
                "keywords": [kw],
                "total_duration": sum(s["end"]-s["start"] for s in unique_sents),
                "representative_text": unique_sents[0]["text"] if unique_sents else ""
            })
        
        return points
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords (nouns, key terms)"""
        # Simple keyword extraction - can be enhanced with spaCy
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"}
        
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter: not stop word, length > 3, appears as important
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count frequency
        from collections import Counter
        freq = Counter(keywords)
        # Return most common
        return [w for w, c in freq.most_common(10)]


class SermonReelComposer:
    """
    Main composer: Creates meaningful reels using Hook->Illustration->Action
    """
    
    def __init__(self):
        self.scripture_detector = ScriptureDetector()
        self.sentence_segmenter = SentenceSegmenter()
        self.point_extractor = SermonPointExtractor()
        
        self.hook_patterns = [re.compile(p, re.IGNORECASE) for p in HOOK_PATTERNS]
        self.illustration_patterns = [re.compile(p, re.IGNORECASE) for p in ILLUSTRATION_PATTERNS]
        self.action_patterns = [re.compile(p, re.IGNORECASE) for p in ACTION_PATTERNS]
    
    def classify_sentence_role(self, text: str) -> Dict[str, float]:
        """
        Classify sentence as Hook, Illustration, or Action
        Returns scores for each role
        """
        scores = {"hook": 0.0, "illustration": 0.0, "action": 0.0, "explanation": 0.0}
        text_lower = text.lower()
        
        # Hook scoring
        for pattern in self.hook_patterns:
            if pattern.search(text):
                scores["hook"] += 0.3
        if "?" in text:
            scores["hook"] += 0.2
        if len(text.split()) < 20 and len(text) > 10:  # Short punchy
            scores["hook"] += 0.1
        if text_lower.startswith(("you know", "listen", "imagine", "have you")):
            scores["hook"] += 0.4
        
        # Illustration scoring
        for pattern in self.illustration_patterns:
            if pattern.search(text):
                scores["illustration"] += 0.3
        if any(w in text_lower for w in ["because", "for example", "like", "story"]):
            scores["illustration"] += 0.2
        if len(text.split()) > 20:  # Longer explanatory
            scores["illustration"] += 0.1
        
        # Action scoring
        for pattern in self.action_patterns:
            if pattern.search(text):
                scores["action"] += 0.3
        if any(w in text_lower for w in ["you need", "you must", "go and", "today", "now"]):
            scores["action"] += 0.3
        if text.strip().endswith(("!",)) or "amen" in text_lower:
            scores["action"] += 0.2
        
        # Explanation is default if none high
        if max(scores.values()) < 0.3:
            scores["explanation"] = 0.5
        
        return scores
    
    def compose_reel_for_point(self, point: Dict, target_duration=105) -> Dict:
        """
        Compose one meaningful reel for a single point/theme
        Target: 90-135s (1:30-2:15), default 105s (1:45)
        Structure: Hook -> Illustration/Explanation -> Action
        
        point: {"theme": "Faith", "sentences": [...]}
        """
        sentences = point["sentences"]
        
        if not sentences:
            return None
        
        # Classify each sentence
        classified = []
        for sent in sentences:
            # Skip scripture unless crucial
            is_scripture, conf, reason = self.scripture_detector.is_scripture_quote(sent["text"])
            if is_scripture and conf > 0.7:
                # Skip scripture unless it's very short or crucial keyword present
                # Check if crucial: if it contains point keywords
                if not any(kw.lower() in sent["text"].lower() for kw in point["keywords"]):
                    continue  # Skip non-crucial scripture
            
            # Must be complete and meaningful
            if not sent["is_complete"] and sent["word_count"] < 10:
                continue
            
            roles = self.classify_sentence_role(sent["text"])
            dominant_role = max(roles, key=roles.get)
            max_score = roles[dominant_role]
            
            classified.append({
                **sent,
                "roles": roles,
                "dominant_role": dominant_role,
                "role_score": max_score,
                "is_scripture": is_scripture,
                "scripture_conf": conf
            })
        
        if not classified:
            return None
        
        # Group by role
        by_role = defaultdict(list)
        for c in classified:
            by_role[c["dominant_role"]].append(c)
        
        # Sort each role by score
        for role in by_role:
            by_role[role].sort(key=lambda x: x["role_score"], reverse=True)
        
        # Compose: Hook + Illustration/Explanation + Action
        # Even if non-sequential, we will order logically
        selected = []
        
        # 1. Hook - need 1 strong hook (15-25s)
        hooks = by_role.get("hook", [])
        if hooks:
            # Pick best hook, preferably from early in sermon but can be anywhere
            hook = hooks[0]
            # Ensure hook is complete and punchy
            if hook["word_count"] >= 8 and hook["word_count"] <= 30:
                selected.append(hook)
        
        # If no hook found, use most engaging sentence as hook
        if not selected:
            # Find sentence with question or exclamation or short punchy
            candidates = sorted(classified, key=lambda x: (x["roles"]["hook"] + (1 if "?" in x["text"] else 0)), reverse=True)
            if candidates:
                selected.append(candidates[0])
        
        # 2. Illustration/Explanation - need 1-2 (40-70s total)
        illustrations = by_role.get("illustration", []) + by_role.get("explanation", [])
        illustrations = sorted(illustrations, key=lambda x: x["role_score"], reverse=True)
        
        # Pick 1-2 illustrations that support the theme and are not same as hook
        for ill in illustrations[:3]:
            if ill not in selected and len(selected) < 3:
                # Avoid too much overlap in time if sequential, but allow non-sequential
                selected.append(ill)
                # Check total duration
                total_dur = sum(s["end"]-s["start"] for s in selected)
                if total_dur >= target_duration * 0.7:  # 70% of target
                    break
        
        # 3. Action - need 1 strong action/ponder (15-30s)
        actions = by_role.get("action", [])
        if actions:
            action = actions[0]
            if action not in selected:
                selected.append(action)
        
        # If still short, add more explanation
        total_dur = sum(s["end"]-s["start"] for s in selected)
        if total_dur < target_duration * 0.8 and len(classified) > len(selected):
            # Add best remaining that fits theme
            remaining = [c for c in classified if c not in selected]
            remaining = sorted(remaining, key=lambda x: x["role_score"], reverse=True)
            for r in remaining:
                if total_dur + (r["end"]-r["start"]) <= target_duration * 1.2:
                    selected.append(r)
                    total_dur += r["end"]-r["start"]
                if total_dur >= target_duration:
                    break
        
        if not selected:
            return None
        
        # Sort selected by time for natural flow, BUT we want logical order Hook->Ill->Action
        # So we will order by role, not time, to create meaningful story even if non-sequential
        # Hook first, then illustration, then action
        role_order = {"hook": 0, "illustration": 1, "explanation": 1, "action": 2}
        selected_sorted = sorted(selected, key=lambda x: (role_order.get(x["dominant_role"], 1), x["start"]))
        
        # Ensure total duration is within 90-135s
        total_dur = sum(s["end"]-s["start"] for s in selected_sorted)
        
        # If too short, try to extend by adding neighboring sentences for context
        if total_dur < 90:
            # For each selected, try to include previous/next sentence for context if it makes sense
            extended = []
            for sel in selected_sorted:
                # Find neighboring sentences in original list
                idx = None
                for i, s in enumerate(sentences):
                    if abs(s["start"] - sel["start"]) < 1.0:  # Same start time
                        idx = i
                        break
                
                if idx is not None:
                    # Add previous sentence if it provides context and is not scripture
                    if idx > 0:
                        prev = sentences[idx-1]
                        is_scr, conf, _ = self.scripture_detector.is_scripture_quote(prev["text"])
                        if not is_scr and prev["word_count"] >= 8:
                            # Check if adding keeps us under max
                            if total_dur + (prev["end"]-prev["start"]) <= 135:
                                extended.append(prev)
                                total_dur += prev["end"]-prev["start"]
                    
                    extended.append(sel)
                    
                    # Add next sentence if needed
                    if idx+1 < len(sentences) and total_dur < 90:
                        nxt = sentences[idx+1]
                        is_scr, conf, _ = self.scripture_detector.is_scripture_quote(nxt["text"])
                        if not is_scr and nxt["word_count"] >= 8:
                            if total_dur + (nxt["end"]-nxt["start"]) <= 135:
                                extended.append(nxt)
                                total_dur += nxt["end"]-nxt["start"]
                else:
                    extended.append(sel)
            
            selected_sorted = extended
        
        # Final check: ensure meaningful and complete
        # Remove any that are too short or incomplete
        final_selected = [s for s in selected_sorted if s["word_count"] >= 8]
        
        if not final_selected:
            return None
        
        total_dur = sum(s["end"]-s["start"] for s in final_selected)
        
        # If still too short (<60s) or too long (>150s), skip this point
        if total_dur < 60 or total_dur > 180:
            # Try to adjust: if too short, skip; if too long, trim to best 2-3
            if total_dur > 180:
                # Keep only top 3 by role score
                final_selected = sorted(final_selected, key=lambda x: x["role_score"], reverse=True)[:3]
                # Re-sort by role order
                final_selected = sorted(final_selected, key=lambda x: (role_order.get(x["dominant_role"], 1), x["start"]))
                total_dur = sum(s["end"]-s["start"] for s in final_selected)
        
        # Create final reel data
        # Sort by start time for actual cutting, but keep logical order for narrative
        # For non-sequential, we will cut and then concat in logical order
        # So we need to keep both: logical order and time order
        
        # For FFmpeg concat, we need to cut each segment and concat in logical order
        # The segments may be non-sequential in original video, but final reel is sequential in logical order
        
        combined_text = " ".join([s["text"] for s in final_selected])
        
        return {
            "theme": point["theme"],
            "sentences": final_selected,  # In logical order Hook->Ill->Action
            "sentences_by_time": sorted(final_selected, key=lambda x: x["start"]),  # By time
            "total_duration": total_dur,
            "combined_text": combined_text,
            "hook": [s for s in final_selected if s["dominant_role"] == "hook"],
            "illustration": [s for s in final_selected if s["dominant_role"] in ["illustration", "explanation"]],
            "action": [s for s in final_selected if s["dominant_role"] == "action"],
            "is_non_sequential": len(final_selected) > 1 and not self._is_sequential(final_selected),
            "meaningfulness_score": self._calculate_meaningfulness(final_selected)
        }
    
    def _is_sequential(self, sentences: List[Dict]) -> bool:
        """Check if sentences are sequential in original video"""
        if len(sentences) < 2:
            return True
        sorted_by_time = sorted(sentences, key=lambda x: x["start"])
        for i in range(len(sorted_by_time)-1):
            # If gap > 10 seconds, considered non-sequential
            if sorted_by_time[i+1]["start"] - sorted_by_time[i]["end"] > 10:
                return False
        return True
    
    def _calculate_meaningfulness(self, sentences: List[Dict]) -> float:
        """Score how meaningful/standalone the composed reel is"""
        score = 0.5
        
        # Has hook?
        has_hook = any(s["dominant_role"] == "hook" for s in sentences)
        if has_hook:
            score += 0.15
        
        # Has illustration/explanation?
        has_ill = any(s["dominant_role"] in ["illustration", "explanation"] for s in sentences)
        if has_ill:
            score += 0.15
        
        # Has action?
        has_action = any(s["dominant_role"] == "action" for s in sentences)
        if has_action:
            score += 0.15
        
        # All sentences complete?
        complete_ratio = sum(1 for s in sentences if s["is_complete"]) / len(sentences) if sentences else 0
        score += complete_ratio * 0.1
        
        # Average word count (meaningful phrases)
        avg_words = np.mean([s["word_count"] for s in sentences]) if sentences else 0
        if 10 <= avg_words <= 25:
            score += 0.05
        
        return min(score, 1.0)
    
    def compose_all_reels(self, long_video_path: str, target_duration=105, num_reels=5, min_duration=90, max_duration=135) -> List[Dict]:
        """
        Main entry: Long sermon video -> 5 meaningful reels (1:30-2:15 each)
        Each reel is non-sequential composition of different parts that support same point
        """
        print(f"\nComposing meaningful sermon reels from: {long_video_path}")
        print(f"Target: {num_reels} reels, {min_duration}-{max_duration}s each, structure Hook->Illustration->Action")
        
        # Step 1: Transcribe
        print("Step 1: Transcribing...")
        from faster_whisper import WhisperModel
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(long_video_path, beam_size=5)
        
        timed_segments = [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments]
        print(f"Transcribed {len(timed_segments)} segments")
        
        # Step 2: Segment into complete sentences
        print("Step 2: Segmenting into complete meaningful sentences...")
        sentences = self.sentence_segmenter.segment_into_sentences(timed_segments)
        print(f"Got {len(sentences)} meaningful sentences")
        
        if not sentences:
            print("No meaningful sentences found!")
            return []
        
        # Step 3: Extract main points
        print(f"Step 3: Extracting main sermon points...")
        points = self.point_extractor.extract_points(sentences, num_points=num_reels*2)  # Extract more, then pick best
        print(f"Found {len(points)} main points:")
        for p in points[:5]:
            print(f"  - {p['theme']}: {len(p['sentences'])} sentences, {p['total_duration']:.0f}s")
        
        # Step 4: Compose reel for each point
        print(f"Step 4: Composing {num_reels} meaningful reels (Hook->Illustration->Action)...")
        reels = []
        
        for point in points:
            if len(reels) >= num_reels:
                break
            
            reel = self.compose_reel_for_point(point, target_duration=target_duration)
            
            if reel and min_duration <= reel["total_duration"] <= max_duration*1.2:  # Allow slight over
                # Check meaningfulness
                if reel["meaningfulness_score"] >= 0.6:
                    reels.append(reel)
                    print(f"  ✓ Reel {len(reels)}: Theme '{reel['theme']}' | {reel['total_duration']:.0f}s | Meaningfulness {reel['meaningfulness_score']:.2f} | Non-sequential: {reel['is_non_sequential']}")
                    print(f"    Hook: {reel['hook'][0]['text'][:60] if reel['hook'] else 'None'}...")
                else:
                    print(f"  ✗ Skipped low meaningfulness: {reel['theme']} ({reel['meaningfulness_score']:.2f})")
        
        # Sort by meaningfulness
        reels.sort(key=lambda x: x["meaningfulness_score"], reverse=True)
        
        print(f"\nComposed {len(reels)} meaningful reels:")
        for i, reel in enumerate(reels, 1):
            print(f"{i}. Theme: {reel['theme']} | {reel['total_duration']:.0f}s | Score: {reel['meaningfulness_score']:.2f}")
            print(f"   Text: {reel['combined_text'][:100]}...")
        
        return reels


def compose_sermon_reels(long_video_path: str, num_reels=5, target_duration=105):
    """Convenience function"""
    composer = SermonReelComposer()
    return composer.compose_all_reels(long_video_path, target_duration=target_duration, num_reels=num_reels)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python sermon_reel_composer.py long_sermon.mp4 [num_reels=5]")
        print("\nThis creates MEANINGFUL reels, not just cuts:")
        print("- Complete sentences, not cut words")
        print("- Skips scripture quoting unless crucial")
        print("- Non-sequential: combines different parts that support same point")
        print("- Structure: Hook -> Illustration -> Action")
        print("- 1:30-2:15 long, meaningful standalone")
    else:
        video = sys.argv[1]
        num = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        reels = compose_sermon_reels(video, num_reels=num)
        print(f"\nDone: {len(reels)} reels composed")
