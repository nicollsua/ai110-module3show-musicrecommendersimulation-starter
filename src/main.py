"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:
    python -m src.main
"""

try:
    from src.recommender import load_songs, recommend_songs
except ModuleNotFoundError:  # allows `python src/main.py` too
    from recommender import load_songs, recommend_songs


def print_recommendations(label: str, user_prefs: dict, recommendations: list) -> None:
    """Print a readable block of ranked recommendations with their reasons."""
    print("=" * 64)
    print(f"Profile: {label}")
    print(f"Prefs:   {user_prefs}")
    print("=" * 64)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  [{song['genre']} / {song['mood']}]")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split(", "):
            print(f"     - {reason}")
    print()


def main() -> None:
    """Load the catalog and print top 5 recommendations for the default profile."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations("Default Pop/Happy", user_prefs, recommendations)


if __name__ == "__main__":
    main()
