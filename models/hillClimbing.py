"""
playlist_generator.py
--------------------------
Generates a smooth mood-transitioning playlist using
Hill Climbing + Simulated Annealing + Random Restart.

Input:  starting song name, target mood, playlist length
Output: a playlist that smoothly transitions from the starting song to the target mood

Data Model:
  Each song has independent [0, 1] intensity values per mood.
  A song can simultaneously have sad=0.9, happy=0.8 (all 1s in the extreme case).

Scoring (lower is better):
  1. Expected Deviation Score (weight: 0.75)
     Target mood intensity should linearly increase from the start song's value to 1.0.
     Larger deviations incur heavier penalties.
  2. Smoothness Score (weight: 0.25)
     Larger differences in non-target moods between adjacent songs incur penalties.

Algorithm Details:
  - Each step randomly replaces one song (never the starting song) and evaluates the score
  - Better scores are always accepted; worse scores are accepted with SA probability
    (high early on, low later)
  - The ending song's target mood intensity must be >= 0.9, otherwise completely rejected
  - Random Restart: when the global best hasn't improved for stagnation_limit consecutive
    steps, reset the playlist and temperature while preserving the global best solution
"""

import csv
import math
import random
import copy
from dataclasses import dataclass, field

# ============================================================
# Extensible mood list — add or remove moods here only
# ============================================================
MOODS = ["calm", "energetic", "happy", "sad", "dark", "romantic", "focus", "hype"]


# ============================================================
# Data Structure
# ============================================================
@dataclass
class Song:
    track_id: str
    track_name: str
    artists: str
    mood_values: dict[str, float] = field(default_factory=dict)  # mood -> [0,1] independent intensity

    def __repr__(self):
        top_mood = max(self.mood_values, key=self.mood_values.get) if self.mood_values else "?"
        top_val = self.mood_values.get(top_mood, 0)
        return f"'{self.track_name}' by {self.artists} (top: {top_mood}={top_val:.2f})"


# ============================================================
# Data Loading
# ============================================================
def load_dataset(csv_path: str) -> list[Song]:
    """Load song dataset from a CSV file."""
    songs = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mood_values = {}
            for m in MOODS:
                if m in row:
                    mood_values[m] = float(row[m])
            if not mood_values:
                continue
            song = Song(
                track_id=row.get("track_id", ""),
                track_name=row.get("track_name", ""),
                artists=row.get("artists", ""),
                mood_values=mood_values,
            )
            songs.append(song)
    return songs


def find_song_by_name(songs: list[Song], name: str) -> Song | None:
    """Fuzzy search for a song by name (case-insensitive, substring match)."""
    name_lower = name.lower().strip()
    # Prefer exact match
    for s in songs:
        if s.track_name.lower().strip() == name_lower:
            return s
    # Fall back to substring match
    for s in songs:
        if name_lower in s.track_name.lower():
            return s
    return None


# ============================================================
# Scoring Function
# ============================================================
def compute_score(
    playlist: list[Song],
    target_mood: str,
    weight_expected: float = 0.75,
    weight_smooth: float = 0.25,
) -> float:
    """
    Compute the total score of a playlist (lower is better).

    1. Expected Deviation: target mood should linearly increase from start value to 1.0
    2. Smoothness: non-target mood jumps between adjacent songs should be minimal
    """
    n = len(playlist)
    if n < 2:
        return 0.0

    # ---- 1. Expected Deviation Score ----
    start_val = playlist[0].mood_values.get(target_mood, 0.0)
    expected_deviation = 0.0
    for i in range(n):
        expected = start_val + (1.0 - start_val) * (i / (n - 1))
        actual = playlist[i].mood_values.get(target_mood, 0.0)
        expected_deviation += (actual - expected) ** 2
    expected_deviation /= n

    # ---- 2. Smoothness Score ----
    non_target_moods = [m for m in MOODS if m != target_mood]
    smoothness_penalty = 0.0
    for i in range(n - 1):
        for m in non_target_moods:
            diff = abs(playlist[i].mood_values.get(m, 0) - playlist[i + 1].mood_values.get(m, 0))
            smoothness_penalty += diff ** 2
    smoothness_penalty /= (n - 1) * max(len(non_target_moods), 1)

    return weight_expected * expected_deviation + weight_smooth * smoothness_penalty


# ============================================================
# Ending Song Constraint
# ============================================================
def is_valid_ending(song: Song, target_mood: str, threshold: float = 0.90) -> bool:
    """The ending song's target mood intensity must be >= threshold."""
    return song.mood_values.get(target_mood, 0.0) >= threshold


