""" 
Returns the maximum recorded speeds at each sensor location 
for all drivers in a given Formula 1 race. 
"""

import pandas as pd
from api_cache import get_cached

BASE_URL = "https://api.openf1.org/v1"
SPEED_COLUMNS = ["i1_speed", "i2_speed", "st_speed"]

def get_max_speed_split(year, location):
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

    lap_rows = []
    driver_rows = []
    for session in sessions:
        session_key = session["session_key"]

        drivers_response = get_cached(
            f"{BASE_URL}/drivers", params={"session_key": session_key}, timeout=30
        )
        drivers_response.raise_for_status()
        drivers = drivers_response.json()
        for driver in drivers:
            driver_rows.append(
                {
                    "Session Key": session_key,
                    "Session": session["session_name"],
                    "Location": session["location"],
                    "Country": session["country_name"],
                    "Driver Number": driver["driver_number"],
                    "Driver": driver["full_name"],
                    "Team": driver["team_name"],
                }
            )

        laps_response = get_cached(
            f"{BASE_URL}/laps", params={"session_key": session_key}, timeout=60
        )
        laps_response.raise_for_status()
        lap_rows.extend(
            {
                "Session Key": session_key,
                "Driver Number": lap["driver_number"],
                **{column: lap.get(column) for column in SPEED_COLUMNS},
            }
            for lap in laps_response.json()
        )

    speeds_df = pd.DataFrame(lap_rows)
    drivers_df = pd.DataFrame(driver_rows)

    if speeds_df.empty or drivers_df.empty:
        raise ValueError(f"No speed data found for {location} in {year}.")

    max_speeds_df = speeds_df.groupby(
        ["Session Key", "Driver Number"], as_index=False
    )[SPEED_COLUMNS].max()
    max_speeds_df = max_speeds_df.rename(
        columns={
            "i1_speed": "Max i1 Speed (km/h)",
            "i2_speed": "Max i2 Speed (km/h)",
            "st_speed": "Max st Speed (km/h)",
        }
    )

    result_df = pd.merge(
        max_speeds_df, drivers_df, on=["Session Key", "Driver Number"], how="left"
    )

    return result_df.sort_values(["Session Key", "Driver"]).reset_index(drop=True)


if __name__ == "__main__":
    year = int(input("Specify the Formula 1 year: "))
    location = input("Specify the race location: ")
    max_speed_split_df = get_max_speed_split(year, location)
    print(max_speed_split_df.to_string(index=False))