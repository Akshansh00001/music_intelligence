# K-Pop Momentum Intelligence

A portfolio-ready Streamlit analytics project focused on South Korean Top 50 playlist re-entries, comeback momentum, retention, and content attributes.

## What's included
- `app.py` — interactive Streamlit dashboard with filters, KPIs, timelines, momentum charts, attribute comparisons, leaderboard and data-quality checks.
- `data/sample_top50_daily.csv` — clearly labelled synthetic sample data for testing the app.
- `generate_sample_data.py` — regenerates synthetic sample data.
- `research_paper.md` — research structure, metric definitions, limitations and recommendation framework.
- `executive_summary.md` — concise stakeholder-facing summary.
- `requirements.txt` — Python dependencies.

## Run locally
Use Python 3.11 or 3.12 recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Use real data
Upload a CSV with these required columns:
`date, position, song, artist, popularity, duration_ms, album_type, total_tracks, is_explicit`

`album_cover_url` is optional and currently not used in calculations. Dates should represent daily snapshots; `position` should be 1–50. `is_explicit` accepts true/false, 1/0, or yes/no.

## Important analytical assumptions
- A re-entry episode is detected when the gap between consecutive observed chart dates for a song–artist pair is greater than the sidebar threshold. Default: more than one day.
- If your data has missing snapshot dates, re-entry detection may create false positives. Check data quality first.
- Momentum score is an exploratory 0–100 index using rank improvement and popularity change within a selected time window. It is not an established industry KPI; document and validate weights before presenting conclusions.
- “Fandom intensity” is a proxy inferred from chart behavior, not a direct measurement of fandom activity, streams, votes or intent.
- Observed retention is based on consecutive observed chart dates, not proof of continuous real-world popularity.

## Suggested deployment
Streamlit Community Cloud: push this folder to a GitHub repository, then choose `app.py` as the app entrypoint and use `requirements.txt` for dependencies.

## Project integrity
Synthetic data is only for demonstrating functionality. Do not present synthetic outputs as findings about real K-Pop songs, Atlantic Recording Corporation, or South Korea's market.
