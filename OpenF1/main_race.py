"""
AIPI 510 Sourcing Data Analytics
Module 1 Project: F1 Speed Analysis
Author: Caleb McNeill

This script retrieves and analyzes Formula 1 race data, focusing on maximum speeds achieved by drivers 
during race sessions. It fetches data from the OpenF1 API, processes it using pandas, and outputs the 
results in a cumulative pandas dataframe format and csv file for further analysis.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
from positions import get_finishing_positions
from overall_time import get_adjusted_overall_time
from max_speed_split import get_max_speed_split
from avg_speed_split import get_avg_speed_split


def get_compiled_race_data(year, location):
	finishing_positions_df = get_finishing_positions(year, location)
	overall_time_df = get_adjusted_overall_time(year, location)
	speed_split_df = get_max_speed_split(year, location)
	avg_speed_split_df = get_avg_speed_split(year, location)

	merge_columns = ["Driver Number", "Driver", "Team"]
	metadata_columns = merge_columns + ["Session", "Location", "Country"]
	metadata_df = speed_split_df[metadata_columns].drop_duplicates()
	compiled_df = finishing_positions_df.merge(
		overall_time_df.drop(columns=["Session Key"]),
		on=merge_columns,
		how="outer",
	)
	compiled_df = compiled_df.merge(
		speed_split_df.drop(
			columns=["Session Key", "Session", "Location", "Country"]
		),
		on=merge_columns,
		how="outer",
	)
	compiled_df = compiled_df.merge(
		avg_speed_split_df.drop(
			columns=["Session Key", "Session", "Location", "Country"]
		),
		on=merge_columns,
		how="outer",
	)
	compiled_df = compiled_df.merge(metadata_df, on=merge_columns, how="left")
	return (
		compiled_df.assign(Year=year)
		.sort_values(["Year", "Position", "Driver"], na_position="last")
		.reset_index(drop=True)
	)


def get_compiled_race_data_range(first_year, last_year, location):
	if first_year > last_year:
		raise ValueError("The first year must be less than or equal to the last year.")

	return pd.concat(
		[
			get_compiled_race_data(year, location)
			for year in range(first_year, last_year + 1)
		],
		ignore_index=True,
	)


def save_compiled_race_data(dataframe, first_year, last_year, location):
	required_time_columns = ["Overall Time (s)", "Adjusted Overall Time (s)"]
	missing_columns = [
		column for column in required_time_columns if column not in dataframe.columns
	]
	if missing_columns:
		raise ValueError(
			"Cannot export CSV; missing required columns: "
			+ ", ".join(missing_columns)
		)

	data_directory = Path(__file__).resolve().parent.parent / "data"
	data_directory.mkdir(parents=True, exist_ok=True)
	safe_location = "_".join(location.strip().split()) or "unknown_location"
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
	base_name = f"f1_race_data_{first_year}_{last_year}_{safe_location}_{timestamp}"
	output_path = data_directory / f"{base_name}.csv"
	file_number = 1
	while output_path.exists():
		output_path = data_directory / f"{base_name}_{file_number}.csv"
		file_number += 1

	dataframe.to_csv(output_path, index=False)
	return output_path


if __name__ == "__main__":
	first_year = int(input("Specify the first Formula 1 year: "))
	last_year = int(input("Specify the last Formula 1 year: "))
	location = input("Specify the race location: ")
	compiled_race_df = get_compiled_race_data_range(
		first_year, last_year, location
	)
	print(compiled_race_df.to_string(index=False))
	output_path = save_compiled_race_data(
		compiled_race_df, first_year, last_year, location
	)
	print(f"Saved dataframe to: {output_path}")

