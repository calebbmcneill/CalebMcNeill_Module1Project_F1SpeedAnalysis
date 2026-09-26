""" Prints the distance an F1 driver has covered in a session."""

import fastf1 as ff1

def print_driver_distance(session, driver):
    """Prints the distance covered by a specific driver in a session."""
    telemetry = session.laps.pick_drivers(driver).get_telemetry()
    distance_meters = telemetry["Distance"].dropna().max()
    distance_kilometers = distance_meters / 1000
    print(f"Driver {driver} covered {distance_kilometers:.2f} km in the session.")

if __name__ == "__main__":
    # Example usage
    session = ff1.get_session(2026, 'Belgium', 'R')
    session.load()
    print_driver_distance(session, 'LEC')
    print_driver_distance(session, 'PIA')