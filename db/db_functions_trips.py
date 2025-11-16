import sqlite3
import time
import streamlit as st
import pandas as pd
from datetime import date
DB_PATH = "db/users.db"

### Connecting to the database trips.db ###
def connect():
    return sqlite3.connect(DB_PATH)

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

def create_trip_users_table():
    conn = connect()
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_trips (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trip_ID INTEGER NOT NULL,
                        user_ID INTEGER NOT NULL,
                        UNIQUE (user_ID, trip_ID),
                        FOREIGN KEY(trip_ID) REFERENCES trips(trip_ID) ON DELETE CASCADE,
                        FOREIGN KEY(user_ID) REFERENCES users(user_ID) ON DELETE CASCADE
    )
    """)
    c.execute("CREATE INDEX IF NOT EXISTS ix_user_trips_trip ON user_trips(trip_ID);")
    c.execute("CREATE INDEX IF NOT EXISTS ix_user_trips_user ON user_trips(user_ID);")
    conn.commit()
    conn.close()

def add_trip(destination, start_date, end_date, occasion, user_ids):
    conn = connect()
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO trips (destination, start_date, end_date, occasion) VALUES (?, ?, ?, ?)",
            (destination, start_date, end_date, occasion)
        )
        if user_ids:
            trip_ID = c.lastrowid
            user_trips_list = [(trip_ID, user_ID) for user_ID in user_ids]
            c.executemany("INSERT OR IGNORE INTO user_trips (trip_ID, user_ID) VALUES (?, ?)", user_trips_list)
        conn.commit()
    except Exception as e:
        st.error(f"Unable to add the trip: {e}")
    finally:
        conn.close()

def del_trip(deleted_tripID: int):
    conn = connect()
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()
    try:
        c.execute(
            "DELETE FROM trips WHERE trip_ID = ?",
            (deleted_tripID,)
        )
        c.execute(
            "DELETE FROM user_trips WHERE trip_ID = ?",
            (deleted_tripID,)
        )
        conn.commit()
    except:
        st.error("Unable to delete the trip")
    finally:
        conn.close()

def create_trip_dropdown(title: str = "Create new trip"):
    with st.expander(title, expanded=False):
        with st.form("Create a trip", clear_on_submit=True):
            destination = st.text_input("Destination")
            start_date = st.date_input("Departure")
            end_date = st.date_input("Return")
            occasion = st.text_input("Occasion")

            conn = connect()
            user_df = pd.read_sql_query("SELECT user_ID, username FROM users ORDER BY username", conn)
            conn.close()

            options = list(zip(user_df["user_ID"], user_df["username"]))
            selected = st.multiselect("Assign users", options=options, format_func=lambda x: x[1])
            user_ids = [opt[0] for opt in selected]

            submitted = st.form_submit_button("invite")

        if submitted:
            if not destination:
                st.error("Destination must not be empty.")
            else:
                add_trip(destination, start_date, end_date, occasion, user_ids)
                st.success("Trip saved!")
                time.sleep(0.5)
                st.rerun()

def del_trip_dropdown(title: str = "Delete trip"):
    with st.expander(title, expanded=False):
        with st.form("Delete a trip", clear_on_submit=True):
            deleted_tripID = st.text_input("Delete trip")
            deleted = st.form_submit_button("delete")

            if deleted:
                if not deleted_tripID:
                    st.error("TRIP ID must be given.")
                else:
                    try:
                        deleted_tripID = int(deleted_tripID)
                    except ValueError:
                        st.error("TRIP ID has to be a integer")
                    else:
                        del_trip(deleted_tripID)
                        st.success("Trip deleted!")
                        time.sleep(0.5)
                        st.rerun()

def show_trip_table():
    conn = connect()
    df = pd.read_sql_query("SELECT * FROM trips", conn)
    conn.close()
    st.dataframe(df)

#########################################
def interactive_trip_table():
    conn = connect()
    trip_df = pd.read_sql_query("SELECT trip_ID, destination, start_date, end_date FROM trips ORDER BY start_date", conn)
    conn.close()

    options = [
    (int(row.trip_ID), f"{row.trip_ID} – {row.destination} ({row.start_date} → {row.end_date})")
    for _, row in trip_df.iterrows()
    ]

    selected = st.selectbox("Select a trip", options=options, format_func=lambda x: x[1])
    trip_id = selected[0]

    if selected:
        conn = connect()
        trip_detail = pd.read_sql_query("SELECT * FROM trips WHERE trip_ID = ?", conn, params=(trip_id,))
        participants = pd.read_sql_query("""
            SELECT u.username, u.email
            FROM users u
            JOIN user_trips ut ON ut.user_ID = u.user_ID
            WHERE ut.trip_ID = ?
            ORDER BY u.username
        """, conn, params=(trip_id,))
        conn.close()

        st.subheader("Trip details")
        st.dataframe(trip_detail)
        st.subheader("Participants")
        st.dataframe(participants)

def trip_list_view():
    conn = connect()
    trip_df = pd.read_sql_query("""
        SELECT trip_ID, destination, start_date, end_date, occasion
        FROM trips
        ORDER BY start_date
    """, conn)
    conn.close()

    if trip_df.empty:
        st.info("No trips available.")
        return

    # Schleife über alle Trips
    for _, row in trip_df.iterrows():
        with st.expander(
            f"#{row.trip_ID} — {row.destination} ({row.start_date} → {row.end_date})",
            expanded=False
        ):
            # Trip-Details anzeigen
            st.write("**Occasion:**", row.occasion)
            st.write("**Start:**", row.start_date)
            st.write("**End:**", row.end_date)

            # Teilnehmende laden
            conn = connect()
            participants = pd.read_sql_query("""
                SELECT u.username, u.email
                FROM users u
                JOIN user_trips ut ON ut.user_ID = u.user_ID
                WHERE ut.trip_ID = ?
                ORDER BY u.username
            """, conn, params=(row.trip_ID,))
            conn.close()

            st.markdown("**Participants:**")
            st.dataframe(participants, hide_index=True, use_container_width=True)

            # Optional: ein kleines Formular im Expander
            with st.form(f"edit_trip_{row.trip_ID}"):
                new_occasion = st.text_input("Edit occasion", value=row.occasion)
                submitted = st.form_submit_button("Save changes")
                if submitted:
                    conn = connect()
                    conn.execute(
                        "UPDATE trips SET occasion = ? WHERE trip_ID = ?",
                        (new_occasion, row.trip_ID)
                    )
                    conn.commit()
                    conn.close()
                    st.success("Trip updated!")
                    st.rerun()
            
            with st.form(f"edit_participants_{row.trip_ID}"):
                st.write("Manage participants")

                # 1️⃣ Alle User aus DB holen (für Auswahl)
                conn = connect()
                all_users_df = pd.read_sql_query("SELECT user_ID, username FROM users ORDER BY username", conn)
                conn.close()

                # 2️⃣ Aktuelle Teilnehmer dieses Trips holen
                conn = connect()
                current_df = pd.read_sql_query("""
                    SELECT u.user_ID, u.username
                    FROM users u
                    JOIN user_trips ut ON ut.user_ID = u.user_ID
                    WHERE ut.trip_ID = ?
                """, conn, params=(row.trip_ID,))
                conn.close()

                # 3️⃣ Multiselect mit allen Usern, vorausgewählt = aktuelle Teilnehmer
                selected_users = st.multiselect(
                    "Select participants",
                    options=all_users_df["user_ID"].tolist(),
                    default=current_df["user_ID"].tolist(),
                    format_func=lambda uid: all_users_df.loc[all_users_df["user_ID"] == uid, "username"].values[0]
                )

                # 4️⃣ Submit-Button
                update_participants = st.form_submit_button("Update participants")

                if update_participants:
                    conn = connect()
                    c = conn.cursor()

                    # Bestehende Zuordnungen löschen
                    c.execute("DELETE FROM user_trips WHERE trip_ID = ?", (row.trip_ID,))

                    # Neue Zuordnungen einfügen
                    user_trips_list = [(row.trip_ID, uid) for uid in selected_users]
                    c.executemany(
                        "INSERT OR IGNORE INTO user_trips (trip_ID, user_ID) VALUES (?, ?)",
                    user_trips_list
                    )

                    conn.commit()
                    conn.close()
                    st.success("Participants updated!")
                    st.rerun()

### Get trips for a specific user ###

def get_user_trips(user_id: int):
    conn = connect()
    query = """
    SELECT t.trip_ID,
           t.destination,
           t.start_date,
           t.end_date,
           t.occasion
    FROM trips t
    JOIN user_trips ut ON t.trip_ID = ut.trip_ID
    WHERE ut.user_ID = ?
    ORDER BY t.start_date
    """
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df


