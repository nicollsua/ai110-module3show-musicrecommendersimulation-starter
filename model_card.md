# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeCheck 1.0**

---

## 2. Intended Use

VibeCheck suggests the top 5 songs from a small catalog based on a single user's taste profile (favorite genre, favorite mood, target energy level, and optionally whether they like acoustic music). Every recommendation comes with a list of reasons, so you can see exactly why a song was picked.

It assumes the user can describe their taste with one genre, one mood, and one energy number, and that they want the same vibe across the whole list.

**Intended use:** classroom exploration of how content-based recommenders turn data into rankings, and a sandbox for seeing how weights and bias affect results.

**Not intended for:** real users or a real product. It has 20 songs, no listening history, and no feedback loop, so it can't learn anything about you. It also shouldn't be used to make claims about what "good" music is, or to decide which artists get exposure, since the scoring obviously favors whatever genres happen to be well-represented in the CSV.

---

## 3. How the Model Works

Think of it like a judge with a scorecard. For every song in the catalog, the judge checks the song against what you said you like and hands out points:

- **Same genre as your favorite?** +2 points. This is the biggest one.
- **Same mood as your favorite?** +1 point.
- **Energy close to what you want?** Up to +1.5 points. A perfect match gets the full 1.5, and you lose points the further away the song is. So if you want 0.8 energy, a 0.82 song gets almost everything, but a 0.3 song only gets about half. The important part is that it rewards being *close*, not being *high*.
- **Acoustic preference (optional).** Up to +0.5 points. If you like acoustic music, more acoustic songs get more points. If you don't, the reverse.

After every song has a score, the songs are sorted from highest to lowest and the top 5 are shown. The best possible score is 5.0.

**Changes from the starter:** The starter code had empty functions, so I built the scoring from scratch. On top of the base recipe I added:
- **Scoring modes** (`balanced`, `genre_first`, `mood_first`, `energy_focused`), which are just different weight settings for the same judge.
- An optional **diversity penalty**: once an artist is in the list, their other songs lose 1 point, and once a genre is in the list, other songs from that genre lose 0.5. This keeps the top 5 from being three songs by the same person.

---

## 4. Data

- **20 songs** in `data/songs.csv`. The starter came with 10, and I added 10 more to cover genres and moods that were missing.
- **Genres (15):** pop (3), lofi (3), rock, ambient, jazz, synthwave, indie pop, hip hop, country, metal, classical, r&b, edm, folk, reggae, blues.
- **Moods (14):** happy, chill, intense, relaxed, moody, focused, confident, nostalgic, angry, peaceful, romantic, euphoric, sad, melancholy.
- **Numeric features:** energy, tempo_bpm, valence, danceability, acousticness (all 0 to 1 except tempo).

**Limits:** Most genres only have one song, so if you like metal, there is exactly one metal song for you. There's no lyrics, language, release year, popularity, or artist info beyond a name. The numbers were made up to "feel right," not measured from real audio. And a big part of musical taste is missing entirely: context (working out vs studying), nostalgia, and the fact that most people like more than one genre.

---

## 5. Strengths

- **Clear-cut profiles work really well.** Chill Lofi, Deep Intense Rock, and High-Energy Pop all got the exact song I would have picked at #1, with scores of 4.9+.
- **The explanations are honest.** Since every point is listed out, it's easy to see *why* something weird shows up, which made debugging the bias way easier.
- **Energy closeness is a good tiebreaker.** For the Chill Lofi profile, the two lofi/chill songs both match on genre and mood, and the one whose energy is closer to 0.35 (Library Rain) wins. That's the behavior I wanted.
- **It degrades kind of gracefully.** When the genre doesn't exist (the "k-pop" profile), it falls back to mood + energy and gives reasonable upbeat songs instead of returning garbage.

---

## 6. Limitations and Bias

