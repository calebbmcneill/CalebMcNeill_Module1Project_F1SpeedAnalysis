""" Returns the cumulative time in pit stops for all drivers in a given Formula 1 race. """

import pandas as pd
from api_cache import get_cached

BASE_URL = "https://api.openf1.org/v1"

def get_pit_stop_times(year, location):
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

    pit_stop_data = []
    driver_data = []
    for session in sessions:
        session_key = session["session_key"]
        pit_stops_response = get_cached(
            f"{BASE_URL}/pit", params={"session_key": session_key}, timeout=60
        )
        pit_stops_response.raise_for_status()

        drivers_response = get_cached(
            f"{BASE_URL}/drivers", params={"session_key": session_key}, timeout=30
        )
        drivers_response.raise_for_status()
        drivers = {
            driver["driver_number"]: driver
            for driver in drivers_response.json()
        }

        for driver_number, driver in drivers.items():
            driver_data.append(
                {
                    "Session Key": session_key,
                    "Driver Number": driver_number,
                    "Driver": driver.get("full_name"),
                    "Team": driver.get("team_name"),
                }
            )

        for pit_stop in pit_stops_response.json():
            pit_stop_data.append(
                {
                    "Session Key": session_key,
                    "Driver Number": pit_stop["driver_number"],
                    "Lane Duration (s)": pit_stop["lane_duration"],
                }
            )

    drivers_df = pd.DataFrame(driver_data)
    pit_stops_df = pd.DataFrame(pit_stop_data)
    total_lane_time_df = (
        pit_stops_df.groupby(["Session Key", "Driver Number"], as_index=False)[
            "Lane Duration (s)"
        ]
        .sum()
    )
    return (
        drivers_df.merge(
            total_lane_time_df, on=["Session Key", "Driver Number"], how="left"
        )
        .fillna({"Lane Duration (s)": 0.0})
        .drop(columns="Session Key")
        .sort_values("Lane Duration (s)", ascending=False)
        .reset_index(drop=True)
    )

if __name__ == "__main__":
    year = int(input("Specify the Formula 1 year: "))
    location = input("Specify the race location: ")
    pit_stop_times_df = get_pit_stop_times(year, location)
    print(pit_stop_times_df.to_string(index=False))