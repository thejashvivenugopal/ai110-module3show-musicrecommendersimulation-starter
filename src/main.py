"""
Command line runner for the Music Recommender Simulation (VibeFinder 1.0).

Demonstrates the core recommender plus the stretch features:
- extra song attributes (popularity, release_decade, instrumentalness, ...)
- multiple ranking modes (Strategy pattern)
- an artist-diversity penalty (fairness)
- a formatted results table (tabulate, with an ASCII fallback)
"""

from src.recommender import load_songs, recommend_songs, RANKING_MODES

try:
    from tabulate import tabulate  # optional dependency
    _HAS_TABULATE = True
except ImportError:  # pragma: no cover - fallback path
    _HAS_TABULATE = False

# Profiles used to stress-test the recommender. The last two are adversarial
# (internally conflicting) profiles meant to see if the scoring can be tricked.
PROFILES = {
    "High-Energy Pop":  {"genre": "pop",   "mood": "happy",   "energy": 0.85},
    "Chill Lofi":       {"genre": "lofi",  "mood": "chill",   "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock":{"genre": "rock",  "mood": "intense", "energy": 0.9},
    "Loud Sad (edge)":  {"genre": "metal", "mood": "melancholy", "energy": 0.95},
    "Impossible Lofi (edge)": {"genre": "lofi", "mood": "energetic", "energy": 0.9, "likes_acoustic": False},
    # Uses the stretch attributes: wants popular, 2020s, instrumental music.
    "Trendy Instrumental": {"genre": "lofi", "mood": "chill", "energy": 0.4,
                             "likes_acoustic": True, "prefer_popular": True,
                             "target_decade": 2020, "prefer_instrumental": True},
}


def render_table(recommendations: list) -> str:
    """Render recommendations as a table, using tabulate when available."""
    headers = ["#", "Title", "Artist", "Genre", "Energy", "Score", "Reasons"]
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        rows.append([
            rank, song["title"], song["artist"], song["genre"],
            song["energy"], f"{score:.2f}", explanation,
        ])
    if _HAS_TABULATE:
        return tabulate(rows, headers=headers, tablefmt="rounded_grid")
    return _ascii_table(headers, rows)


def _ascii_table(headers: list, rows: list) -> str:
    """Minimal dependency-free bordered table (fallback for tabulate)."""
    cols = list(zip(*([headers] + rows))) if rows else [[h] for h in headers]
    widths = [max(len(str(c)) for c in col) for col in cols]
    line = "+".join("-" * (w + 2) for w in widths)
    border = f"+{line}+"

    def fmt(cells):
        return "| " + " | ".join(str(c).ljust(w) for c, w in zip(cells, widths)) + " |"

    out = [border, fmt(headers), border]
    out += [fmt(r) for r in rows]
    out.append(border)
    return "\n".join(out)


def show(name: str, prefs: dict, songs: list, mode: str = "balanced",
         diversity: bool = False, k: int = 5) -> None:
    """Run one profile and print its recommendations as a table."""
    recs = recommend_songs(prefs, songs, k=k, mode=mode, diversity=diversity)
    tag = f"mode={mode}" + (", diversity=ON" if diversity else "")
    print(f"\n=== {name} ({tag}) ===")
    print(f"prefs: {prefs}")
    print(render_table(recs))


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print(f"Available ranking modes: {', '.join(RANKING_MODES)}")

    # 1) Core profiles in the default (balanced) mode, shown as tables.
    for name, prefs in PROFILES.items():
        show(name, prefs, songs)

    # 2) Same profile, different ranking modes (Strategy pattern in action).
    print("\n\n########## RANKING MODE COMPARISON (High-Energy Pop) ##########")
    for mode in RANKING_MODES:
        show("High-Energy Pop", PROFILES["High-Energy Pop"], songs, mode=mode, k=3)

    # 3) Diversity penalty: Chill Lofi has repeated artists (LoRoom) without it.
    print("\n\n########## DIVERSITY PENALTY (Chill Lofi) ##########")
    show("Chill Lofi", PROFILES["Chill Lofi"], songs, diversity=False)
    show("Chill Lofi", PROFILES["Chill Lofi"], songs, diversity=True)


if __name__ == "__main__":
    main()