The biggest weakness I found is that **genre overpowers everything else, and the catalog's genre imbalance turns that into a filter bubble.** Pop has 3 songs in the catalog while most genres have 1, so a pop fan always gets 3 songs with a free +2.0 head start, even when those songs have completely the wrong mood. In the default "happy pop" run, "Heartbreak Neon" (a *sad* pop song) ranked above "Rooftop Lights" (a happy song that's basically pop but labeled "indie pop"), because exact string matching gives "indie pop" zero genre credit. Meanwhile, a user who likes metal, folk, or classical gets one genre match and then the rest of their list is filled with whatever has similar energy, which is how a metal fan ends up with "Sunrise City" (a happy pop song) at #5. So the system quietly gives pop and lofi fans better, more varied lists than people with niche taste.

A second issue is the **energy "floor."** Because energy closeness is linear, almost every song gets at least 0.75–1.5 points just for existing. That means for users with no genre match, the bottom of the list is basically sorted by energy alone, and "Gym Hero" (0.93 energy) ends up in the top 5 for 5 out of my 7 profiles. It also means users with mid-range energy targets (around 0.5) can never be "far" from any song, so their rankings are flatter and less meaningful than for users at the extremes.

Lastly, **conflicting preferences get silently resolved in favor of labels.** The "Sad but Hyped" user (folk, sad, energy 0.9) got a slow, quiet folk song at #1 because the genre + mood labels (+3.0) outweighed the huge energy mismatch. The system never tells the user "hey, nothing actually fits what you asked for." And the "likes acoustic" preference is basically ignored for high-energy users because the catalog has no loud acoustic songs.

---

## 7. Evaluation

### Profiles tested

I tested 4 "normal" profiles and 3 adversarial ones that I brainstormed with AI to try to break the scoring:

| Profile | genre | mood | energy | likes_acoustic | Why |
|---|---|---|---|---|---|
| Default Pop/Happy | pop | happy | 0.80 | – | starter profile |
| High-Energy Pop | pop | intense | 0.95 | False | workout vibe |
| Chill Lofi | lofi | chill | 0.35 | True | study vibe |
| Deep Intense Rock | rock | intense | 0.90 | False | only 1 rock song exists |
| Sad but Hyped | folk | sad | 0.90 | – | conflicting: sad labels, high energy |
| Ghost Genre | k-pop | happy | 0.70 | – | genre not in catalog |
| Acoustic Headbanger | metal | angry | 0.95 | True | conflicting: loud but acoustic |

### What surprised me

- **"Gym Hero" is everywhere.** It shows up in the top 5 for 5 of 7 profiles. To a non-programmer: Gym Hero is pop, it's intense, and it's very high energy. The system gives points for "close energy" to basically anyone who wants energetic music, and gives +2 to anyone who likes pop. So it's a decent "second choice" for a lot of different people, and since the catalog is small, there isn't much competition for those slots. It's not that the system thinks Gym Hero is a great happy song, it's that it's the least-bad option for a lot of profiles.
- **Labels beat vibes.** "Sad but Hyped" got a quiet folk ballad at #1 (energy 0.30 vs a target of 0.90). The labels matched, so it won, even though it's the opposite of hype.
- **The Ghost Genre profile was actually fine.** With no genre match it fell back to happy, mid-energy songs (Rooftop Lights, Sunrise City), which is a pretty sensible answer for someone who likes k-pop. Max score was only 2.41 though, which is a good hint that nothing really fit.
- **Does it "feel right"?** For Chill Lofi, yes, completely. Library Rain → Midnight Coding → Focus Flow → Spacewalk Thoughts → Coffee Shop Stories is a list I'd actually study to. For Default Pop/Happy, mostly, but I'd swap Heartbreak Neon out for Rooftop Lights.

### Comparing profiles (pairwise)

