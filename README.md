# Formula 1 Speed Analysis

**Duke University AIPI 510 | Module 1: Sourcing for Data Analytics**
Author: Caleb McNeill

This project uses the [OpenF1 API](https://openf1.org/) to collect, clean, and analyze Formula 1 race data from the 2023-2025 seasons. The analysis focuses on speed, race time, finishing position, and the relationship between these measures across drivers and circuits.

The repository includes the reproducible data-collection scripts, prepared CSV files, an exploratory analysis notebook, and a Streamlit blog that presents the findings for a general audience.

## Project Contents

| Path | Purpose |
| --- | --- |
| [`exploratory_data_analysis.ipynb`](exploratory_data_analysis.ipynb) | Exploratory analysis of the prepared season data |
| [`blog/blog_streamlit.py`](blog/blog_streamlit.py) | Streamlit presentation of the analysis |
| [`OpenF1/`](OpenF1/) | OpenF1 API collection and data-processing scripts |
| [`FastF1/`](FastF1/) | Experimental telemetry-based distance analysis |
| [`data/`](data/) | Provided and generated CSV datasets |
| [`docs/project_works_cited_APA.docx`](docs/project_works_cited_APA.docx) | Project sources and works cited |

## Getting Started

### Requirements

- Python 3.10 or later
- Git
- Internet access for new OpenF1 API requests

### Installation

From PowerShell:

```powershell
git clone https://github.com/calebbmcneill/CalebMcNeill_Module1Project_F1SpeedAnalysis.git
cd CalebMcNeill_Module1Project_F1SpeedAnalysis
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The existing CSV files can be explored without making API requests. API access is only required when collecting new season or race data.

## Reproduce the Data Pipeline

### Collect a season

Run from the repository root after activating the virtual environment:

```powershell
cd OpenF1
python main_season.py
```

When prompted, enter a season year such as `2023`, `2024`, or `2025`. The script saves a timestamped season CSV in `data/`.

### Combine season files

```powershell
python csv_compile.py
```

This combines matching season CSV files for 2023-2025 into a timestamped analysis-ready dataset without making additional API requests.

### Run the exploratory analysis

Open [`exploratory_data_analysis.ipynb`](exploratory_data_analysis.ipynb) in VS Code or Jupyter and select the Python interpreter from `.venv` as the notebook kernel.

### Run the Streamlit blog

From the repository root:

```powershell
streamlit run blog/blog_streamlit.py
```
Deployed URL: https://calebmcneillmodule1projectf1speedanalysis-ecwqcyixcgfcheuvr6nn.streamlit.app/

### Run the experimental distance analysis

From the repository root, open `FastF1/distance_session.py`, update the driver abbreviation values near the top of the file, and run:

```powershell
python FastF1/distance_session.py
```

## Data

The prepared season datasets contain race-level driver records with fields for driver identity, team, finishing position, adjusted overall time, speed-trap measurements, session, circuit location, country, and year. The repository also includes a Spa-Francorchamps race dataset for targeted race-level analysis.

Files in `data/` are timestamped outputs so that collection runs remain traceable. The combined 2023-2025 file is used by the Streamlit application.

Included datasets:

- `f1_season_data_2023_2025_combined_20260922_114820_066553.csv`: combined 2023-2025 season dataset used by the Streamlit application.
- `f1_season_data_2023_20260921_200010_944377.csv`: 2023 season data.
- `f1_season_data_2024_20260921_200415_623623.csv`: 2024 season data.
- `f1_season_data_2025_20260921_200842_535953.csv`: 2025 season data.
- `f1_race_data_2023_2026_Spa-Francorchamps_20260920_201101_596143.csv`: targeted Spa-Francorchamps race data.

## OpenF1 Processing Scripts

- `api_cache.py`: caches API responses to reduce redundant requests.
- `main_race.py`: retrieves and assembles a single race-session dataset.
- `main_season.py`: collects race data for a selected season.
- `csv_compile.py`: combines existing season CSV files.
- `avg_speed_split.py`: calculates average speed metrics by segment.
- `max_speed_split.py`: captures maximum speed measurements.
- `overall_time.py`: computes normalized race-time measures.
- `positions.py`: organizes finishing positions and race outcomes.

## Notes

- `OpenF1/unused/` and `FastF1/unused/` contain exploratory files retained for reference and are not part of the primary workflow (not for grade).
- API responses and available session data may change over time. Timestamped CSV outputs preserve the data used for a particular analysis run.
- See [`docs/project_works_cited_APA.docx`](docs/project_works_cited_APA.docx) for the project's sources.

