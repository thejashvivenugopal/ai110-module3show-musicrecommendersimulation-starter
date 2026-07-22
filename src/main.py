"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs

# Profiles used to stress-test the recommender.
# The first three are "normal" tastes; the last two are adversarial
# (internally conflicting) profiles meant to see if the scoring can be tricked.
PROFILES = {
    "High-Energy Pop":  {"genre": "pop",   "mood": "happy",   "energy": 0.85},
    "Chill Lofi":       {"genre": "lofi",  "mood": "chill",   "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock":{"genre": "rock",  "mood": "intense", "energy": 0.9},
    # Adversarial: wants a calm mood but very high energy (contradiction).
    "Loud Sad (edge)":  {"genre": "metal", "mood": "melancholy", "energy": 0.95},
    # Adversarial: genre that is inherently low-energy/acoustic, but asks for
    # high energy and no acoustic — no song can satisfy all three.
    "Impossible Lofi (edge)": {"genre": "lofi", "mood": "energetic", "energy": 0.9, "likes_acoustic": False},
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Run and print the top-k recommendations for one named profile."""
    recommendations = recommend_songs(user_prefs, songs, k=k)
    print(f"\n=== Profile: {name} ===")
    print(f"prefs: {user_prefs}\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} — {song['artist']}  (score: {score:.2f})")
        print(f"   genre={song['genre']}, mood={song['mood']}, energy={song['energy']}")
        print(f"   Because: {explanation}\n")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    for name, prefs in PROFILES.items():
        print_recommendations(name, prefs, songs, k=5)


if __name__ == "__main__":
    main()