- **Default Pop/Happy vs High-Energy Pop:** Same genre, so the same 3 pop songs show up in both, but the order flips. Happy pop puts Sunrise City (happy, 0.82) first, while High-Energy Pop puts Gym Hero (intense, 0.93) first. That makes sense: the only things that changed were mood and energy, and Gym Hero matches both of the new ones.
- **Default Pop/Happy vs Chill Lofi:** Zero overlap. The pop list is all 0.6–0.9 energy, the lofi list is all under 0.45 energy and highly acoustic. This is the clearest proof the energy score is working, since the two users sit on opposite ends of the scale.
- **Default Pop/Happy vs Deep Intense Rock:** Only Gym Hero and Sunrise City overlap, and they're there for different reasons. For pop they get the genre bonus; for rock they only get energy points. The rock user only has one rock song, so after Storm Runner the list is filled with other high-energy songs (pop, edm, metal).
- **High-Energy Pop vs Deep Intense Rock:** These are pretty similar users (intense, ~0.9 energy, not acoustic), and the lists show it. Both contain Gym Hero, Storm Runner, Pulse Reactor, and Sunrise City. The only real difference is which one gets the +2.0 genre bonus to take #1. This shows how much the genre label decides the top spot when two users want the same "vibe."
- **High-Energy Pop vs Chill Lofi:** Complete opposites and no overlap at all. High-energy pop gets non-acoustic songs above 0.8 energy, and chill lofi gets acoustic songs under 0.45.
- **Chill Lofi vs Deep Intense Rock:** Also no overlap. Lofi gets acoustic, quiet songs and rock gets loud, electric ones. The acoustic preference pushes these two even further apart than energy alone would.
- **Sad but Hyped vs Default Pop/Happy:** Both contain Heartbreak Neon but for different reasons: for the sad user it's a mood match, for the happy user it's a genre match. The sad user's list is otherwise mostly "random high-energy songs," which shows that once the one folk song is used up, energy takes over.
- **Acoustic Headbanger vs Deep Intense Rock:** Almost the same list (Pulse Reactor, Gym Hero, Storm Runner, Sunrise City), even though one says they love acoustic and one says they don't. Acoustic fit only added +0.01 to +0.09 for the headbanger because no loud acoustic songs exist. So the acoustic preference basically doesn't matter for this user.

### Experiment: weight shift (energy ×2, genre ×0.5)

I added an `energy_focused` mode that doubles energy (1.5 → 3.0) and halves genre (2.0 → 1.0), then reran every profile with `python -m src.main --mode energy_focused`. The math is still valid: max score goes from 5.0 to 5.5, and every component still can't go negative.

What changed:
- **Default Pop/Happy:** Rooftop Lights jumped from #4 to **#2**, passing Gym Hero and Heartbreak Neon. I think this is **more accurate**: it's a happy, 0.76-energy song, which is exactly what this user wanted.
- **High-Energy Pop:** Storm Runner (rock) jumped from #4 to #2 above Sunrise City. More accurate for a workout vibe, less accurate if you really only want pop.
- **Chill Lofi:** Spacewalk Thoughts (ambient/chill) passed Focus Flow (lofi/focused). Honestly a toss-up, both are good study songs.
- **Sad but Hyped:** The folk ballad still won, but only by 0.10 over Heartbreak Neon. The conflict is much more visible now.

Overall, the experiment made results **more vibe-based and less label-based**, which I think is better for most profiles. The downside is it also makes the "everything is high energy" cluster (Gym Hero, Pulse Reactor, Storm Runner) even stickier for anyone who wants high energy.

### Tests

`pytest` runs 7 tests: the 2 starter tests for the `Recommender` class, plus tests that `load_songs` converts numbers, `score_song` returns the right score and reasons, energy rewards closeness instead of magnitude, results are sorted, and the diversity penalty pushes a repeat artist down.

### Raw output: balanced mode, all profiles

