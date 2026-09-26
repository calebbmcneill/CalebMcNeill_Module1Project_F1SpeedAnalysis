""" Returns the finishing positions for all drivers in a given Formula 1 race. """

import pandas as pd
from api_cache import get_cached

BASE_URL = "https://api.openf1.org/v1"

def get_finishing_positions(year, location):
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

    finishing_positions = []
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

        for result in session_result_response.json():
            driver = drivers.get(result["driver_number"], {})
            finishing_positions.append(
                {
                    "Session Key": session_key,
                    "Driver Number": result["driver_number"],
                    "Driver": driver.get("full_name"),
                    "Team": driver.get("team_name"),
                    "Position": result["position"],
                }
            )

    return pd.DataFrame(finishing_positions).sort_values("Position").reset_index(drop=True)

if __name__ == "__main__":
    year = int(input("Specify the Formula 1 year: "))
    location = input("Specify the race location: ")
    finishing_positions_df = get_finishing_positions(year, location)
    print(finishing_positions_df.to_string(index=False))