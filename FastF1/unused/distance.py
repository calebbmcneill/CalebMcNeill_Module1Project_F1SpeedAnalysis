"""Append FastF1 telemetry distance to the combined season CSV."""

from datetime import datetime
from pathlib import Path

import fastf1
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_ROOT / "data"
SOURCE_PATTERN = "f1_season_data_2023_2025_combined*.csv"


def _normalize(value):
    if pd.isna(value):
        return ""
    return " ".join(str(value).casefold().replace("-", " ").split())


def _get_event_name(year, location, country):
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    location_key = _normalize(location)
    country_key = _normalize(country)
    matches = schedule[schedule["Location"].map(_normalize).eq(location_key)]
    if matches.empty and country_key:
        matches = schedule[schedule["Country"].map(_normalize).eq(country_key)]
    if matches.empty:
        raise ValueError(f"No FastF1 event found for {year}, {location}, {country}.")
    return matches.iloc[0]["EventName"]


def _calculate_session_distances(session):
    session.load()
    distances = []
    for driver_number in session.laps["DriverNumber"].dropna().unique():
        driver_laps = session.laps.pick_drivers(str(driver_number))
        if "IsAccurate" in driver_laps.columns:
            driver_laps = driver_laps[driver_laps["IsAccurate"].fillna(False)]

        total_distance = 0.0
        for _, lap in driver_laps.iterrows():
            telemetry = lap.get_car_data().add_distance()
            if not telemetry.empty and "Distance" in telemetry:
                total_distance += telemetry["Distance"].iloc[-1]

        distances.append(
            {
                "Driver Number": int(driver_number),
                "Distance (km)": total_distance / 1000,
            }
        )
    return pd.DataFrame(distances)


def append_distances_to_csv(source_file=None, output_file=None):
    source_path = (
        Path(source_file)
        if source_file
        else sorted(DATA_DIRECTORY.glob(SOURCE_PATTERN), key=lambda path: path.stat().st_mtime)[-1]
    )
    if not source_path.is_absolute():
        source_path = DATA_DIRECTORY / source_path

    source_df = pd.read_csv(source_path)
    required_columns = {"Year", "Location", "Country", "Driver Number"}
    missing_columns = required_columns - set(source_df.columns)
    if missing_columns:
        raise ValueError(f"Source CSV is missing columns: {sorted(missing_columns)}")

    distance_frames = []
    session_cache = {}
    valid_source_df = source_df.dropna(
        subset=["Year", "Location", "Country", "Driver Number"]
    )
    for (year, location, country), _race_rows in valid_source_df.groupby(
        ["Year", "Location", "Country"]
    ):
        event_name = _get_event_name(int(year), location, country)
        session_key = (int(year), event_name)
        if session_key not in session_cache:
            session_cache[session_key] = fastf1.get_session(int(year), event_name, "R")
            session_cache[session_key].distance_df = _calculate_session_distances(
                session_cache[session_key]
            )

        distances = session_cache[session_key].distance_df.copy()
        distances["Year"] = int(year)
        distances["Location"] = location
        distances["Country"] = country
        distance_frames.append(distances)

    if distance_frames:
        distance_df = pd.concat(distance_frames, ignore_index=True)
    else:
        distance_df = pd.DataFrame(
            columns=["Year", "Location", "Country", "Driver Number", "Distance (km)"]
        )
    output_df = source_df.merge(
        distance_df,
        on=["Year", "Location", "Country", "Driver Number"],
        how="left",
    )

    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = DATA_DIRECTORY / (
            f"f1_season_data_2023_2025_with_distance_{timestamp}.csv"
        )
        file_number = 1
        while output_path.exists():
            output_path = DATA_DIRECTORY / (
                f"f1_season_data_2023_2025_with_distance_{timestamp}_{file_number}.csv"
            )
            file_number += 1
    else:
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = DATA_DIRECTORY / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_path, index=False)
    return output_df, output_path


if __name__ == "__main__":
    dataframe, output_path = append_distances_to_csv()
    print(f"Saved {len(dataframe)} rows with distance data to: {output_path}")