```
Loaded songs: 20

================================================================
Profile: Default Pop/Happy   (mode: balanced)
Prefs:   {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
================================================================
1. Sunrise City by Neon Echo  [pop / happy]
   Score: 4.47
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.82 vs target 0.80 (+1.47)
2. Gym Hero by Max Pulse  [pop / intense]
   Score: 3.31
     - genre match (+2.0)
     - energy 0.93 vs target 0.80 (+1.30)
3. Heartbreak Neon by Neon Echo  [pop / sad]
   Score: 3.20
     - genre match (+2.0)
     - energy 0.60 vs target 0.80 (+1.20)
4. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 2.44
     - mood match (+1.0)
     - energy 0.76 vs target 0.80 (+1.44)
5. Concrete Crown by Lyric Vault  [hip hop / confident]
   Score: 1.47
     - energy 0.78 vs target 0.80 (+1.47)

================================================================
Profile: High-Energy Pop   (mode: balanced)
Prefs:   {'genre': 'pop', 'mood': 'intense', 'energy': 0.95, 'likes_acoustic': False}
================================================================
1. Gym Hero by Max Pulse  [pop / intense]
   Score: 4.95
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.93 vs target 0.95 (+1.47)
     - non-acoustic fit (+0.47)
2. Sunrise City by Neon Echo  [pop / happy]
   Score: 3.71
     - genre match (+2.0)
     - energy 0.82 vs target 0.95 (+1.30)
     - non-acoustic fit (+0.41)
3. Heartbreak Neon by Neon Echo  [pop / sad]
   Score: 3.35
     - genre match (+2.0)
     - energy 0.60 vs target 0.95 (+0.98)
     - non-acoustic fit (+0.38)
4. Storm Runner by Voltline  [rock / intense]
   Score: 2.89
     - mood match (+1.0)
     - energy 0.91 vs target 0.95 (+1.44)
     - non-acoustic fit (+0.45)
5. Pulse Reactor by DJ Kinetix  [edm / euphoric]
   Score: 1.98
     - energy 0.95 vs target 0.95 (+1.50)
     - non-acoustic fit (+0.48)

================================================================
Profile: Chill Lofi   (mode: balanced)
Prefs:   {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'likes_acoustic': True}
================================================================
1. Library Rain by Paper Lanterns  [lofi / chill]
   Score: 4.93
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.35 vs target 0.35 (+1.50)
     - acoustic fit (+0.43)
2. Midnight Coding by LoRoom  [lofi / chill]
   Score: 4.75
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.42 vs target 0.35 (+1.40)
     - acoustic fit (+0.35)
3. Focus Flow by LoRoom  [lofi / focused]
   Score: 3.81
     - genre match (+2.0)
     - energy 0.40 vs target 0.35 (+1.42)
     - acoustic fit (+0.39)
4. Spacewalk Thoughts by Orbit Bloom  [ambient / chill]
   Score: 2.85
     - mood match (+1.0)
     - energy 0.28 vs target 0.35 (+1.40)
     - acoustic fit (+0.46)
5. Coffee Shop Stories by Slow Stereo  [jazz / relaxed]
   Score: 1.92
     - energy 0.37 vs target 0.35 (+1.47)
     - acoustic fit (+0.45)

================================================================
Profile: Deep Intense Rock   (mode: balanced)
Prefs:   {'genre': 'rock', 'mood': 'intense', 'energy': 0.9, 'likes_acoustic': False}
================================================================
1. Storm Runner by Voltline  [rock / intense]
   Score: 4.93
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.91 vs target 0.90 (+1.48)
     - non-acoustic fit (+0.45)
2. Gym Hero by Max Pulse  [pop / intense]
   Score: 2.93
     - mood match (+1.0)
     - energy 0.93 vs target 0.90 (+1.46)
     - non-acoustic fit (+0.47)
3. Pulse Reactor by DJ Kinetix  [edm / euphoric]
   Score: 1.91
     - energy 0.95 vs target 0.90 (+1.43)
     - non-acoustic fit (+0.48)
4. Iron Cathedral by Black Anvil  [metal / angry]
   Score: 1.88
     - energy 0.97 vs target 0.90 (+1.40)
     - non-acoustic fit (+0.48)
5. Sunrise City by Neon Echo  [pop / happy]
   Score: 1.79
     - energy 0.82 vs target 0.90 (+1.38)
     - non-acoustic fit (+0.41)

================================================================
Profile: Sad but Hyped   (mode: balanced)
Prefs:   {'genre': 'folk', 'mood': 'sad', 'energy': 0.9}
================================================================
1. Rainy Window Letters by Hollow Pines  [folk / sad]
   Score: 3.60
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.30 vs target 0.90 (+0.60)
2. Heartbreak Neon by Neon Echo  [pop / sad]
   Score: 2.05
     - mood match (+1.0)
     - energy 0.60 vs target 0.90 (+1.05)
3. Storm Runner by Voltline  [rock / intense]
   Score: 1.49
     - energy 0.91 vs target 0.90 (+1.48)
4. Gym Hero by Max Pulse  [pop / intense]
   Score: 1.46
     - energy 0.93 vs target 0.90 (+1.46)
5. Pulse Reactor by DJ Kinetix  [edm / euphoric]
   Score: 1.43
     - energy 0.95 vs target 0.90 (+1.43)

================================================================
Profile: Ghost Genre   (mode: balanced)
Prefs:   {'genre': 'k-pop', 'mood': 'happy', 'energy': 0.7}
================================================================
1. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 2.41
     - mood match (+1.0)
     - energy 0.76 vs target 0.70 (+1.41)
2. Sunrise City by Neon Echo  [pop / happy]
   Score: 2.32
     - mood match (+1.0)
     - energy 0.82 vs target 0.70 (+1.32)
3. Night Drive Loop by Neon Echo  [synthwave / moody]
   Score: 1.43
     - energy 0.75 vs target 0.70 (+1.42)
4. Concrete Crown by Lyric Vault  [hip hop / confident]
   Score: 1.38
     - energy 0.78 vs target 0.70 (+1.38)
5. Heartbreak Neon by Neon Echo  [pop / sad]
   Score: 1.35
     - energy 0.60 vs target 0.70 (+1.35)

================================================================
Profile: Acoustic Headbanger   (mode: balanced)
Prefs:   {'genre': 'metal', 'mood': 'angry', 'energy': 0.95, 'likes_acoustic': True}
================================================================
1. Iron Cathedral by Black Anvil  [metal / angry]
   Score: 4.49
     - genre match (+2.0)
     - mood match (+1.0)
     - energy 0.97 vs target 0.95 (+1.47)
     - acoustic fit (+0.01)
2. Pulse Reactor by DJ Kinetix  [edm / euphoric]
   Score: 1.52
     - energy 0.95 vs target 0.95 (+1.50)
     - acoustic fit (+0.02)
3. Gym Hero by Max Pulse  [pop / intense]
   Score: 1.50
     - energy 0.93 vs target 0.95 (+1.47)
     - acoustic fit (+0.03)
4. Storm Runner by Voltline  [rock / intense]
   Score: 1.49
     - energy 0.91 vs target 0.95 (+1.44)
     - acoustic fit (+0.05)
5. Sunrise City by Neon Echo  [pop / happy]
   Score: 1.40
     - energy 0.82 vs target 0.95 (+1.30)
     - acoustic fit (+0.09)
```

