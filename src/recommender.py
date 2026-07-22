import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# --- Algorithm Recipe weights (see README "How The System Works") ---
GENRE_MATCH_POINTS = 2.0
MOOD_MATCH_POINTS = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_BONUS = 0.5
ACOUSTIC_THRESHOLD = 0.6

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Songs for a UserProfile, highest score first."""
        prefs = _profile_to_prefs(user)
        scored = [(song, score_song(prefs, asdict(song))[0]) for song in self.songs]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _score in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string of the reasons this song was scored."""
        _score, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return "; ".join(reasons)

def _profile_to_prefs(user: UserProfile) -> Dict:
    """Convert a UserProfile object into the score_song() prefs dict."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dicts with numeric fields cast."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            for field in ("energy", "valence", "danceability", "acousticness"):
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user prefs; return (score, reasons) per the recipe."""
    score = 0.0
    reasons: List[str] = []

    if song.get("genre") == user_prefs.get("genre"):
        score += GENRE_MATCH_POINTS
        reasons.append(f"genre match ({song['genre']}, +{GENRE_MATCH_POINTS:.1f})")

    if song.get("mood") == user_prefs.get("mood"):
        score += MOOD_MATCH_POINTS
        reasons.append(f"mood match ({song['mood']}, +{MOOD_MATCH_POINTS:.1f})")

    target = user_prefs.get("energy")
    if target is not None:
        closeness = ENERGY_WEIGHT * (1.0 - abs(float(target) - float(song["energy"])))
        score += closeness
        reasons.append(f"energy closeness (+{closeness:.2f})")

    if user_prefs.get("likes_acoustic") and float(song["acousticness"]) >= ACOUSTIC_THRESHOLD:
        score += ACOUSTIC_BONUS
        reasons.append(f"acoustic pick (+{ACOUSTIC_BONUS:.1f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, then return the top-k as (song, score, explanation)."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "no strong matches"
        scored.append((song, score, explanation))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
