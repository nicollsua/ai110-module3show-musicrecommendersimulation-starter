import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict

# Scoring modes (Strategy pattern): each mode is just a different set of weights
# that the same score_song "judge" uses. "balanced" is the original Algorithm Recipe.
SCORING_MODES: Dict[str, Dict[str, float]] = {
    "balanced":       {"genre": 2.0, "mood": 1.0, "energy": 1.5, "acoustic": 0.5},
    "genre_first":    {"genre": 3.0, "mood": 0.5, "energy": 1.0, "acoustic": 0.5},
    "mood_first":     {"genre": 1.0, "mood": 2.5, "energy": 1.5, "acoustic": 0.5},
    # Phase 4 experiment: energy doubled (1.5 -> 3.0), genre halved (2.0 -> 1.0)
    "energy_focused": {"genre": 1.0, "mood": 1.0, "energy": 3.0, "acoustic": 0.5},
}
DEFAULT_MODE = "balanced"

NUMERIC_INT_FIELDS = {"id"}
NUMERIC_FLOAT_FIELDS = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}


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


def _profile_to_prefs(user: UserProfile) -> Dict:
    """Convert a UserProfile dataclass into the prefs dict used by score_song."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
    }


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the catalog of Song objects."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for this user, best first."""
        prefs = _profile_to_prefs(user)
        ranked = sorted(self.songs, key=lambda s: score_song(prefs, asdict(s))[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a readable explanation of why a song got its score."""
        score, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV into a list of dicts with numeric fields converted."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key in NUMERIC_INT_FIELDS:
                row[key] = int(row[key])
            for key in NUMERIC_FLOAT_FIELDS:
                row[key] = float(row[key])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict, mode: str = DEFAULT_MODE) -> Tuple[float, List[str]]:
    """Score one song against user prefs and return (score, list of reasons)."""
    w = SCORING_MODES[mode]
    score = 0.0
    reasons = []

    genre = user_prefs.get("genre")
    if genre and song["genre"].lower() == genre.lower():
        score += w["genre"]
        reasons.append(f"genre match (+{w['genre']:.1f})")

    mood = user_prefs.get("mood")
    if mood and song["mood"].lower() == mood.lower():
        score += w["mood"]
        reasons.append(f"mood match (+{w['mood']:.1f})")

    target_energy = user_prefs.get("energy")
    if target_energy is not None:
        gap = abs(song["energy"] - target_energy)
        points = w["energy"] * (1 - gap)
        score += points
        reasons.append(f"energy {song['energy']:.2f} vs target {target_energy:.2f} (+{points:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        fit = song["acousticness"] if likes_acoustic else 1 - song["acousticness"]
        points = w["acoustic"] * fit
        score += points
        label = "acoustic" if likes_acoustic else "non-acoustic"
        reasons.append(f"{label} fit (+{points:.2f})")

    return round(score, 4), reasons


ARTIST_REPEAT_PENALTY = 1.0
GENRE_REPEAT_PENALTY = 0.5


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    mode: str = DEFAULT_MODE, diversity: bool = False) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort high to low, and return the top k as (song, score, explanation)."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        scored.append((song, score, reasons))
    scored = sorted(scored, key=lambda item: item[1], reverse=True)

    if not diversity:
        return [(song, score, ", ".join(reasons)) for song, score, reasons in scored[:k]]
    return _diverse_top_k(scored, k)


def _diverse_top_k(scored: List[Tuple[Dict, float, List[str]]], k: int) -> List[Tuple[Dict, float, str]]:
    """Greedily build the top k, penalizing songs whose artist or genre is already picked."""
    picked: List[Tuple[Dict, float, str]] = []
    remaining = list(scored)
    while remaining and len(picked) < k:
        artists = {song["artist"] for song, _, _ in picked}
        genres = {song["genre"] for song, _, _ in picked}
        best = None
        for song, score, reasons in remaining:
            adjusted, extra = score, []
            if song["artist"] in artists:
                adjusted -= ARTIST_REPEAT_PENALTY
                extra.append(f"diversity: artist already listed (-{ARTIST_REPEAT_PENALTY:.1f})")
            if song["genre"] in genres:
                adjusted -= GENRE_REPEAT_PENALTY
                extra.append(f"diversity: genre already listed (-{GENRE_REPEAT_PENALTY:.1f})")
            if best is None or adjusted > best[1]:
                best = (song, round(adjusted, 4), reasons + extra, (song, score, reasons))
        remaining.remove(best[3])
        picked.append((best[0], best[1], ", ".join(best[2])))
    return picked