### Raw output: energy_focused experiment, all profiles

```
Loaded songs: 20

================================================================
Profile: Default Pop/Happy   (mode: energy_focused)
Prefs:   {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
================================================================
1. Sunrise City by Neon Echo  [pop / happy]
   Score: 4.94
     - genre match (+1.0)
     - mood match (+1.0)
     - energy 0.82 vs target 0.80 (+2.94)
2. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 3.88
     - mood match (+1.0)
     - energy 0.76 vs target 0.80 (+2.88)
3. Gym Hero by Max Pulse  [pop / intense]
   Score: 3.61
     - genre match (+1.0)
     - energy 0.93 vs target 0.80 (+2.61)
4. Heartbreak Neon by Neon Echo  [pop / sad]
   Score: 3.40
     - genre match (+1.0)
     - energy 0.60 vs target 0.80 (+2.40)
5. Concrete Crown by Lyric Vault  [hip hop / confident]
   Score: 2.94
     - energy 0.78 vs target 0.80 (+2.94)

================================================================
Profile: High-Energy Pop   (mode: energy_focused)
Prefs:   {'genre': 'pop', 'mood': 'intense', 'energy': 0.95, 'likes_acoustic': False}
================================================================
1. Gym Hero by Max Pulse  [pop / intense]
   Score: 5.42
     - genre match (+1.0)
     - mood match (+1.0)
     - energy 0.93 vs target 0.95 (+2.94)
     - non-acoustic fit (+0.47)
2. Storm Runner by Voltline  [rock / intense]
   Score: 4.33
     - mood match (+1.0)
     - energy 0.91 vs target 0.95 (+2.88)
     - non-acoustic fit (+0.45)
3. Sunrise City by Neon Echo  [pop / happy]
   Score: 4.02
     - genre match (+1.0)
     - energy 0.82 vs target 0.95 (+2.61)
     - non-acoustic fit (+0.41)
4. Pulse Reactor by DJ Kinetix  [edm / euphoric]
   Score: 3.48
     - energy 0.95 vs target 0.95 (+3.00)
     - non-acoustic fit (+0.48)
5. Iron Cathedral by Black Anvil  [metal / angry]
   Score: 3.42
     - energy 0.97 vs target 0.95 (+2.94)
     - non-acoustic fit (+0.48)

================================================================
Profile: Chill Lofi   (mode: energy_focused)
Prefs:   {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35, 'likes_acoustic': True}
================================================================
1. Library Rain by Paper Lanterns  [lofi / chill]
   Score: 5.43
     - genre match (+1.0)
     - mood match (+1.0)
     - energy 0.35 vs target 0.35 (+3.00)
     - acoustic fit (+0.43)
2. Midnight Coding by LoRoom  [lofi / chill]
   Score: 5.14
     - genre match (+1.0)
     - mood match (+1.0)
     - energy 0.42 vs target 0.35 (+2.79)
     - acoustic fit (+0.35)
3. Spacewalk Thoughts by Orbit Bloom  [ambient / chill]
   Score: 4.25
     - mood match (+1.0)
     - energy 0.28 vs target 0.35 (+2.79)
     - acoustic fit (+0.46)
4. Focus Flow by LoRoom  [lofi / focused]
   Score: 4.24
     - genre match (+1.0)
     - energy 0.40 vs target 0.35 (+2.85)
     - acoustic fit (+0.39)
5. Coffee Shop Stories by Slow Stereo  [jazz / relaxed]
   Score: 3.38
     - energy 0.37 vs target 0.35 (+2.94)
     - acoustic fit (+0.45)

================================================================
Profile: Deep Intense Rock   (mode: energy_focused)
Prefs:   {'genre': 'rock', 'mood': 'intense', 'energy': 0.9, 'likes_acoustic': False}
================================================================
1. Storm Runner by Voltline  [rock / intense]
   Score: 5.42
     - genre match (+1.0)
     - mood match (+1.0)
     - energy 0.91 vs target 0.90 (+2.97)
     - non-acoustic fit (+0.45)
2. Gym Hero by Max Pulse  [pop / intense]
   Score: 4.38
     - mood match (+1.0)
     - energy 0.93 vs target 0.90 (+2.91)
     - non-acoustic fit (+0.47)
3. Pulse Reactor by DJ Kinetix  [edm / euphoric]
   Score: 3.33
     - energy 0.95 vs target 0.90 (+2.85)
     - non-acoustic fit (+0.48)
4. Iron Cathedral by Black Anvil  [metal / angry]
   Score: 3.27
     - energy 0.97 vs target 0.90 (+2.79)
     - non-acoustic fit (+0.48)
5. Sunrise City by Neon Echo  [pop / happy]
   Score: 3.17
     - energy 0.82 vs target 0.90 (+2.76)
     - non-acoustic fit (+0.41)

================================================================
Profile: Sad but Hyped   (mode: energy_focused)
Prefs:   {'genre': 'folk', 'mood': 'sad', 'energy': 0.9}
================================================================
1. Rainy Window Letters by Hollow Pines  [folk / sad]
   Score: 3.20
     - genre match (+1.0)
     - mood match (+1.0)
     - energy 0.30 vs target 0.90 (+1.20)
2. Heartbreak Neon by Neon Echo  [pop / sad]
   Score: 3.10
     - mood match (+1.0)
     - energy 0.60 vs target 0.90 (+2.10)
3. Storm Runner by Voltline  [rock / intense]
   Score: 2.97
     - energy 0.91 vs target 0.90 (+2.97)
4. Gym Hero by Max Pulse  [pop / intense]
   Score: 2.91
     - energy 0.93 vs target 0.90 (+2.91)
5. Pulse Reactor by DJ Kinetix  [edm / euphoric]
   Score: 2.85
     - energy 0.95 vs target 0.90 (+2.85)

================================================================
Profile: Ghost Genre   (mode: energy_focused)
Prefs:   {'genre': 'k-pop', 'mood': 'happy', 'energy': 0.7}
================================================================
1. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 3.82
     - mood match (+1.0)
     - energy 0.76 vs target 0.70 (+2.82)
2. Sunrise City by Neon Echo  [pop / happy]
   Score: 3.64
     - mood match (+1.0)
     - energy 0.82 vs target 0.70 (+2.64)
3. Night Drive Loop by Neon Echo  [synthwave / moody]
   Score: 2.85
     - energy 0.75 vs target 0.70 (+2.85)
4. Concrete Crown by Lyric Vault  [hip hop / confident]
   Score: 2.76
     - energy 0.78 vs target 0.70 (+2.76)
5. Heartbreak Neon by Neon Echo  [pop / sad]
   Score: 2.70
     - energy 0.60 vs target 0.70 (+2.70)

================================================================
Profile: Acoustic Headbanger   (mode: energy_focused)
Prefs:   {'genre': 'metal', 'mood': 'angry', 'energy': 0.95, 'likes_acoustic': True}
================================================================
1. Iron Cathedral by Black Anvil  [metal / angry]
   Score: 4.96
     - genre match (+1.0)
     - mood match (+1.0)
     - energy 0.97 vs target 0.95 (+2.94)
     - acoustic fit (+0.01)
2. Pulse Reactor by DJ Kinetix  [edm / euphoric]
   Score: 3.02
     - energy 0.95 vs target 0.95 (+3.00)
     - acoustic fit (+0.02)
3. Gym Hero by Max Pulse  [pop / intense]
   Score: 2.96
     - energy 0.93 vs target 0.95 (+2.94)
     - acoustic fit (+0.03)
4. Storm Runner by Voltline  [rock / intense]
   Score: 2.93
     - energy 0.91 vs target 0.95 (+2.88)
     - acoustic fit (+0.05)
5. Sunrise City by Neon Echo  [pop / happy]
   Score: 2.70
     - energy 0.82 vs target 0.95 (+2.61)
     - acoustic fit (+0.09)
```

