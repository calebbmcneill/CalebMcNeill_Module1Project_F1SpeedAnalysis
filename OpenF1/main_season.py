"""
AIPI 510 - Sourcing Data Analytics
Module 1 Project: F1 Speed Analysis
Author: Caleb McNeill

This script calls supplementary feature functions to retrieve and analyze Formula 1 race data, 
focusing on maximum speeds achieved by drivers during race sessions. It fetches data from the 
OpenF1 API, processes it using pandas, and outputs the results in a cumulative pandas dataframe 
format and csv file for further analysis.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from api_cache import get_cached
from main_race import get_compiled_race_data


BASE_URL = "https://api.openf1.org/v1"


def get_race_locations(year):
	response = get_cached(
		f"{BASE_URL}/sessions", params={"year": year}, timeout=30
	)
	response.raise_for_status()
	return list(
		dict.fromkeys(
			session["location"]
			for session in response.json()
			if session["session_name"] == "Race"
			and not session.get("is_cancelled", False)
		)
	)


def get_compiled_season_data(year):
	locations = get_race_locations(year)
	if not locations:
		raise ValueError(f"No race sessions found for {year}.")

	return pd.concat(
		[get_compiled_race_data(year, location) for location in locations],
		ignore_index=True,
	).sort_values(["Year", "Location", "Position", "Driver"], na_position="last").reset_index(
		drop=True
	)


def save_compiled_season_data(dataframe, year):
	data_directory = Path(__file__).resolve().parent.parent / "data"
	data_directory.mkdir(parents=True, exist_ok=True)
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
	output_path = data_directory / f"f1_season_data_{year}_{timestamp}.csv"
	file_number = 1
	while output_path.exists():
		output_path = data_directory / f"f1_season_data_{year}_{timestamp}_{file_number}.csv"
		file_number += 1

	dataframe.to_csv(output_path, index=False)
	return output_path


if __name__ == "__main__":
	year = int(input("Specify the Formula 1 Season year: "))
	season_df = get_compiled_season_data(year)
	print(season_df.to_string(index=False))
	output_path = save_compiled_season_data(season_df, year)
	print(f"Saved dataframe to: {output_path}")