import streamlit as st
import pandas as pd
from datetime import date
from db.db_functions_users import edit_own_profile
from db.db_functions_usertrips import get_user_trips

# --- Page setup ---
st.set_page_config(page_title="Employee Dashboard", layout="wide")
st.title("Employee Dashboard")

# --- Access control ---
if "role" not in st.session_state or st.session_state["role"] != "User":
    st.error("Access denied. Please log in as User.")
    st.stop()

# --- Layout ---
left, right = st.columns([4, 2], gap="large")

# --- LEFT COLUMN: Trip Overview ---
with left:
    st.subheader("Trip Overview")

    user_id = st.session_state.get("user_id", None)
    if user_id is None:
        st.warning("No user logged in. Please log in first.")
        st.stop()

    # Fetch trips from the DB
    trips = get_user_trips(user_id)

    if trips is None or trips.empty:
        st.info("You have no trips recorded yet.")
    else:
        trips["date_start"] = pd.to_datetime(trips["date_start"])
        trips["date_end"] = pd.to_datetime(trips["date_end"])

        # --- Calendar filter ---
        st.markdown("### 📅 Filter trips by date range")
        date_range = st.date_input(
            "Select a date or range",
            value=(date.today(), date.today()),
            help="Pick one day or a range to see matching trips",
        )

        # Handle single vs range selection
        if isinstance(date_range, tuple):
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range

        # Filter trips that overlap with the chosen date(s)
        mask = (trips["date_start"] <= end_date) & (trips["date_end"] >= start_date)
        filtered = trips.loc[mask].sort_values("date_start", ascending=False)

        if filtered.empty:
            st.warning("No trips found for the selected date(s).")
        else:
            st.dataframe(
                filtered[["destination", "date_start", "date_end", "budget", "status"]],
                use_container_width=True,
                hide_index=True
            )

# --- RIGHT COLUMN: Edit Profile ---
with right:
    edit_own_profile()
