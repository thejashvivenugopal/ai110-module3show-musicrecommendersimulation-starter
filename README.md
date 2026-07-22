# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube predict what you'll love next by
blending two ideas: **collaborative filtering** (learning from the behavior of
users similar to you — likes, skips, and shared playlists) and
**content-based filtering** (comparing the measurable attributes of songs, such
as energy, tempo, and mood). They train large models on billions of these signals.
My version is a small, transparent **content-based** recommender: instead of
learning from other users, it scores each song by how closely its attributes
match a single user's stated taste profile. It prioritizes **similarity over
popularity** — a song wins by matching the user's preferred genre, mood, and
energy level, not by being a hit. I chose this because it is easy to explain:
every recommendation comes with a human-readable reason.

### How a score is computed

1. **Scoring Rule (one song):** each song earns a weighted score built from
   feature matches. Numeric features (like `energy`) are scored by *closeness* —
   `1 - |target - actual|` — so a song near the user's target energy beats one
   that is simply louder or quieter. Categorical features (`genre`, `mood`) add
   fixed points on an exact match.
2. **Ranking Rule (the list):** every song is scored, the list is sorted by
   score (highest first), ties are broken, and the top *k* are returned.

### Finalized Algorithm Recipe

```
SCORE(song) =
    2.0   if song.genre == user.favorite_genre            else 0
  + 1.0   if song.mood  == user.favorite_mood             else 0
  + 1.5 * (1 - |user.target_energy - song.energy|)        # energy closeness (0–1)
  + 0.5   if user.likes_acoustic and song.acousticness >= 0.6  else 0
```

| Feature | Weight | Why |
|---|---|---|
| `genre` match | +2.0 | Strongest identity signal — a hard boundary users rarely cross |
| `mood` match | +1.0 | Real, but moods cross genres, so a softer signal |
| `energy` closeness | ×1.5 | Best-discriminating numeric feature; scored by proximity, not magnitude |
| `acousticness` fit | +0.5 | Applied only when the user `likes_acoustic` |

### Data flow

```
Input (UserProfile)  ──►  Process (loop: score_song judges each of 18 songs)
                                      │
                                      ▼
                          Ranking (sort by score, take top K)  ──►  Output (Top K + reasons)
```

### Expected biases

- **Genre over-prioritization.** With genre worth +2.0 and mood only +1.0, the
  system will favor same-genre songs even when an out-of-genre track better
  matches the user's mood and energy — a great mood-matched song from the "wrong"
  genre can be buried.
- **Energy is always-on; genre/mood are all-or-nothing.** Energy contributes a
  smooth partial score to every song, but genre and mood give points only on an
  *exact string match*. A "chill" user gets zero mood credit for a "relaxed"
  song even though they feel nearly identical — the model has no notion of
  similar-but-not-equal categories.
- **Small, curated catalog.** With 18 hand-made songs and no real listening
  history, results reflect my labeling choices, not real behavior. Rare
  genres (only one metal or classical track) can never form a strong cluster.

### Features used in the simulation

**`Song`** stores: `id`, `title`, `artist`, `genre`, `mood`, `energy`,
`tempo_bpm`, `valence`, `danceability`, `acousticness`.

**`UserProfile`** stores: `favorite_genre`, `favorite_mood`, `target_energy`,
`likes_acoustic`.

The scoring math uses `genre`, `mood`, `energy`, and `acousticness`; the other
song fields (`tempo_bpm`, `valence`, `danceability`) are available for
experiments described later in this README.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Produced by running `python -m src.main` with the default profile
`{genre: pop, mood: happy, energy: 0.8}`:

```
Loaded songs: 18

Top 5 recommendations for genre=pop, mood=happy, energy=0.8:

1. Sunrise City — Neon Echo  (score: 4.47)
   genre=pop, mood=happy, energy=0.82
   Because: genre match (pop, +2.0); mood match (happy, +1.0); energy closeness (+1.47)

2. Gym Hero — Max Pulse  (score: 3.30)
   genre=pop, mood=intense, energy=0.93
   Because: genre match (pop, +2.0); energy closeness (+1.30)

3. Rooftop Lights — Indigo Parade  (score: 2.44)
   genre=indie pop, mood=happy, energy=0.76
   Because: mood match (happy, +1.0); energy closeness (+1.44)

4. Concrete Kings — Blockprint  (score: 1.50)
   genre=hip-hop, mood=energetic, energy=0.8
   Because: energy closeness (+1.50)

5. Night Drive Loop — Neon Echo  (score: 1.42)
   genre=synthwave, mood=moody, energy=0.75
   Because: energy closeness (+1.42)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