---

## 8. Future Work

- **Fuzzy genre matching.** Give partial credit for related genres (pop ↔ indie pop, rock ↔ metal) using a small similarity table, so "indie pop" isn't treated as unrelated to "pop."
- **Let users have multiple favorites.** A list of genres/moods with their own weights would fit real people way better than a single favorite.
- **Use the features I'm ignoring.** Valence and danceability are already in the CSV. Valence especially could fix the "Sad but Hyped" problem, since it measures how positive a song sounds regardless of its mood label.
- **Flag bad fits.** If the top score is below some threshold, tell the user "nothing here really matches" instead of pretending.
- **More, balanced data.** At least 3–5 songs per genre so niche users aren't stuck with one match.

---

## 9. Personal Reflection

My biggest learning moment was seeing "Heartbreak Neon" beat "Rooftop Lights" for a happy pop user. I wrote that scoring rule myself and it seemed totally reasonable on paper, but one string label ("indie pop" vs "pop") was worth more than the entire vibe of the song. It made me realize that a lot of "bias" in recommenders isn't some deep evil thing, it's just a weight someone picked plus whatever data happened to be in the catalog.

AI tools helped a lot with the boring-but-necessary parts: writing the CSV loader, formatting the output, brainstorming adversarial profiles I wouldn't have thought of (the "Acoustic Headbanger" one was a good catch), and explaining `sorted()` vs `.sort()` (sorted returns a new list and leaves the original alone, `.sort()` changes the list in place and returns None). But I still had to double-check things. For example, one of the tests I had generated for the diversity penalty assumed it would *remove* repeat artists completely, which isn't what a soft penalty does, so the test failed and I had to rewrite it to check that the repeat artist moves *down* instead. I also had to sanity check the math on every weight change myself, because "it runs" doesn't mean "the numbers make sense."

What surprised me most is how much a dumb weighted sum *feels* like a real recommendation. The Chill Lofi list honestly looks like something Spotify would give me, and it's just addition. That's kind of the scary part too, because it means a system can feel smart while hiding pretty obvious biases. If I kept going, I'd add fuzzy genre matching, use valence to catch mood conflicts, and try a tiny version of collaborative filtering with a few fake users to see how different the results are from pure content-based scoring.
