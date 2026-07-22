# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
