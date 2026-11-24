from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---- Tests for the functional (dict-based) API ----
from src.recommender import load_songs, score_song, recommend_songs


def test_load_songs_converts_numeric_fields():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 20
    assert isinstance(songs[0]["id"], int)
    assert isinstance(songs[0]["energy"], float)
    assert isinstance(songs[0]["tempo_bpm"], float)


def test_score_song_returns_score_and_reasons():
    song = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}
    score, reasons = score_song({"genre": "pop", "mood": "happy", "energy": 0.8}, song)
    assert score == 4.5  # 2.0 genre + 1.0 mood + 1.5 perfect energy
    assert "genre match (+2.0)" in reasons
    assert "mood match (+1.0)" in reasons


def test_energy_rewards_closeness_not_magnitude():
    prefs = {"energy": 0.4}
    close, _ = score_song(prefs, {"genre": "x", "mood": "y", "energy": 0.45, "acousticness": 0.5})
    far, _ = score_song(prefs, {"genre": "x", "mood": "y", "energy": 0.95, "acousticness": 0.5})
    assert close > far


def test_recommend_songs_sorted_high_to_low():
    songs = load_songs("data/songs.csv")
    recs = recommend_songs({"genre": "lofi", "mood": "chill", "energy": 0.35}, songs, k=5)
    scores = [score for _, score, _ in recs]
    assert scores == sorted(scores, reverse=True)
    assert recs[0][0]["genre"] == "lofi"


def test_diversity_penalty_pushes_down_repeat_artists():
    songs = load_songs("data/songs.csv")
    prefs = {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}
    plain = [s["title"] for s, _, _ in recommend_songs(prefs, songs, k=5)]
    diverse = recommend_songs(prefs, songs, k=5, diversity=True)
    diverse_titles = [s["title"] for s, _, _ in diverse]
    # Focus Flow is a second LoRoom song, so it should drop below the ambient track
    assert plain.index("Focus Flow") < plain.index("Spacewalk Thoughts")
    assert diverse_titles.index("Focus Flow") > diverse_titles.index("Spacewalk Thoughts")
    focus = next(expl for s, _, expl in diverse if s["title"] == "Focus Flow")
    assert "artist already listed" in focus


def test_advanced_features_only_score_when_requested():
    songs = load_songs("data/songs.csv")
    song = next(s for s in songs if s["title"] == "Dusty Porch Swing")
    assert song["release_decade"] == 1990 and isinstance(song["popularity"], int)
    base, _ = score_song({"genre": "country", "mood": "nostalgic", "energy": 0.5}, song)
    full, reasons = score_song({"genre": "country", "mood": "nostalgic", "energy": 0.5,
                                "favorite_decade": 1990, "mood_tags": ["nostalgic", "warm"]}, song)
    assert full == round(base + 0.5 + 0.6, 4)  # decade match + 2 tags
    assert any("1990s match" in r for r in reasons)
