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
    sheet_names_urls = {
        "main": st.secrets["private_gsheets_url_main"],
        "ddict": st.secrets["private_gsheets_url_data_dictionary"],
    }

    @st.cache(suppress_st_warning = True, allow_output_mutation = True)
    def get_data():
        """Obtain data used by the app."""

        # This dictionary will contain both data sheets
        db = {}

        for sheet_name in sheet_names_urls:
            url = sheet_names_urls[sheet_name]

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