# ============================================================
# Random Playlist Initialization
# ============================================================
def random_playlist(
    songs: list[Song],
    start_song: Song,
    end_candidates: list[Song],
    playlist_length: int,
) -> list[Song]:
    """Generate a random initial playlist: fixed start, end from candidate pool, middle random."""
    playlist = [start_song]
    for _ in range(playlist_length - 2):
        playlist.append(random.choice(songs))
    playlist.append(random.choice(end_candidates))
    return playlist


# ============================================================
# Hill Climbing + Simulated Annealing + Random Restart
# ============================================================
def generate_playlist(
    songs: list[Song],
    start_song: Song,
    target_mood: str,
    playlist_length: int = 10,
    max_iterations: int = 20000,
    initial_temp: float = 1.0,
    cooling_rate: float = 0.9995,
    end_threshold: float = 0.90,
    weight_expected: float = 0.75,
    weight_smooth: float = 0.25,
    stagnation_limit: int = 3000,
    seed: int | None = None,
    verbose: bool = True,
) -> list[Song]:
    """
    Generate a playlist using Hill Climbing + Simulated Annealing + Random Restart.

    Random Restart Condition:
      Triggered when the global best score has not improved for stagnation_limit
      consecutive iterations. Resets the current playlist to a new random solution
      and resets temperature to initial_temp, while preserving the global best.
    """
    if seed is not None:
        random.seed(seed)

    if target_mood not in MOODS:
        raise ValueError(f"Unknown mood '{target_mood}', available: {MOODS}")

    # ---- End candidate pool ----
    end_candidates = [s for s in songs if is_valid_ending(s, target_mood, end_threshold)]
    if not end_candidates:
        print(f"Warning: no songs with {target_mood} >= {end_threshold}, "
              f"relaxing to {end_threshold * 0.7:.2f}...")
        end_threshold *= 0.7
        end_candidates = [s for s in songs if is_valid_ending(s, target_mood, end_threshold)]
    if not end_candidates:
        end_candidates = songs  # final fallback

    # ---- Initialization ----
    playlist = random_playlist(songs, start_song, end_candidates, playlist_length)
    current_score = compute_score(playlist, target_mood, weight_expected, weight_smooth)

    global_best_playlist = copy.deepcopy(playlist)
    global_best_score = current_score

    temperature = initial_temp
    accepted_worse = 0
    total_accepted = 0
    restarts = 0
    iters_since_improvement = 0  # iterations since last global best improvement

    if verbose:
        print(f"\nHill Climbing + Simulated Annealing + Random Restart")
        print(f"   Start song:       {start_song}")
        print(f"   Target mood:      {target_mood}")
        print(f"   Playlist length:  {playlist_length}")
        print(f"   Initial score:    {current_score:.6f}")
        print(f"   Weights:          expected_dev={weight_expected}, smoothness={weight_smooth}")
        print(f"   Annealing:        T0={initial_temp}, cooling_rate={cooling_rate}")
        print(f"   Restart:          after {stagnation_limit} steps without improvement")
        print()

    for iteration in range(max_iterations):

        # ========== Random Restart Check ==========
        if iters_since_improvement >= stagnation_limit:
            restarts += 1
            if verbose:
                print(f"   Restart #{restarts} @ iter {iteration} | "
                      f"global_best={global_best_score:.6f} | stagnant for {stagnation_limit} steps")

            # Re-randomize playlist, reset temperature
            playlist = random_playlist(songs, start_song, end_candidates, playlist_length)
            current_score = compute_score(playlist, target_mood, weight_expected, weight_smooth)
            temperature = initial_temp
            iters_since_improvement = 0
            continue

        # ========== Generate Neighbor ==========
        new_playlist = copy.deepcopy(playlist)
        pos = random.randint(1, playlist_length - 1)

        if pos == playlist_length - 1:
            # Ending position: pick from high-target-mood candidate pool only
            new_playlist[pos] = random.choice(end_candidates)
        else:
            # Middle position: pick from full song pool
            new_playlist[pos] = random.choice(songs)

        # Hard constraint on ending song
        if not is_valid_ending(new_playlist[-1], target_mood, end_threshold):
            iters_since_improvement += 1
            continue

        # ========== Score & Decision ==========
        new_score = compute_score(new_playlist, target_mood, weight_expected, weight_smooth)
        delta = new_score - current_score

        accept = False
        if delta <= 0:
            # Better or equal — always accept
            accept = True
        else:
            # Simulated Annealing: accept worse solution with decreasing probability
            if temperature > 1e-10:
                acceptance_prob = math.exp(-delta / temperature)
                if random.random() < acceptance_prob:
                    accept = True
                    accepted_worse += 1

        if accept:
            playlist = new_playlist
            current_score = new_score
            total_accepted += 1

            if current_score < global_best_score:
                global_best_playlist = copy.deepcopy(playlist)
                global_best_score = current_score
                iters_since_improvement = 0  # improved — reset counter
            else:
                iters_since_improvement += 1
        else:
            iters_since_improvement += 1

        # Cool down
        temperature *= cooling_rate

        # Logging
        if verbose and (iteration + 1) % 2000 == 0:
            print(f"   iter {iteration + 1:5d} | current={current_score:.6f} | "
                  f"global_best={global_best_score:.6f} | T={temperature:.6f} | "
                  f"restarts={restarts} | accepted_worse={accepted_worse}")

    if verbose:
        print(f"\nOptimization complete! Global best score: {global_best_score:.6f}")
        print(f"   Total iterations: {max_iterations}, accepted: {total_accepted}, "
              f"accepted_worse: {accepted_worse}, restarts: {restarts}")

    return global_best_playlist


