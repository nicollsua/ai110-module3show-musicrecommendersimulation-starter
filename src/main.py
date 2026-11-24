"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:
    python -m src.main                       # all profiles, balanced mode
    python -m src.main --mode energy_focused # switch scoring strategy
    python -m src.main --profile "Chill Lofi"
"""

import argparse

try:
    from src.recommender import load_songs, recommend_songs, SCORING_MODES, DEFAULT_MODE
except ModuleNotFoundError:  # allows `python src/main.py` too
    from recommender import load_songs, recommend_songs, SCORING_MODES, DEFAULT_MODE


PROFILES = {
    # Core profiles
    "Default Pop/Happy":  {"genre": "pop", "mood": "happy", "energy": 0.8},
    "High-Energy Pop":    {"genre": "pop", "mood": "intense", "energy": 0.95, "likes_acoustic": False},
    "Chill Lofi":         {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock":  {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
    # Adversarial / edge-case profiles
    "Sad but Hyped":      {"genre": "folk", "mood": "sad", "energy": 0.9},
    "Ghost Genre":        {"genre": "k-pop", "mood": "happy", "energy": 0.7},
    "Acoustic Headbanger": {"genre": "metal", "mood": "angry", "energy": 0.95, "likes_acoustic": True},
}


def print_recommendations(label: str, user_prefs: dict, recommendations: list, mode: str) -> None:
    """Print a readable block of ranked recommendations with their reasons."""
    print("=" * 64)
    print(f"Profile: {label}   (mode: {mode})")
    print(f"Prefs:   {user_prefs}")
    print("=" * 64)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']} / {song['mood']}]")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split(", "):
            print(f"     - {reason}")
    print()


def main() -> None:
    """Load the catalog and print top 5 recommendations for each test profile."""
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=sorted(SCORING_MODES), default=DEFAULT_MODE)
    parser.add_argument("--profile", choices=list(PROFILES), help="run only one profile")
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    names = [args.profile] if args.profile else list(PROFILES)
    for name in names:
        prefs = PROFILES[name]
        recs = recommend_songs(prefs, songs, k=args.k, mode=args.mode)
        print_recommendations(name, prefs, recs, args.mode)


if __name__ == "__main__":
    main()
