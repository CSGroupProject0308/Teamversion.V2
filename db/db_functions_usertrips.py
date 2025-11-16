##EMPLOYEE OVERVIEW PAGE FUNCTIONS####
import sqlite3
import sys
import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

DB_PATH = "db/users.db"
DB_PATH_TRIPS = "db/trips.db"
DB_PATH_USER_TRIPS = "db/user_trips.db"

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.db_functions_trips import get_user_trips, create_trip_table
from db.db_functions_users import edit_own_profile

import streamlit as st
from db.db_functions_users import edit_own_profile
st.set_page_config(page_title="User Dashboard", layout="wide")
st.title("User Dashboard")

""" Access control, so only users can access this page """
if "role" not in st.session_state or st.session_state["role"] != "User":
    st.error("Access denied. Please log in as User.")
    st.stop()


left, right = st.columns([4, 2], gap="large")
with left:
    st.subheader("Trip-Overview")


with right:
    edit_own_profile()


### Connecting to the database trips.db ###
def connect():
    return sqlite3.connect(DB_PATH, DB_PATH_TRIPS, DB_PATH_USER_TRIPS)

### Match database to signed in user ###

if "user_id" not in st.session_state:
    st.error("No employee is logged in.")
else:
    user_id = st.session_state["user_id"]
    user_trips_df = get_user_trips(user_id)

    if user_trips_df.empty:
        st.info("You have no trips assigned yet.")
    else:
        st.dataframe(user_trips_df, use_container_width=True)


### Create trips table for specific user###
def create_trip_table():
    conn = connect()
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS trips (
                        trip_ID INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
                        destination TEXT NOT NULL,
                        start_date TEXT,
                        end_date TEXT, 
                        occasion TEXT
    )
    """)
    conn.commit()
    conn.close()