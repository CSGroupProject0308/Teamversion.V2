import sqlite3
import pandas as pd

DB_PATH = "db/users.db"

def connect():
    return sqlite3.connect(DB_PATH)

CITY_COORDS = {
    "St. Gallen":   {"lat": 47.4245, "lon": 9.3767},
    "Bern":         {"lat": 46.9481, "lon": 7.4474},
    "Zurich":       {"lat": 47.3769, "lon": 8.5417},
    "Basel":        {"lat": 47.5596, "lon": 7.5886},
    "Lucerne":      {"lat": 47.0502, "lon": 8.3093},
    "Lausanne":     {"lat": 46.5197, "lon": 6.6323},
    "Geneva":       {"lat": 46.2044, "lon": 6.1432},
}

import itertools

def generate_city_pairs(city_dict):
    cities = list(city_dict.keys())
    pairs = []

    for dep, arr in itertools.permutations(cities, 2):
        pairs.append({
            "departure_city": dep,
            "arrival_city": arr,
            "dep_lat": city_dict[dep]["lat"],
            "dep_lon": city_dict[dep]["lon"],
            "arr_lat": city_dict[arr]["lat"],
            "arr_lon": city_dict[arr]["lon"],
        })

    return pairs

ALL_CITY_ROUTES = generate_city_pairs(CITY_COORDS)

demo_trips = pd.DataFrame(ALL_CITY_ROUTES)


def get_user_trips(user_id: int) -> pd.DataFrame:
    """
    Returns all trips assigned to a given user (employee)
    using the user_trips mapping table.
    """
    conn = connect()

    query = """
        SELECT 
            t.trip_ID,
            t.destination,
            t.start_date,
            t.end_date,
            t.occasion
        FROM trips t
        JOIN user_trips ut ON t.trip_ID = ut.trip_ID
        WHERE ut.user_ID = ?
        ORDER BY t.start_date ASC
    """

    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df
