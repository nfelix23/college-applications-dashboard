import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

import app_general_functions as agf

def feature_college(db):

    st.markdown("## College Info Charts")
    st.markdown("Select one college from the dropdown box below in order to see information and charts.")

    # Let user select a college
    selected_college_index = st.selectbox(
        "College Name",
        options = db.colleges.sort_values("name").index.tolist(),
        format_func = lambda idx: db.colleges.iloc[idx].loc["name"]
    )

    # Display college's location
    selected_row = db.colleges.iloc[selected_college_index]
    name = selected_row["name"]
    locn = selected_row["location"]

    st.markdown(f"Location: {locn}")

    # Display number of applicants
    num_applicants = (
        db.main
        .loc[db.main["name"] == name, :]
        .shape[0]
    )
    st.markdown(f"Number of respondents who applied: {num_applicants}")

    total_applicants = db.main.drop_duplicates("respondent_code", keep = "first").shape[0]
    perc_applicants = agf.add_perc_symbol(num_applicants / total_applicants * 100)
    st.markdown(f"Percentage of respondents who applied: {perc_applicants}")

    # Obtain statistics for that college
    one_college_stats = db.college_stats.loc[
        db.college_stats["name"] == name,
    ]

    # Function to make a chart for a particular info_type
    def college_info_bar_chart(info_type):
        """Take an info_type (interests or characteristics) and a representation (students or percentile). Display a bar chart."""
        col_set = set(
            db.ddict.loc[
                db.ddict["info_type"] == info_type,
                "var_name"
            ].to_list()
        )

        mask = one_college_stats["var_name"].isin(col_set)

        filtered_df = one_college_stats.loc[mask]

        filtered_df = filtered_df.merge(
            right = db.ddict[["var_name", "long_name", "is_other"]]
        )

        filtered_df["option_type"] = filtered_df["is_other"].apply(
            lambda x: "Other Option" if x else "Given Option"
        )

        filtered_df["perc"] = filtered_df["num_students"] / num_applicants * 100
        filtered_df["perc_str"] = agf.make_perc_col(filtered_df["perc"])

        agf.chart_of_percentages(
            filtered_df,
            num_var_title = "Percentage of Applicants",
            opt_var_title = info_type.title(),
        )

    # Display a chart for each of these info_type values
    checkbox_info_types = ["interests", "characteristics"]
    for info_type in checkbox_info_types:
        st.markdown(f"## {info_type.title()}")
        college_info_bar_chart(info_type)