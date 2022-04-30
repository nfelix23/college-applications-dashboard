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
            key = f"select_college_types {st_key} {option}"
        )

        if checked:
            set_selection.add(option)

    if len(set_selection) == 0:
        st.caption("Since no college types were selected, all colleges will be included.")
        set_selection.update(options)

    str_selection = " and ".join(list(set_selection))

    return str_selection, set_selection

def make_perc_col(series):
    """Convert a numeric series to a string series with % at the end."""
    def add_perc_symbol(num):
        padded = "{:<02.2f}".format(num)
        result = f"{padded}%"

        return result

    result = series.apply(add_perc_symbol)

    return result

def chart_checkbox(
    db,
    info_type, # str, whether interests or characteristics
    singular, # str, singular form of info_type, for grammar purposes
    intro, # str, the introductory text for the chart
    st_key, # str, string to put into key argument of streamlit widgets
    debug = False, # bool, whether or not to show the intermediary steps in data transformation
):

    # Display intro text
    st.markdown(intro)

    # Ask for college types
    str_coll_types, set_coll_types = select_college_types(st_key = f"chart_checkbox {st_key}")

    # Transform data
    apps_filtered = (
        db.apps
        .loc[
            db.apps["college_type"].isin(set_coll_types)
        ]
        .pivot_table(index = "respondent_code", values = "num_apps", aggfunc = "sum")
        .reset_index(drop = False)
    )

    main_filtered = (
        db.main
        .loc[
            db.main["college_type"].isin(set_coll_types)
        ]
    )

    reference_df = db.ddict.loc[
        db.ddict["info_type"] == info_type,
        ["var_name", "long_name", "is_other"]
    ]

    bool_cols = reference_df["var_name"].tolist()

    selection = ["index", "respondent_code"] + bool_cols

    main_filtered = main_filtered.loc[:, selection]
    
    scored_df = (
        main_filtered
        .pivot_table(
            index = ["respondent_code"],
            values = bool_cols,
            aggfunc = "sum",
        )
        .reset_index(drop = False)
    )

    raw_scores = (
        scored_df
        .merge(
            right = apps_filtered[["respondent_code", "num_apps"]],
            on = "respondent_code",
            how = "left",
        )
    )

    for var_name in bool_cols:
        raw_scores[var_name] = raw_scores[var_name] / raw_scores["num_apps"]

    scored_series = (
        raw_scores
        .loc[:, bool_cols]
        .mean(axis = 0)
        .mul(100)
        .round(2)
    )

    scored_series.name = "perc"

    scored_df = (
        scored_series
        .reset_index(drop = False)
        .rename(columns = {"index": "var_name"})
        .merge(
            right = reference_df,
            on = "var_name",
            how = "left",
        )
    )

    scored_df["option_type"] = scored_df["is_other"].apply(lambda b: "Other Option" if b else "Given Option")

    scored_df["perc_str"] = make_perc_col(scored_df["perc"])

    # Show intermediary steps
    if debug:
        st.write(apps_filtered)
        st.write(main_filtered)
        st.write(scored_df)
        st.write(raw_scores)
        st.write(scored_series)
        st.write(scored_df)

    # Find top scoring option
    top_index = scored_df["perc"].idxmax()
    top_name = scored_df.at[top_index, "long_name"]
    top_score = scored_df.at[top_index, "perc_str"]

    st.markdown(f"Top {singular}: **{top_name}**. On average, each student chose this {singular} for {top_score} of their college applications.")

    # Make chart
    num_var_title = "Score"
    opt_var_title = singular.title()

    source = alt.Chart(scored_df)

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

    st.caption("Percentages may not add up to exactly 100% because respondents were allowed to check multiple options for each application.")

    return