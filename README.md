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

## Multi-Profile Evaluation

Output of `python -m src.main`, which runs five profiles — three normal tastes
and two adversarial (self-contradicting) edge cases.

```
=== Profile: High-Energy Pop ===
prefs: {'genre': 'pop', 'mood': 'happy', 'energy': 0.85}

1. Sunrise City — Neon Echo  (score: 4.46)  genre=pop, mood=happy, energy=0.82
   Because: genre match (pop, +2.0); mood match (happy, +1.0); energy closeness (+1.46)
2. Gym Hero — Max Pulse  (score: 3.38)  genre=pop, mood=intense, energy=0.93
   Because: genre match (pop, +2.0); energy closeness (+1.38)
3. Rooftop Lights — Indigo Parade  (score: 2.37)  genre=indie pop, mood=happy, energy=0.76
   Because: mood match (happy, +1.0); energy closeness (+1.36)
4. Concrete Kings — Blockprint  (score: 1.43)  genre=hip-hop, mood=energetic, energy=0.8
   Because: energy closeness (+1.43)
5. Storm Runner — Voltline  (score: 1.41)  genre=rock, mood=intense, energy=0.91
   Because: energy closeness (+1.41)

=== Profile: Chill Lofi ===
prefs: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'likes_acoustic': True}

1. Library Rain — Paper Lanterns  (score: 5.00)  genre=lofi, mood=chill, energy=0.35
   Because: genre match (lofi, +2.0); mood match (chill, +1.0); energy closeness (+1.50); acoustic pick (+0.5)
2. Midnight Coding — LoRoom  (score: 4.89)  genre=lofi, mood=chill, energy=0.42
   Because: genre match (lofi, +2.0); mood match (chill, +1.0); energy closeness (+1.40); acoustic pick (+0.5)
3. Focus Flow — LoRoom  (score: 3.92)  genre=lofi, mood=focused, energy=0.4
   Because: genre match (lofi, +2.0); energy closeness (+1.42); acoustic pick (+0.5)
4. Spacewalk Thoughts — Orbit Bloom  (score: 2.90)  genre=ambient, mood=chill, energy=0.28
   Because: mood match (chill, +1.0); energy closeness (+1.40); acoustic pick (+0.5)
5. Coffee Shop Stories — Slow Stereo  (score: 1.97)  genre=jazz, mood=relaxed, energy=0.37
   Because: energy closeness (+1.47); acoustic pick (+0.5)

=== Profile: Deep Intense Rock ===
prefs: {'genre': 'rock', 'mood': 'intense', 'energy': 0.9}

1. Storm Runner — Voltline  (score: 4.48)  genre=rock, mood=intense, energy=0.91
   Because: genre match (rock, +2.0); mood match (intense, +1.0); energy closeness (+1.48)
2. Gym Hero — Max Pulse  (score: 2.46)  genre=pop, mood=intense, energy=0.93
   Because: mood match (intense, +1.0); energy closeness (+1.46)
3. Neon Warehouse — Pulse Theory  (score: 1.43)  genre=edm, mood=energetic, energy=0.95
   Because: energy closeness (+1.43)
4. Iron Verdict — Ashfall  (score: 1.38)  genre=metal, mood=aggressive, energy=0.98
   Because: energy closeness (+1.38)
5. Sunrise City — Neon Echo  (score: 1.38)  genre=pop, mood=happy, energy=0.82
   Because: energy closeness (+1.38)

=== Profile: Loud Sad (edge) — genre=metal, mood=melancholy, energy=0.95 ===

1. Iron Verdict — Ashfall  (score: 3.46)  genre=metal, mood=aggressive, energy=0.98
   Because: genre match (metal, +2.0); energy closeness (+1.46)
2. Neon Warehouse — Pulse Theory  (score: 1.50)  genre=edm, mood=energetic, energy=0.95
   Because: energy closeness (+1.50)
3. Gym Hero — Max Pulse  (score: 1.47)  genre=pop, mood=intense, energy=0.93
   Because: energy closeness (+1.47)
4. Storm Runner — Voltline  (score: 1.44)  genre=rock, mood=intense, energy=0.91
   Because: energy closeness (+1.44)
5. Winter Nocturne — Clara Wynn  (score: 1.41)  genre=classical, mood=melancholy, energy=0.22
   Because: mood match (melancholy, +1.0); energy closeness (+0.41)

=== Profile: Impossible Lofi (edge) — genre=lofi, mood=energetic, energy=0.9, likes_acoustic=False ===

1. Midnight Coding — LoRoom  (score: 2.78)  genre=lofi, mood=chill, energy=0.42
   Because: genre match (lofi, +2.0); energy closeness (+0.78)
2. Focus Flow — LoRoom  (score: 2.75)  genre=lofi, mood=focused, energy=0.4
   Because: genre match (lofi, +2.0); energy closeness (+0.75)
3. Library Rain — Paper Lanterns  (score: 2.67)  genre=lofi, mood=chill, energy=0.35
   Because: genre match (lofi, +2.0); energy closeness (+0.67)
4. Neon Warehouse — Pulse Theory  (score: 2.42)  genre=edm, mood=energetic, energy=0.95
   Because: mood match (energetic, +1.0); energy closeness (+1.43)
5. Concrete Kings — Blockprint  (score: 2.35)  genre=hip-hop, mood=energetic, energy=0.8
   Because: mood match (energetic, +1.0); energy closeness (+1.35)
```

---

## Experiments You Tried

**Experiment: weight shift — double energy, halve genre.**
I temporarily set `ENERGY_WEIGHT = 3.0` and `GENRE_MATCH_POINTS = 1.0` (from
1.5 and 2.0), then reverted after observing the effect.

- **Impossible Lofi** (wants `energy=0.9` but `genre=lofi`) flipped completely.
  Under the default recipe the top 3 were low-energy lofi tracks (energy
  0.35–0.42); under the experiment the top 5 became the *highest*-energy songs in
  the catalog (Neon Warehouse 0.95, Gym Hero 0.93, Storm Runner 0.91). Energy now
  wins the tug-of-war against genre.
- **High-Energy Pop** kept Sunrise City at #1 (it matches everything), but the
  ranking below it tilted toward raw energy.

**Verdict:** the change made results *different, not universally more accurate*.
It fixed the contradictory edge case (honoring the stated energy) but weakened
the intuitive normal profiles, where matching the favorite genre is genuinely
what a user expects. This is why the finalized recipe keeps genre at +2.0 — the
right weight depends on whether you trust the user's genre label or their numbers
more.

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



