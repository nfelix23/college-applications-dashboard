import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

def select_college_types(st_key):
    """Let the user select one or both college types."""

    st.markdown("Select college types to include.")

    options = ["local", "international"]
    set_selection = set()

    for option in options:
        checked = st.checkbox(
            option,
            value = True,
            key = f"{st_key} {option}"
        )

        if checked:
            set_selection.add(option)

    if len(set_selection) == 0:
        st.caption("Since no college types were selected, all colleges will be included.")
        set_selection.update(options)

    str_selection = " and ".join(list(set_selection))

    return str_selection, set_selection

def select_to_count(st_key):
    """Let the user select whether to count students or applications."""
    to_count = st.radio(
        "What to count",
        options = ["students", "applications"],
        key = st_key
    )
    return to_count

def make_perc_col(series):
    """Convert a numeric series to a string series with % at the end."""
    def add_perc_symbol(num):
        padded = "{:<02.2f}".format(num)
        result = f"{padded}%"

        return result

    result = series.apply(add_perc_symbol)

    return result