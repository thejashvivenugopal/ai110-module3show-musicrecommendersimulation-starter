import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# --- Algorithm Recipe weights (see README "How The System Works") ---
GENRE_MATCH_POINTS = 2.0
MOOD_MATCH_POINTS = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_BONUS = 0.5
ACOUSTIC_THRESHOLD = 0.6

# --- Stretch: extra attribute weights (opt-in, only used if the user asks) ---
POPULARITY_WEIGHT = 1.0        # scaled by popularity / 100
DECADE_MATCH_POINTS = 1.0
INSTRUMENTAL_BONUS = 0.75
INSTRUMENTAL_THRESHOLD = 0.6

# --- Stretch: diversity / fairness ---
ARTIST_PENALTY = 1.0           # subtracted per earlier appearance of the same artist

# --- Stretch: ranking modes (Strategy pattern) ---
# Each mode is a named weight configuration. Switching mode swaps the whole
# scoring strategy without touching score_song's logic.
RANKING_MODES: Dict[str, Dict[str, float]] = {
    "balanced":          {"genre": 2.0, "mood": 1.0, "energy": 1.5, "acoustic": 0.5},
    "genre-first":       {"genre": 4.0, "mood": 1.0, "energy": 0.5, "acoustic": 0.5},
    "mood-first":        {"genre": 1.0, "mood": 4.0, "energy": 0.5, "acoustic": 0.5},
    "energy-similarity": {"genre": 0.0, "mood": 0.0, "energy": 3.0, "acoustic": 0.0},
}
DEFAULT_MODE = "balanced"

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
    # Stretch attributes (defaults keep the starter tests working).
    popularity: int = 50
    release_decade: int = 2020
    instrumentalness: float = 0.0
    language: str = "english"
    duration_sec: int = 200

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
            for field in ("energy", "valence", "danceability", "acousticness", "instrumentalness"):
                if field in row and row[field] != "":
                    row[field] = float(row[field])
            for field in ("popularity", "release_decade", "duration_sec"):
                if field in row and row[field] != "":
                    row[field] = int(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict, weights: Optional[Dict[str, float]] = None) -> Tuple[float, List[str]]:
    """Score one song against user prefs; return (score, reasons) per the recipe."""
    if weights is None:
        weights = RANKING_MODES[DEFAULT_MODE]

    score = 0.0
    reasons: List[str] = []

    w_genre = weights.get("genre", 0.0)
    if w_genre and song.get("genre") == user_prefs.get("genre"):
        score += w_genre
        reasons.append(f"genre match ({song['genre']}, +{w_genre:.1f})")

    w_mood = weights.get("mood", 0.0)
    if w_mood and song.get("mood") == user_prefs.get("mood"):
        score += w_mood
        reasons.append(f"mood match ({song['mood']}, +{w_mood:.1f})")

    w_energy = weights.get("energy", 0.0)
    target = user_prefs.get("energy")
    if w_energy and target is not None:
        closeness = w_energy * (1.0 - abs(float(target) - float(song["energy"])))
        score += closeness
        reasons.append(f"energy closeness (+{closeness:.2f})")

    w_acoustic = weights.get("acoustic", 0.0)
    if w_acoustic and user_prefs.get("likes_acoustic") and float(song.get("acousticness", 0)) >= ACOUSTIC_THRESHOLD:
        score += w_acoustic
        reasons.append(f"acoustic pick (+{w_acoustic:.1f})")

    # --- Stretch attributes: only applied when the user opts in ---
    if user_prefs.get("prefer_popular") and song.get("popularity") is not None:
        bonus = POPULARITY_WEIGHT * (float(song["popularity"]) / 100.0)
        score += bonus
        reasons.append(f"popularity boost (+{bonus:.2f})")

    target_decade = user_prefs.get("target_decade")
    if target_decade is not None and song.get("release_decade") is not None:
        if int(song["release_decade"]) == int(target_decade):
            score += DECADE_MATCH_POINTS
            reasons.append(f"decade match ({target_decade}s, +{DECADE_MATCH_POINTS:.1f})")

    if user_prefs.get("prefer_instrumental") and song.get("instrumentalness") is not None:
        if float(song["instrumentalness"]) >= INSTRUMENTAL_THRESHOLD:
            score += INSTRUMENTAL_BONUS
            reasons.append(f"instrumental pick (+{INSTRUMENTAL_BONUS:.2f})")

    return score, reasons

def _apply_artist_penalty(scored: List[list]) -> List[list]:
    """Penalize repeated artists so the list does not fill up with one artist."""
    seen: Dict[str, int] = {}
    for item in scored:
        artist = item[0].get("artist")
        prior = seen.get(artist, 0)
        if prior > 0:
            penalty = ARTIST_PENALTY * prior
            item[1] -= penalty
            item[2] = item[2] + [f"artist repeat penalty (-{penalty:.1f})"]
        seen[artist] = prior + 1
    return scored

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = DEFAULT_MODE,
    diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Score every song, then return the top-k as (song, score, explanation)."""
    weights = RANKING_MODES.get(mode, RANKING_MODES[DEFAULT_MODE])

    scored: List[list] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        scored.append([song, score, reasons])

    scored.sort(key=lambda item: item[1], reverse=True)

    if diversity:
        # Penalize in ranked order, then re-sort so variety rises to the top.
        scored = _apply_artist_penalty(scored)
        scored.sort(key=lambda item: item[1], reverse=True)

    results: List[Tuple[Dict, float, str]] = []
    for song, score, reasons in scored[:k]:
        explanation = "; ".join(reasons) if reasons else "no strong matches"
        results.append((song, score, explanation))
    return results
