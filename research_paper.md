# Research Paper: K-Pop Chart Re-Entry and Comeback Momentum Intelligence

## 1. Abstract
This project proposes a reproducible analytical workflow for identifying repeated entries into a daily South Korean Top 50 playlist and comparing the momentum and observed retention of first entries versus re-entries. The dashboard combines chart rank, popularity scores, and content metadata to support exploratory release-strategy analysis. Any conclusions must be calculated from the licensed, verified source dataset; bundled sample data is synthetic and supports software testing only.

## 2. Research questions
1. Which song–artist pairs have the highest number of detected re-entry episodes?
2. Do re-entry episodes show stronger rank improvement or popularity change than first entries?
3. How long does a song remain visible after a comeback episode?
4. Are comeback metrics associated with single/album classification, album size, song duration or explicit-content flag?
5. Can chart-based signals provide a useful *proxy* for fandom-driven engagement?

## 3. Data and validation
Expected fields: date, position, song, artist, popularity, duration_ms, album_type, total_tracks, is_explicit, and optionally album_cover_url.

Validation steps:
- Parse dates and numeric fields; reject invalid dates and ranks outside 1–50.
- Normalize whitespace and case for song–artist identifiers.
- Check whether each date contains exactly 50 rows.
- Check duplicate date–song–artist combinations.
- Inspect missing popularity and content metadata.
- Confirm the meaning, scale and update cadence of `popularity` with the data provider.
- Confirm that chart dates are complete before interpreting gaps as exits.

## 4. Operational definitions
- **Song identity:** normalized song title + artist string. Collaborations, remixes, transliterations and title variants may require a curated mapping table.
- **Episode:** a run of observed chart appearances separated from the previous appearance by a gap exceeding the chosen threshold.
- **Re-entry frequency:** count of episodes after the first observed episode.
- **Rank improvement:** entry rank minus best rank in the selected post-entry window; positive values indicate improvement.
- **Popularity change:** popularity at the end of the selected window minus popularity at the episode's first observed snapshot. Interpret only after confirming the score's scale and whether it is comparable over time.
- **Observed retention:** consecutive observed calendar dates with a chart appearance from the episode start. Missing source dates can bias this measure.
- **Momentum intensity score:** exploratory normalized composite combining rank improvement (up to 50 points) and popularity change (scaled and clipped to a 0–50 contribution). The implementation clips the total to 0–100. This score is a heuristic, not a validated or standard measure.
- **Fandom intensity proxy:** a composite interpretation of re-entry frequency, comeback momentum and retention. It must not be described as direct fandom measurement.

## 5. Methodology
1. Load and validate snapshots.
2. Normalize song–artist identifiers.
3. Sort each song's appearances by date.
4. Segment appearances into episodes using a configurable gap threshold.
5. Measure rank and popularity movement within a configurable post-entry window.
6. Estimate observed retention using the observed daily chart sequence.
7. Compare episode metrics by album type, album size, duration and explicit flag.
8. Present song-level results with clear caveats and exportable tables.

## 6. Analysis plan
For the real dataset, report:
- Number of dates, rows, unique songs and artists.
- Percentage of dates with exactly 50 records.
- Number and share of songs with at least one re-entry.
- Distribution of re-entry counts and gap lengths.
- First-entry versus re-entry rank and popularity movement.
- Median and mean retention, with sample sizes.
- Group differences by album type and explicit flag, including uncertainty intervals where feasible.
- Sensitivity analysis for alternative episode-gap thresholds and momentum windows.

Avoid relying only on averages. Use medians, distributions, sample sizes and confidence intervals. If inferential testing is appropriate, pre-register comparisons and check assumptions; correct for multiple comparisons when testing many attributes.

## 7. Limitations and bias
- Playlist rank is ordinal and does not reveal actual streams.
- A provider popularity score may be proprietary, delayed or not directly comparable between dates.
- Re-entry can be caused by promotions, virality, performances, anniversaries, algorithmic changes, data gaps or playlist methodology; it is not proof of fandom action.
- Single/album metadata may not reliably identify whether a track was promoted as a single.
- Explicit-content flag does not capture language, theme, censorship, platform restrictions or audience demographics.
- Artist popularity, release age, promotional schedule, playlist placement and concurrent events can confound comparisons.
- Observational associations do not establish causation.

## 8. Recommendations framework
Only after analysis of real data:
- Prioritize tracks with repeatable re-entry patterns for event-calendar monitoring.
- Compare post-comeback trajectories by artist and track type rather than relying on a single overall average.
- Track the first 7–14 days after a detected re-entry and evaluate whether rank and popularity improvements persist.
- Use sensitivity checks to distinguish genuine re-entries from missing data.
- Treat explicitness and album size as descriptive segmentation variables, not causal explanations.
- Combine playlist metrics with licensed streams, social engagement, release dates and event calendars where permitted.

## 9. Reproducibility
Record source name, collection date, timezone, data license, snapshot completeness, code version, parameter values and metric definitions. Keep raw data immutable and store cleaned outputs separately. Never publish synthetic sample-data results as market findings.

## 10. Conclusion
The project provides a practical dashboard for studying chart re-entry and momentum. Its value depends on complete snapshots, clear operational definitions and cautious interpretation. The dashboard is a decision-support prototype; business recommendations require validated source data and domain review.
