import argparse
import json

from config import JSON_FILE, SQL_FILE
from generator import Generator


# for only run type, we use the same logic as garmin_sync
def run_strava_sync(
    client_id,
    client_secret,
    refresh_token,
    sync_types: list = ["running"],
    only_run=False,
):
    try:
        generator = Generator(SQL_FILE)
        generator.set_strava_config(client_id, client_secret, refresh_token)
        
        # If no sync_types are specified and `only_run` is not set, default to 'running'
        if only_run or (len(sync_types) == 1 and sync_types[0] == "running"):
            sync_types = ["running"]

        # Pass sync_types to the generator (assuming `sync` can handle this parameter)
        generator.sync(sync_types)

        activities_list = generator.load()
        with open(JSON_FILE, "w") as f:
            json.dump(activities_list, f)
    except Exception as e:
        print(f"Error during Strava sync: {e}")
        # You may want to raise the exception or handle it more gracefully here


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("client_id", help="strava client id")
    parser.add_argument("client_secret", help="strava client secret")
    parser.add_argument("refresh_token", help="strava refresh token")
    parser.add_argument(
        "--only-run",
        dest="only_run",
        action="store_true",
        help="if is only for running",
    )
    parser.add_argument(
        "--sync-types",
        dest="sync_types",
        nargs="*",
        default=["running"],  # Default to "running" if no types are provided
        help="Types of activities to sync (e.g., running, cycling, etc.)",
    )

    options = parser.parse_args()
    run_strava_sync(
        options.client_id,
        options.client_secret,
        options.refresh_token,
        sync_types=options.sync_types,
        only_run=options.only_run,
    )
