"""
Miguel Antonio H. Germar, 2022
Main script for the College Applications Dashboard.
"""

import pandas as pd
import numpy as np
import streamlit as st

# For connecting to private Google Sheets file
from google.oauth2 import service_account
from gsheetsdb import connect

# Custom imports for app features
from app_home import feature_home
from app_overview import feature_overview
from app_breakdown import feature_breakdown

if __name__ == "__main__":

    emoji = ":school:"

    st.set_page_config(
        page_title = "ASHS College Apps Dashboard",
        page_icon = emoji,
        initial_sidebar_state = "expanded",
    )

    st.title(f"{emoji} ASHS College Apps Dashboard")

    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )
    conn = connect(credentials = credentials)

    # Dictionary containing sheet names and their respective URLs
    sheets_urls = st.secrets["private_gsheets_url"]

    @st.cache(suppress_st_warning = True, allow_output_mutation = True)
    def get_data():
        """Obtain data used by the app."""

        # This dictionary will contain both data sheets
        db = {}

        for sheet_name in sheets_urls:
            url = sheets_urls[sheet_name]

            # Query the Google Sheets file.
            query = f'SELECT * FROM "{url}"'

            rows = conn.execute(
                query,
                headers = 1,
            )

            # DataFrame from query
            df = pd.DataFrame(rows)

            db[sheet_name] = df

        db = pd.Series(db)

        # Cast columns to appropriate types, based on data dictionary
        for index, row in db.ddict.iterrows():
            db.main[row["var_name"]] = (
                db.main[row["var_name"]]
                .astype(row["primitive_type"])
            )

        # Merge colleges sheet into main sheet
        db.main = (
            db.main
            .merge(
                right = db.colleges,
                on = "name",
                how = "left",
            )
        )

        # Make new sheet with number of applications per student
        db["apps"] = (
            db.main
            .pivot_table(
                index = ["respondent_code", "college_type"],
                aggfunc = "size",
            )
            .reset_index(drop = False)
            .rename(columns = {0: "num_students"})
        )

        return db

    # Obtain data.
    db = get_data()

    with st.sidebar:
        page_names = {
            "page1": "Home Page",
            "page2": "Overview Charts",
            "page3": "Breakdown Charts",
        }

        # Radio buttons to select pages of the app
        feature = st.radio(
            "App Feature",
            options = page_names.keys(),
            format_func = lambda key: page_names[key],
        )

    if feature == "page1":
        feature_home()

    elif feature == "page2":
        feature_overview(db)

    elif feature == "page3":
        feature_breakdown(db)