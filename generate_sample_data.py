import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
start = pd.Timestamp("2025-01-01")
days = 90
n_songs = 150
songs = [f"Demo Track {i:03d}" for i in range(1, n_songs + 1)]
artists = [f"Demo Artist {(i-1)//3+1:03d}" for i in range(1, n_songs + 1)]
metadata = {}
active = {i: set() for i in range(n_songs)}
for i in range(n_songs):
    metadata[i] = {
        "popularity": float(np.clip(rng.normal(55, 18), 1, 100)),
        "duration_ms": int(rng.integers(150000, 260000)),
        "album_type": "Single" if i % 2 == 0 else "Album",
        "total_tracks": int(rng.integers(1, 16)),
        "is_explicit": bool(i % 5 == 0)
    }
    # Each track has one run; selected tracks receive one or two separated comeback runs.
    run_count = 1 + (i % 3 == 0) + (i % 11 == 0)
    starts = [int(rng.integers(0, 20))]
    for j in range(1, run_count):
        starts.append(int(rng.integers(25 + (j-1)*20, min(days-5, 45 + (j-1)*20))))
    for s in starts:
        length = int(rng.integers(4, 14))
        for d in range(s, min(days, s + length)):
            active[i].add(d)

rows = []
for d in range(days):
    present = [i for i in range(n_songs) if d in active[i]]
    if len(present) < 50:
        absent = [i for i in range(n_songs) if i not in present]
        fill = rng.choice(absent, size=50-len(present), replace=False).tolist()
        present.extend(fill)
    elif len(present) > 50:
        # Preserve active songs with more than one run where possible, but enforce Top 50 size.
        present = rng.choice(present, size=50, replace=False).tolist()
    # Rank using stable track strength plus daily noise.
    ranked = sorted(present, key=lambda i: (-(metadata[i]["popularity"] + rng.normal(0, 8))))
    for pos, i in enumerate(ranked, start=1):
        m = metadata[i]
        rows.append({
            "date": (start + pd.Timedelta(days=d)).date().isoformat(),
            "position": pos,
            "song": songs[i],
            "artist": artists[i],
            "popularity": round(float(np.clip(m["popularity"] + rng.normal(0, 2), 1, 100)), 1),
            "duration_ms": m["duration_ms"],
            "album_type": m["album_type"],
            "total_tracks": m["total_tracks"],
            "is_explicit": m["is_explicit"],
            "album_cover_url": ""
        })
df = pd.DataFrame(rows)
path = Path(__file__).parent / "data" / "sample_top50_daily.csv"
path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(path, index=False)
print(f"Wrote {len(df)} synthetic rows; daily row counts: {df.groupby('date').size().min()}–{df.groupby('date').size().max()}")
