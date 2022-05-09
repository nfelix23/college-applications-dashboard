import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

def select_college_types(st_key):
    """Let the user select one or both college types."""

    options_lists = {
        "local": ["local"],
        "international": ["international"],
        "local and international": ["local", "international"],
    }

    str_selection = st.radio(
        label = "Select college types to include.",
        options = options_lists,
        key = f"select_college_types {st_key}",
    )

    set_selection = set(options_lists[str_selection])

    return str_selection, set_selection

def add_perc_symbol(num):
    """Convert a number to a string with two decimals places and a percent symbol."""

    padded = "{:<02.2f}".format(num)
    result = f"{padded}%"

    return result

def make_perc_col(series):
    """Convert a numeric series to a string series with % at the end."""

    result = series.apply(add_perc_symbol)

    return result

def chart_of_percentages(df, num_var_title, opt_var_title):
    source = alt.Chart(df)

    y_sort = alt.EncodingSortField("perc", order = "descending")

    bar = (
        source
        .mark_bar()
        .encode(
            x = alt.X("perc:Q", title = num_var_title),
            y = alt.Y("var_name:N", title = opt_var_title, sort = y_sort),
            color = alt.Color("option_type:N", title = "Option Type"),
            tooltip = [
                alt.Tooltip("long_name:N", title = "Option"),
                alt.Tooltip("perc_str:N", title = num_var_title),
            ],
        )
    )
    
    text = (
        source
        .mark_text(
            align = "right",
            baseline = "middle",
            dx = 20,
        )
        .encode(
            text = alt.Text("perc_str:N"),
            y = alt.Y("var_name:N", title = opt_var_title, sort = y_sort, axis = None),
        )
        .properties(width = 50)
    )
    chart = alt.hconcat(bar, text, spacing = 0)

    st.altair_chart(chart, use_container_width = True)

    return None