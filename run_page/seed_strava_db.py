"""
Seed the 282 historical Strava activities into run_page/data.db so that the
daily Coros sync can accumulate on top of them (running_page merges sources via
data.db, not by appending files). This avoids any dependency on GPX files being
present in the CI checkout.

Run from the repo root:  python run_page/seed_strava_db.py
"""
import json
import os
import sys
from datetime import timedelta
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generator.db import init_db, update_or_create_activity, Activity  # noqa: E402
from generator import Generator  # noqa: E402
from config import SQL_FILE, JSON_FILE  # noqa: E402


def parse_duration(s):
    if s is None:
        return timedelta(0)
    if isinstance(s, (int, float)):
        return timedelta(seconds=float(s))
    s = str(s).strip()
    if not s:
        return timedelta(0)
    parts = [int(p) for p in s.split(":")]
    if len(parts) == 3:
        h, m, sec = parts
    elif len(parts) == 2:
        h, m, sec = 0, parts[0], parts[1]
    else:
        return timedelta(0)
    return timedelta(hours=h, minutes=m, seconds=sec)


class RunActivity:
    """Duck-typed activity matching what generator.db.update_or_create_activity expects."""

    def __init__(self, a):
        self.id = int(a["run_id"])
        self.name = a.get("name", "")
        self.distance = float(a.get("distance", 0) or 0)
        self.moving_time = parse_duration(a.get("moving_time"))
        self.elapsed_time = parse_duration(a.get("elapsed_time") or a.get("moving_time"))
        self.type = a.get("type", "Run")
        self.subtype = a.get("subtype", "") or ""
        self.start_date = a.get("start_date", "")
        self.start_date_local = a.get("start_date_local", "")
        self.location_country = a.get("location_country", "") or ""
        self.average_heartrate = a.get("average_heartrate")
        self.average_speed = float(a.get("average_speed", 0) or 0)
        eg = a.get("elevation_gain", 0) or a.get("total_elevation_gain", 0) or 0
        eg = float(eg)
        self.elevation_gain = eg
        self.total_elevation_gain = eg
        self.map = SimpleNamespace(summary_polyline=a.get("summary_polyline", "") or "")
        sl = a.get("start_latlng")
        if isinstance(sl, (list, tuple)) and len(sl) == 2:
            self.start_latlng = SimpleNamespace(lat=sl[0], lon=sl[1])
        else:
            self.start_latlng = None


def is_nike(a):
    if a.get("name") == "run from nike":
        return True
    rid = str(a.get("run_id", ""))
    return len(rid) == 13 and rid.isdigit()


def main():
    with open(JSON_FILE, encoding="utf-8") as f:
        data = json.load(f)

    strava = [a for a in data if not is_nike(a)]
    print(f"[seed] total in activities.json: {len(data)}, strava to seed: {len(strava)}")

    session = init_db(SQL_FILE)
    new = 0
    for a in strava:
        try:
            if update_or_create_activity(session, RunActivity(a)):
                new += 1
        except Exception as e:  # keep going if one record is malformed
            print(f"[seed] skip run_id={a.get('run_id')}: {e}")
    session.commit()

    total = session.query(Activity).count()
    print(f"[seed] inserted {new} new rows; data.db now holds {total} activities")

    # Regenerate activities.json straight from data.db (no GPX scan needed).
    acts = Generator(SQL_FILE).load()
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(acts, f)
    print(f"[seed] wrote activities.json with {len(acts)} activities from data.db")


if __name__ == "__main__":
    main()
