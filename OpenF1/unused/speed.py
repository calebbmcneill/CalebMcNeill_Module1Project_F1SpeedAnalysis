"""Print each driver's maximum speed in every Formula 1 session for a year."""

import requests
import pandas as pd

BASE_URL = "https://api.openf1.org/v1"
SPEED_COLUMNS = ["i1_speed", "i2_speed", "st_speed"]


def get_max_speeds(year, location):
    requested_location = location.strip().casefold()
    sessions_response = requests.get(
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

    lap_rows = []
    driver_rows = []
    for session in sessions:
        session_key = session["session_key"]

        drivers_response = requests.get(
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

        laps_response = requests.get(
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

    drivers_df = pd.DataFrame(driver_rows)
    speeds_df = pd.DataFrame(lap_rows)
    if drivers_df.empty:
        return pd.DataFrame(
            columns=[
                "Session",
                "Location",
                "Country",
                "Driver Number",
                "Driver",
                "Team",
                "Max Speed (km/h)",
            ]
        )

    print(f"Calculating maximum speeds for {len(drivers_df)} drivers in {len(sessions)} sessions...")
    print(speeds_df.head())
    
    speeds_df["Lap Max Speed (km/h)"] = speeds_df[SPEED_COLUMNS].max(axis=1)
    max_speeds_df = speeds_df.groupby(
        ["Session Key", "Driver Number"], as_index=False
    )["Lap Max Speed (km/h)"].max()
    max_speeds_df = max_speeds_df.rename(
        columns={"Lap Max Speed (km/h)": "Max Speed (km/h)"}
    )
    return (
        drivers_df.merge(
            max_speeds_df, on=["Session Key", "Driver Number"], how="left"
        )
        .drop(columns="Session Key")
        .sort_values(["Session", "Location", "Driver"])
        .reset_index(drop=True)
    )


year = int(input("Specify the Formula 1 year: "))
location = input("Specify the race location: ")
max_speed_df = get_max_speeds(year, location)
print(max_speed_df.to_string(index=False))
