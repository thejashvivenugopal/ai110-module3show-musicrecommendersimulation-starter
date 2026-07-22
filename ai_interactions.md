# AI Interactions Log

> Documents the AI-assisted workflow used to build the stretch features for
> VibeFinder 1.0.

---

## Agentic Workflow (SF8) — Additional Song Attributes

**What task did you give the agent?**

Add 5+ meaningful attributes to the song dataset and update the scoring logic to
use them consistently, without breaking the existing tests or changing the
default recommendations.

**Prompts used:**

- "Analyze `songs.csv` and suggest 5 additional real-world song attributes that a
  content-based recommender could score on. Add them to all 18 rows with
  realistic values."
- "Update `score_song` so the new attributes only affect the score when the user
  opts in (e.g., `prefer_popular`, `target_decade`, `prefer_instrumental`), so
  existing profiles and documented outputs stay identical."

**What did the agent generate or change?**

- Added 5 columns to `data/songs.csv`: `popularity` (0–100), `release_decade`,
  `instrumentalness` (0–1), `language`, `duration_sec`.
- Added those fields to the `Song` dataclass **with default values** so the
  starter tests (which build `Song` without them) still pass.
- Extended `load_songs` to cast the new numeric columns.
- Added three opt-in scoring components to `score_song`: a popularity boost
  (scaled by `popularity/100`), a decade-match bonus, and an instrumental bonus.

**What did you verify or fix manually?**

- Confirmed the two starter tests still pass (defaults matter — new fields had to
  be added *after* the required ones with defaults).
- Confirmed the default profiles produce the exact same scores as before, since
  the new components are opt-in only.
- Verified with a "Trendy Instrumental" profile that all three new components
  actually appear in the reasons (e.g., `popularity boost (+0.72)`,
  `decade match (2020s, +1.0)`, `instrumental pick (+0.75)`).

---

## Design Pattern (SF10) — Multiple Ranking Modes

**Which design pattern did you use?**

The **Strategy pattern**. Each ranking mode is a named weight configuration in a
`RANKING_MODES` dictionary. `score_song` accepts a `weights` argument, so
swapping the strategy changes the whole ranking behavior without editing the
scoring logic itself.

**How did AI help you brainstorm or implement it?**

- Asked the AI for ways to let a user switch ranking strategies cleanly instead
  of copy-pasting the scoring function. It suggested the Strategy pattern and
  recommended representing each strategy as data (a weight dict) rather than a
  separate function, which keeps the modes trivial to add.
- Brainstormed four meaningful modes: `balanced`, `genre-first`, `mood-first`,
  and `energy-similarity` (which zeroes out genre/mood and ranks purely by how
  close the energy is).

**How does the pattern appear in your final code?**

- `RANKING_MODES` in `src/recommender.py` holds the strategies.
- `recommend_songs(..., mode="genre-first")` selects one and passes its weights
  to `score_song`.
- `src/main.py` runs the same profile through all four modes so you can compare.

---

## Diversity / Fairness (SF9)

**Feature:** an **artist-repeat penalty**. When `diversity=True`, songs by an
artist that already appears higher in the list are penalized (`-1.0` per earlier
appearance) and the list is re-sorted. This prevents one artist from dominating
the top results. Verified with the Chill Lofi profile, where "Focus Flow" (same
artist as "Midnight Coding") drops from 3.92 to 2.92 and yields to variety.

---

## Visual Output (SF11)

**Feature:** results render as a formatted table (via `tabulate` when installed,
with a built-in bordered-ASCII fallback so it always runs). The table shows rank,
title, artist, genre, energy, score, and the full "reasons" string, which makes
the scoring far easier to read than line-by-line prints.
