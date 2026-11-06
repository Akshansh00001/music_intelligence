import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="K-Pop Momentum Intelligence", page_icon="🎵", layout="wide")

REQUIRED = ["date", "position", "song", "artist", "popularity", "duration_ms",
            "album_type", "total_tracks", "is_explicit"]

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

def prepare_data(raw):
    df = raw.copy()
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in ["position", "popularity", "duration_ms", "total_tracks"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["song"] = df["song"].astype("string").str.strip()
    df["artist"] = df["artist"].astype("string").str.strip()
    df["album_type"] = df["album_type"].astype("string").str.strip().str.title()
    df["is_explicit"] = df["is_explicit"].astype(str).str.lower().map(
        {"true": True, "1": True, "yes": True, "false": False, "0": False, "no": False})
    df["song_artist_id"] = (df["song"].fillna("").str.lower() + " — " +
                            df["artist"].fillna("").str.lower())
    df["duration_min"] = df["duration_ms"] / 60000
    df = df.dropna(subset=["date", "position", "song", "artist"])
    df = df[df["position"].between(1, 50)]
    df = df.sort_values(["song_artist_id", "date", "position"])
    return df

def analyze(df, gap_days=1, comeback_window=7):
    # A song is considered re-entered when its observed chart dates have a gap
    # greater than gap_days between consecutive chart appearances.
    records = []
    for sid, g in df.groupby("song_artist_id", sort=False):
        g = g.sort_values("date")
        dates = sorted(g["date"].dt.normalize().unique())
        if not dates:
            continue
        date_set = set(dates)
        first_date = pd.Timestamp(dates[0])
        prev = None
        entry_no = 0
        for d in dates:
            d = pd.Timestamp(d)
            is_entry = prev is None or (d - prev).days > gap_days
            if is_entry:
                entry_no += 1
                gap = np.nan if prev is None else (d - prev).days
                episode = g[g["date"].dt.normalize() == d].copy()
                # Windowed momentum compares first chart-day rank with best rank
                # and popularity change in the following N calendar days.
                win = g[(g["date"].dt.normalize() >= d) &
                        (g["date"].dt.normalize() <= d + pd.Timedelta(days=comeback_window))]
                start = episode.sort_values("date").iloc[0]
                peak = win["position"].min() if len(win) else start["position"]
                pop_start = start["popularity"]
                pop_end = win.sort_values("date").iloc[-1]["popularity"] if len(win) else pop_start
                rank_jump = max(0.0, float(start["position"] - peak))
                pop_change = float(pop_end - pop_start) if pd.notna(pop_start) and pd.notna(pop_end) else 0.0
                # Score is transparent and bounded; rank improvement and popularity change
                # are normalized to avoid mixing raw scales.
                rank_component = min(rank_jump / 49, 1) * 50
                pop_component = np.clip(pop_change, -100, 100) / 2
                intensity = float(np.clip(rank_component + pop_component, 0, 100))
                later_dates = g[g["date"].dt.normalize() >= d]["date"].dt.normalize().drop_duplicates()
                retained = 0
                for day in pd.date_range(d, d + pd.Timedelta(days=365), freq="D"):
                    if day in date_set:
                        retained += 1
                    else:
                        break
                row = start.to_dict()
                row.update({
                    "episode_start": d, "episode_number": entry_no,
                    "is_reentry": entry_no > 1, "gap_days": gap,
                    "peak_rank_window": peak, "rank_jump": rank_jump,
                    "popularity_change_window": pop_change,
                    "retention_observed_days": retained,
                    "momentum_intensity_score": intensity
                })
                records.append(row)
            prev = d
    episodes = pd.DataFrame(records)
    return episodes

st.title("🎵 K-Pop Momentum Intelligence")
st.caption("Chart re-entry, comeback momentum and fandom-engagement proxy analytics for South Korea's Top 50 playlist.")
with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload daily Top 50 CSV", type=["csv"])
    st.markdown("Required fields: date, position, song, artist, popularity, duration_ms, album_type, total_tracks, is_explicit")
    gap_days = st.slider("Days between appearances to count as a new episode", 0, 7, 1)
    comeback_window = st.slider("Momentum measurement window (days)", 1, 14, 7)

if uploaded:
    try:
        raw = load_csv(uploaded)
        df = prepare_data(raw)
    except Exception as e:
        st.error(f"Could not prepare file: {e}")
        st.stop()
else:
    sample_path = Path(__file__).parent / "data" / "sample_top50_daily.csv"
    if sample_path.exists():
        df = prepare_data(pd.read_csv(sample_path))
        st.info("Showing illustrative synthetic sample data. Upload your real dataset for valid findings.")
    else:
        st.info("Upload a CSV to begin. A synthetic sample can be generated with `python generate_sample_data.py`.")
        st.stop()

if df.empty:
    st.warning("No valid chart rows remain after validation.")
    st.stop()

episodes = analyze(df, gap_days=gap_days, comeback_window=comeback_window)
if episodes.empty:
    st.warning("No song episodes could be calculated.")
    st.stop()

with st.sidebar:
    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    songs = sorted(df["song"].dropna().unique().tolist())
    selected_songs = st.multiselect("Song filter", songs, default=[])
    artists = sorted(df["artist"].dropna().unique().tolist())
    selected_artists = st.multiselect("Artist filter", artists, default=[])
    album_options = sorted(df["album_type"].dropna().unique().tolist())
    selected_album_types = st.multiselect("Album type", album_options, default=album_options)
    min_reentries = st.number_input("Minimum re-entries", min_value=0, max_value=100, value=0)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = df["date"].min(), df["date"].max()
filtered = df[(df["date"] >= start) & (df["date"] < end + pd.Timedelta(days=1))]
if selected_songs:
    filtered = filtered[filtered["song"].isin(selected_songs)]
if selected_artists:
    filtered = filtered[filtered["artist"].isin(selected_artists)]
if selected_album_types:
    filtered = filtered[filtered["album_type"].isin(selected_album_types)]
filtered_eps = episodes[(episodes["episode_start"] >= start) & (episodes["episode_start"] < end + pd.Timedelta(days=1))]
if selected_songs:
    filtered_eps = filtered_eps[filtered_eps["song"].isin(selected_songs)]
if selected_artists:
    filtered_eps = filtered_eps[filtered_eps["artist"].isin(selected_artists)]
if selected_album_types:
    filtered_eps = filtered_eps[filtered_eps["album_type"].isin(selected_album_types)]

reentry_counts = episodes.groupby("song_artist_id")["is_reentry"].sum().rename("reentry_count")
filtered_eps = filtered_eps.join(reentry_counts, on="song_artist_id")
filtered_eps["reentry_count"] = filtered_eps["reentry_count"].fillna(0).astype(int)
filtered_eps = filtered_eps[filtered_eps["reentry_count"] >= min_reentries]

total_days = filtered["date"].dt.normalize().nunique()
songs_count = filtered["song_artist_id"].nunique()
reentries = int(filtered_eps["is_reentry"].sum()) if not filtered_eps.empty else 0
avg_score = filtered_eps.loc[filtered_eps["is_reentry"], "momentum_intensity_score"].mean() if filtered_eps["is_reentry"].any() else 0
avg_retention = filtered_eps.loc[filtered_eps["is_reentry"], "retention_observed_days"].mean() if filtered_eps["is_reentry"].any() else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Songs in view", f"{songs_count:,}")
c2.metric("Detected re-entries", f"{reentries:,}")
c3.metric("Avg. comeback score", f"{avg_score:.1f}/100")
c4.metric("Avg. observed retention", f"{avg_retention:.1f} days")

tabs = st.tabs(["Overview", "Re-entry timeline", "Momentum", "Attributes", "Leaderboard", "Data quality"])
with tabs[0]:
    st.subheader("Chart activity over time")
    daily = filtered.groupby(filtered["date"].dt.date).agg(chart_rows=("song", "size"), mean_popularity=("popularity", "mean")).reset_index(names="date")
    if not daily.empty:
        fig = px.line(daily, x="date", y="chart_rows", title="Observed Top 50 rows per day")
        st.plotly_chart(fig, use_container_width=True)
        fig2 = px.line(daily, x="date", y="mean_popularity", title="Average popularity score over time")
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown("**Interpretation note:** playlist presence is an observed chart signal, not a direct measure of streams or fandom size.")

with tabs[1]:
    st.subheader("Re-entry episodes")
    if filtered_eps.empty:
        st.info("No episodes match the selected filters.")
    else:
        timeline = filtered_eps.copy()
        timeline["label"] = timeline["song"].astype(str) + " — " + timeline["artist"].astype(str)
        fig = px.scatter(timeline, x="episode_start", y="label", color="is_reentry",
                         size="momentum_intensity_score", hover_data=["episode_number", "gap_days", "peak_rank_window", "retention_observed_days"],
                         title="First entries and detected re-entries")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(timeline[["episode_start","song","artist","episode_number","is_reentry","gap_days","peak_rank_window","retention_observed_days"]].sort_values("episode_start", ascending=False), use_container_width=True)

with tabs[2]:
    st.subheader("Comeback momentum")
    comeback = filtered_eps[filtered_eps["is_reentry"]].copy()
    if comeback.empty:
        st.info("No re-entry episodes in the current selection.")
    else:
        fig = px.scatter(comeback, x="popularity_change_window", y="rank_jump", color="momentum_intensity_score",
                         size="retention_observed_days", hover_name="song",
                         hover_data=["artist","episode_start","gap_days","peak_rank_window"],
                         title=f"Popularity change vs. rank improvement (first {comeback_window} days)")
        st.plotly_chart(fig, use_container_width=True)
        fig2 = px.histogram(comeback, x="momentum_intensity_score", nbins=20, title="Comeback momentum score distribution")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Score is a transparent exploratory index, not an industry-standard metric. Validate weights against business outcomes before using for decisions.")

with tabs[3]:
    st.subheader("Content attributes and comeback behavior")
    attr = filtered_eps[filtered_eps["is_reentry"]].copy()
    if attr.empty:
        st.info("No comeback episodes available for attribute comparisons.")
    else:
        a, b = st.columns(2)
        with a:
            fig = px.box(attr, x="album_type", y="momentum_intensity_score", points="all", title="Momentum score by album type")
            st.plotly_chart(fig, use_container_width=True)
        with b:
            fig = px.box(attr, x="is_explicit", y="momentum_intensity_score", points="all", title="Momentum score: explicit vs clean")
            st.plotly_chart(fig, use_container_width=True)
        fig = px.scatter(attr, x="total_tracks", y="momentum_intensity_score", color="album_type",
                         hover_name="song", title="Album size vs. comeback momentum")
        st.plotly_chart(fig, use_container_width=True)
        fig = px.scatter(attr, x="duration_min", y="momentum_intensity_score", color="is_explicit",
                         hover_name="song", title="Song duration vs. comeback momentum")
        st.plotly_chart(fig, use_container_width=True)
        st.warning("These are associations, not causal effects. Control for artist popularity, release timing, playlist exposure and missing metadata before drawing conclusions.")

with tabs[4]:
    st.subheader("Fandom intensity proxy leaderboard")
    if filtered_eps.empty:
        st.info("No songs match the filters.")
    else:
        board = filtered_eps.groupby(["song_artist_id","song","artist"]).agg(
            reentry_count=("is_reentry","sum"),
            mean_comeback_score=("momentum_intensity_score", lambda s: s[filtered_eps.loc[s.index, "is_reentry"]].mean() if filtered_eps.loc[s.index, "is_reentry"].any() else 0),
            mean_retention_days=("retention_observed_days", "mean"),
            best_rank=("peak_rank_window","min"),
            median_gap_days=("gap_days","median")
        ).reset_index().sort_values(["reentry_count","mean_comeback_score"], ascending=False)
        st.dataframe(board.drop(columns=["song_artist_id"]).round(2), use_container_width=True)
        st.download_button("Download leaderboard CSV", board.to_csv(index=False).encode("utf-8"), "fandom_intensity_leaderboard.csv", "text/csv")

with tabs[5]:
    st.subheader("Data validation checks")
    daily_counts = df.groupby(df["date"].dt.date).size()
    bad_days = daily_counts[daily_counts != 50]
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows loaded", f"{len(df):,}")
    q2.metric("Unique chart dates", f"{df['date'].dt.normalize().nunique():,}")
    q3.metric("Dates with ≠50 rows", f"{len(bad_days):,}")
    q4.metric("Duplicate date-song pairs", f"{df.duplicated(['date','song_artist_id']).sum():,}")
    st.write("Missing values by field")
    st.dataframe(df.isna().sum().rename("missing_count").to_frame(), use_container_width=True)
    if len(bad_days):
        st.warning("Some days do not have exactly 50 rows. Confirm whether these reflect source gaps, duplicate records or a partial export.")
    st.write("Daily row counts")
    st.dataframe(daily_counts.rename("rows").reset_index(), use_container_width=True)

st.divider()
st.caption("K-Pop Momentum Intelligence • Built for analytical exploration. Verify source licensing, data definitions and score assumptions before external publication.")
