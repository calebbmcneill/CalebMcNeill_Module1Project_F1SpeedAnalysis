"""Returns the overall time for each driver in a given race as a list of integers in seconds."""

import pandas as pd
from api_cache import get_cached

BASE_URL = "https://api.openf1.org/v1"

def get_adjusted_overall_time(year, location):
    requested_location = location.strip().casefold()
    sessions_response = get_cached(
        f"{BASE_URL}/sessions", params={"year": year}, timeout=30
    )
    sessions_response.raise_for_status()
    sessions = [
        session
        for session in sessions_response.json()
        if (
            session["location"].casefold() == requested_location
            and session["session_name"] == "Race"
        )
    ]

    if not sessions:
        raise ValueError(f"No race sessions found for {location} in {year}.")

    adjusted_time_data = []
    for session in sessions:
        session_key = session["session_key"]
        session_result_response = get_cached(
            f"{BASE_URL}/session_result",
            params={"session_key": session_key},
            timeout=30,
        )
        session_result_response.raise_for_status()

        drivers_response = get_cached(
            f"{BASE_URL}/drivers", params={"session_key": session_key}, timeout=30
        )
        drivers_response.raise_for_status()
        drivers = {
            driver["driver_number"]: driver
            for driver in drivers_response.json()
        }

        pit_response = get_cached(
            f"{BASE_URL}/pit", params={"session_key": session_key}, timeout=60
        )
        if pit_response.status_code == 404:
            pit_rows = []
        else:
            pit_response.raise_for_status()
            pit_rows = [
                {
                    "Session Key": session_key,
                    "Driver Number": pit_stop["driver_number"],
                    "Lane Duration (s)": pit_stop["lane_duration"],
                }
                for pit_stop in pit_response.json()
            ]
        pit_df = pd.DataFrame(pit_rows)
        if pit_df.empty:
            lane_duration_by_driver = pd.DataFrame(
                columns=["Session Key", "Driver Number", "Lane Duration (s)"]
            )
        else:
            lane_duration_by_driver = pit_df.groupby(
                ["Session Key", "Driver Number"], as_index=False
            )["Lane Duration (s)"].sum()

        for result in session_result_response.json():
            driver = drivers.get(result["driver_number"], {})
            driver_lane_duration = lane_duration_by_driver.loc[
                lane_duration_by_driver["Driver Number"]
                == result["driver_number"],
                "Lane Duration (s)",
            ]
            lane_duration = (
                driver_lane_duration.iloc[0]
                if not driver_lane_duration.empty
                else 0.0
            )
            overall_time = result["duration"]
            adjusted_time_data.append(
                {
                    "Session Key": session_key,
                    "Driver Number": result["driver_number"],
                    "Driver": driver.get("full_name"),
                    "Team": driver.get("team_name"),
                    "Overall Time (s)": overall_time,
                    "Lane Duration (s)": lane_duration,
                    "Adjusted Overall Time (s)": (
                        overall_time - lane_duration
                        if pd.notna(overall_time)
                        else pd.NA
                    ),
                }
            )

    return (
        pd.DataFrame(adjusted_time_data)
        .sort_values("Adjusted Overall Time (s)", na_position="last")
        .reset_index(drop=True)
    )


get_overall_time = get_adjusted_overall_time


if __name__ == "__main__":
    year = int(input("Specify the Formula 1 year: "))
    location = input("Specify the race location: ")
    overall_time_df = get_adjusted_overall_time(year, location)
    print(overall_time_df.to_string(index=False))