# ============================================================
# Print Playlist
# ============================================================
def print_playlist(playlist: list[Song], target_mood: str):
    """Pretty-print the generated playlist."""
    n = len(playlist)
    start_val = playlist[0].mood_values.get(target_mood, 0.0)

    print(f"\n{'='*80}")
    print(f"  Generated Playlist (target mood: {target_mood})")
    print(f"{'='*80}")
    print(f"{'#':>3}  {'Song':<30} {'Artist':<20} {target_mood:>8} {'Expected':>8} {'Delta':>8}")
    print(f"{'-'*80}")

    for i, song in enumerate(playlist):
        expected = start_val + (1.0 - start_val) * (i / (n - 1)) if n > 1 else start_val
        actual = song.mood_values.get(target_mood, 0.0)
        deviation = actual - expected

        name = song.track_name[:28]
        artist = song.artists[:18]
        marker = " >>" if i == 0 else (" !!" if i == n - 1 else "   ")

        print(f"{i + 1:>3}{marker} {name:<30} {artist:<20} {actual:>8.4f} {expected:>8.4f} {deviation:>+8.4f}")

    print(f"{'='*80}")

    # Mood intensity overview
    print(f"\n  Mood Intensity Overview:")
    print(f"{'#':>3}  ", end="")
    for m in MOODS:
        label = f"*{m}*" if m == target_mood else m
        print(f"{label:>10}", end="")
    print()
    for i, song in enumerate(playlist):
        print(f"{i + 1:>3}  ", end="")
        for m in MOODS:
            print(f"{song.mood_values.get(m, 0):>10.4f}", end="")
        print()
    print()


# ============================================================
# Main
# ============================================================
def main():
    import sys
    import os

    # Dataset: same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(script_dir, "simulated_mood_dataset.csv")

    print("Loading dataset...")
    songs = load_dataset(dataset_path)
    print(f"   Loaded {len(songs)} songs, {len(MOODS)} moods: {MOODS}")

    # ---------- User Input ----------
    if len(sys.argv) >= 4:
        song_name = sys.argv[1]
        target_mood = sys.argv[2]
        playlist_length = int(sys.argv[3])
    else:
        song_name = input("\nEnter starting song name: ").strip()
        target_mood = input(f"Enter target mood {MOODS}: ").strip().lower()
        length_str = input("Enter playlist length (default 10): ").strip()
        playlist_length = int(length_str) if length_str else 10

    # Find song
    start_song = find_song_by_name(songs, song_name)
    if start_song is None:
        print(f"\nSong '{song_name}' not found.")
        print("   Sample available songs:")
        for s in random.sample(songs, min(10, len(songs))):
            print(f"     - {s.track_name} ({s.artists})")
        return

    print(f"\nFound starting song: {start_song}")

    # ---------- Generate Playlist ----------
    playlist = generate_playlist(
        songs=songs,
        start_song=start_song,
        target_mood=target_mood,
        playlist_length=playlist_length,
        max_iterations=20000,
        initial_temp=1.0,
        cooling_rate=0.9995,
        end_threshold=0.90,
        weight_expected=0.75,
        weight_smooth=0.25,
        stagnation_limit=3000,
        seed=42,
        verbose=True,
    )

    # ---------- Print Results ----------
    print_playlist(playlist, target_mood)

    final_score = compute_score(playlist, target_mood)
    print(f"  Final score: {final_score:.6f} (lower is better)")


if __name__ == "__main__":
    main()
