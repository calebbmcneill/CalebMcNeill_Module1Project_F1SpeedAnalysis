"""Compile local season CSVs and append FastF1 telemetry distance."""

import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"
SEASON_FILE_PATTERN = re.compile(
    r"^f1_season_data_(\d{4})_\d{8}_\d{6}(?:_\d+)?\.csv$"
)


def compile_season_data(first_year=2023, last_year=2025, output_file=None):
    if first_year > last_year:
        raise ValueError("The first year must be less than or equal to the last year.")

    season_files = []
    for csv_file in DATA_DIRECTORY.glob("f1_season_data_*.csv"):
        match = SEASON_FILE_PATTERN.match(csv_file.name)
        if match and first_year <= int(match.group(1)) <= last_year:
            season_files.append(csv_file)

    if not season_files:
        raise FileNotFoundError(
            f"No season CSV files found for {first_year}-{last_year} in {DATA_DIRECTORY}."
        )

    season_files.sort(
        key=lambda path: int(SEASON_FILE_PATTERN.match(path.name).group(1))
    )
    compiled_df = pd.concat(
        [pd.read_csv(csv_file) for csv_file in season_files],
        ignore_index=True,
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    if output_file is None:
        output_path = DATA_DIRECTORY / (
            f"f1_season_data_{first_year}_{last_year}_with_distance_{timestamp}.csv"
        )
    else:
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = DATA_DIRECTORY / output_path

    if output_path.exists():
        output_path = output_path.with_name(
            f"{output_path.stem}_{timestamp}{output_path.suffix}"
        )

    combined_source_path = DATA_DIRECTORY / (
        f".f1_season_data_{first_year}_{last_year}_combined_source_{timestamp}.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    compiled_df.to_csv(combined_source_path, index=False)

    sys.path.insert(0, str(DATA_DIRECTORY.parent))
    from unused.FastF1.distance import append_distances_to_csv

    try:
        enriched_df, enriched_path = append_distances_to_csv(
            source_file=combined_source_path,
            output_file=output_path,
        )
    finally:
        combined_source_path.unlink(missing_ok=True)

    return enriched_df, enriched_path


if __name__ == "__main__":
    compiled_df, output_path = compile_season_data()
    print(f"Saved {len(compiled_df)} rows with distance data to: {output_path}")