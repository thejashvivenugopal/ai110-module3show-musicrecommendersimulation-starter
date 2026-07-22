# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

A tiny, explain-everything music recommender.

---

## 2. Goal / Task

VibeFinder suggests songs that match a person's stated taste. You give it a
favorite genre, a favorite mood, and a target energy level. It looks through the
song catalog and returns the top 5 songs that fit best. Every suggestion comes
with a plain reason so you can see *why* it was picked. It tries to predict which
songs you would enjoy right now based on how close each song is to your taste.

---

## 3. Algorithm Summary

Think of it as a small points contest for each song:

- A song earns **+2.0 points** if its genre matches your favorite genre.
- It earns **+1.0 point** if its mood matches your favorite mood.
- It earns up to **+1.5 points** for having energy close to your target. The
  closer the match, the more points — a big gap earns almost nothing.
- If you say you like acoustic music, a calm, acoustic song earns a small
  **+0.5 bonus**.

Every song gets a total score, and the system sorts them from highest to lowest
and shows the top 5. The main change from the starter code is that energy is
scored by *closeness* (how near it is to what you want) instead of just rewarding
louder or quieter songs.

---

## 4. Data Used

- **18 songs** in the catalog, stored in `data/songs.csv`.
- Each song has: genre, mood, energy, tempo, valence, danceability, and
  acousticness.
- The starter file had 10 songs; I added 8 to cover more variety, reaching
  **15 genres** (pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop,
  edm, classical, r&b, metal, country, reggae, folk) and **12 moods**.
- **Limits:** it is still tiny and hand-made. Some genres have only one song, so
  those tastes cannot be served well. There is no real listening history, no
  lyrics, and no language or artist-similarity information.

---

## 5. Strengths  

- It works well for **clear, consistent tastes**. When genre, mood, and energy
  all point the same way (like "High-Energy Pop" or "Chill Lofi"), the top
  results feel right.
- The **explanations are honest** — you can always see exactly which rule earned
  the points, which makes the system easy to trust and debug.
- It correctly separates **opposite vibes**: intense rock and chill lofi never
  get confused for each other.

---

## 6. Limitations and Bias 

The biggest weakness I found is that **genre is worth a flat +2.0 no matter
what, so it can override every other preference.** I discovered this with an
"Impossible Lofi" profile that asked for `genre=lofi` but `energy=0.9`. Lofi is
inherently low-energy music, so no song could satisfy both — yet the top three
results were all lofi tracks with energy around 0.35–0.42, the exact opposite of
what the user asked for. The genre points simply outweighed the large energy
gap. This means the system can trap a user in a **filter bubble**: if you name a
genre, you will almost always get that genre back, even when your other
preferences point somewhere else. A second, related bias is that genre and mood
only reward **exact string matches** — a user who likes "chill" gets zero credit
for a "relaxed" song even though they feel nearly identical, so users whose taste
sits between my labels are served worse. Finally, rare genres (only one metal or
classical track) can never form a strong cluster, so those users see thinner,
lower-quality lists than pop or lofi users.

---

## 7. Evaluation  

I tested five profiles with `python -m src.main`: three normal tastes
(High-Energy Pop, Chill Lofi, Deep Intense Rock) and two adversarial profiles
with self-contradicting preferences (Loud Sad, Impossible Lofi). For each I
looked at whether the top 5 matched the intent and whether the explanations made
sense. Full output is in the README "Multi-Profile Evaluation" section.

**Profile comparisons (plain language):**

- **High-Energy Pop vs. Chill Lofi.** These are near-opposites and the system
  handled them cleanly: Pop returned bright, fast songs (Sunrise City, Gym Hero)
  while Lofi returned quiet, acoustic ones (Library Rain, Midnight Coding). This
  makes sense because their genre, mood, *and* energy all point in opposite
  directions, so all three scoring rules agree.
- **Chill Lofi vs. Deep Intense Rock.** Lofi's list is dominated by the acoustic
  bonus (every top pick is acoustic), while Rock's list ignores acousticness
  entirely and rewards high energy. This shows the `likes_acoustic` flag is doing
  real work only when the user turns it on.
- **Deep Intense Rock vs. Loud Sad (edge).** Both want loud music, and both
  surfaced the same high-energy pool (Gym Hero, Storm Runner, Iron Verdict). The
  difference is the genre anchor: Rock puts Storm Runner first, Loud Sad puts
  Iron Verdict (metal) first. The "melancholy" mood barely mattered because only
  one melancholy song exists and it is very low energy.
- **Impossible Lofi (edge) — the surprise.** This was the most revealing. The
  user asked for high energy, but got the *lowest*-energy songs in the catalog,
  because genre points (+2.0) beat the energy gap. This is the clearest proof
  that genre currently dominates the recipe.

**What surprised me:** how easily one flat category weight could completely
override a strong numeric preference.

**Explaining "Gym Hero" to a non-programmer:** imagine each song earns points in
a small contest. A song gets a big chunk of points just for being the *right
genre*, another chunk for the *right mood*, and some points for having *about the
right energy*. "Gym Hero" is pop and very high-energy, so even though its mood is
"intense" instead of "happy," the genre + energy points alone are enough to keep
it near the top for a Happy-Pop fan. It keeps showing up because being in the
favorite genre is worth so much that a mismatched mood can't push it down far.

---

## 8. Intended Use and Non-Intended Use

**Intended use:** VibeFinder is a classroom project for learning how recommender
systems turn data into ranked suggestions. It is meant for exploring scoring
rules and seeing how weights change results.

**Not intended for:** real users or production apps. It should not be used to
make important decisions, to judge what music is "good," or as a real music
service. With only 18 songs and no real listening data, it cannot represent real
musical taste, and its genre bias would treat some users unfairly.

---

## 9. Ideas for Improvement

1. **Rebalance genre vs. energy** so a strong numeric preference can override a
   genre match, fixing the "Impossible Lofi" filter-bubble problem.
2. **Add fuzzy category matching** so similar moods (like "chill" and "relaxed")
   give partial credit instead of all-or-nothing.
3. **Grow and balance the catalog** so every genre has several songs, and add
   diversity to the top 5 so it is not all one artist or genre.

---

## 10. Personal Reflection  

My biggest learning moment was watching the "Impossible Lofi" test. I asked for
high energy but got the quietest songs in the catalog. That one result made the
idea of "weights" click — a single number (genre = +2.0) can quietly control the
whole outcome. It taught me that a recommender's behavior lives in its numbers,
not just its code.

AI tools helped me move fast: brainstorming features, generating new songs for
the dataset, and drafting the scoring logic. But I had to double-check them. For
example, the AI's suggested import broke when I ran the app as a module, and I
had to verify the math and the returned data shapes matched what the tests
expected. The AI was a strong first-draft partner, but I stayed the one deciding
the logic.

What surprised me most was how a handful of simple `if` statements and one
distance formula could produce lists that genuinely *feel* like recommendations.
There is no machine learning here at all, yet the explanations make it feel
smart. If I kept going, I would add fuzzy mood matching and let the system learn
weights from which songs a user actually keeps, so it improves over time instead
of following fixed rules.
