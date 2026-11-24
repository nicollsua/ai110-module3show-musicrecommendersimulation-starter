# AI Interactions Log

> Stretch features attempted: **Challenge 1 (Advanced Song Features)**, **Challenge 2 (Multiple Scoring Modes)**, **Challenge 3 (Diversity Penalty)**, and **Challenge 4 (Visual Summary Table)**. I also used an agentic workflow for most of the implementation, so that section is filled in too.

---

## Agentic Workflow (SF8)

**What task did you give the agent?**

I used Claude Code in agent mode inside VS Code and gave it the full project instructions. The goal was to go from the empty starter functions to a working CLI recommender, then add the stress-test profiles, the weight-shift experiment, and the stretch features, committing and pushing after each phase.

**Prompts used:**

- "Use Python's csv module to implement `load_songs` so it reads `data/songs.csv` and returns a list of dictionaries. Convert `id` to an int and energy, tempo_bpm, valence, danceability, and acousticness to floats so I can do math with them."
- "Implement `score_song(user_prefs, song)` with this recipe: +2.0 for a genre match, +1.0 for a mood match, and `1.5 * (1 - |song energy - target energy|)` for energy so it rewards closeness instead of just high energy. If the user sets `likes_acoustic`, add up to +0.5 based on acousticness. Return both the score and a list of reasons like 'genre match (+2.0)'."
- "What's the most Pythonic way to loop through every song, score it with `score_song`, and return the top k sorted from highest to lowest? Also explain the difference between `.sort()` and `sorted()`."
- "Suggest adversarial or edge-case user profiles that could trick this scoring logic, like conflicting preferences (high energy + sad mood)."
- "Apply this experiment: double the energy weight and halve the genre weight. Verify the math still makes sense (max score, no negative components)."
- "Brainstorm a simple design pattern so I can switch between ranking strategies like genre-first, mood-first, and energy-focused without copy-pasting the scoring function."
- "Add a diversity penalty: if a song's artist is already in the top recommendations, subtract points. Same for genre but smaller."
- "Add 5 new attributes to songs.csv that aren't in the baseline: popularity (0-100), release decade, detailed mood tags (like nostalgic, aggressive, euphoric), instrumentalness, and liveness. Fill in realistic values for all 20 songs. Then update score_song so it uses them, but only when the user profile sets the matching preference, so my existing profiles and documented outputs don't change."
- "Format the output as an ASCII table that still includes the reasons for each score. Don't add a new library."

**What did the agent generate or change?**

- `data/songs.csv`: added 10 songs covering genres/moods that weren't in the starter (hip hop, country, metal, classical, r&b, edm, folk, reggae, blues, and a sad pop song).
- `src/recommender.py`: `load_songs`, `score_song`, `recommend_songs`, the `Recommender` class methods, the `SCORING_MODES` dictionary, and the `_diverse_top_k` helper. Added 1-line docstrings to every function.
- `src/main.py`: 7 test profiles, a readable printout with reasons, `--mode`, `--profile`, `--diverse`, `--table`, and `-k` CLI flags.
- `data/songs.csv` (Challenge 1): 5 new columns: `popularity`, `release_decade`, `mood_tags` (semicolon-separated), `instrumentalness`, `liveness`.
- `src/recommender.py` (Challenge 1): a `_score_advanced_features` helper, called at the end of `score_song`. `load_songs` converts the new numeric columns, and the `Song` dataclass got the new fields with defaults so the starter tests still work.
- `src/main.py` (Challenge 1): two new profiles, "90s Nostalgia Hunter" and "Deep Focus Instrumental."
- `tests/test_recommender.py`: 6 new tests on top of the 2 starter tests.
- Ran `python -m src.main` and `pytest` after each change, and committed/pushed after each phase.

**What did you verify or fix manually?**

- **The diversity test was wrong at first.** The first version of the test asserted that the top 5 would have *no* repeat artists. That failed, because the penalty is soft (−1.0), and Focus Flow (a second LoRoom song) still scores high enough to stay in the top 5 for Chill Lofi. That's actually the behavior I want, so I rewrote the test to check that the repeat artist moves *down* (from #3 to #4, below Spacewalk Thoughts) and that the reason string mentions the penalty.
- **Challenge 1 didn't break anything.** I diffed the full output of the original 7 profiles before and after adding the new features, and it was identical. That confirmed the new rules really only apply when a profile opts in. I also hand-checked Dusty Porch Swing for the nostalgia profile: 2.0 + 1.0 + 1.47 + 0.46 + 0.5 + 0.9 + 0.09 = 6.42, which matches the terminal.
- **Starter tests vs new Song fields.** The starter tests build `Song(...)` objects with only the original 10 fields, so adding required fields would have broken them. I gave the new fields default values instead.
- **Import path.** The starter `main.py` used `from recommender import ...`, which breaks when you run `python -m src.main` from the project root. I made it try `src.recommender` first and fall back.
- **Math check on the experiment.** I hand-checked that in `energy_focused` mode the max score is 1.0 + 1.0 + 3.0 + 0.5 = 5.5, and that energy points can't go negative since energy values are all between 0 and 1 (so the gap is at most 1).
- **Hand-checked a few scores.** For example, Sunrise City for the pop/happy/0.8 user: 2.0 + 1.0 + 1.5 × (1 − 0.02) = 4.47, which matches the terminal output.
- **Sanity checked results against my own taste.** The Chill Lofi list felt right; the happy pop list had a sad song at #3 which I flagged as a bias instead of "fixing" it, because it's a real consequence of the weights and worth documenting.

---

## Design Pattern (SF10)

**Which design pattern did you use?**

A lightweight **Strategy** pattern.

**How did AI help you brainstorm or implement it?**

I asked for a way to support genre-first, mood-first, and energy-focused ranking without duplicating `score_song`. The AI gave two options: (1) a full class-based Strategy, with a `ScoringStrategy` base class and one subclass per mode, or (2) treating each strategy as just a set of weights in a dictionary, since every mode uses the exact same scoring steps and only the numbers change. I went with option 2 because the class version would have been 4 classes that only differ by 4 numbers, which felt like overkill for this project. If a mode ever needed totally different logic (like scoring by valence instead of mood), I'd switch to the class version.

**How does the pattern appear in your final code?**

- `SCORING_MODES` in `src/recommender.py` holds the strategies (`balanced`, `genre_first`, `mood_first`, `energy_focused`).
- `score_song(user_prefs, song, mode)` looks up the weights for the chosen mode and applies them, so there's one "judge" and swappable weight sets.
- `recommend_songs(..., mode=...)` passes the mode through, and `main.py` exposes it as `--mode`, so you can switch strategies from the command line, e.g. `python -m src.main --mode mood_first`.
- The diversity penalty is a separate re-ranking step (`_diverse_top_k`) layered on top, so it works with any scoring mode.
