import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

def feature_breakdown(db):
    st.markdown("This page is under construction. Do not mind the contents.")

    st.write(db.main.head())

    bool_cols = db.ddict.loc[
        db.ddict["info_type"].isin(["interests", "characteristics"]),
        "var_name"
    ].tolist()

    college_stats = (
        db.main
        .pivot_table(
            index = ["name", "location", "college_type"],
            values = bool_cols,
            aggfunc = "sum",
        )
        .reset_index(drop = False)
    )

    st.write(college_stats)