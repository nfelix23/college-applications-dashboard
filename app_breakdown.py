import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

import app_graph_functions as agf

def feature_breakdown(db):

    st.markdown("## Breakdown Page")

    with st.expander("Options", expanded = False):

        st.markdown("### College Types")

        str_college_types, set_college_types = agf.select_college_types(st_key = "breakdown")

        set_exclude_college_types = set(["local", "international"]) - set_college_types

        checkbox_info_types = ["location", "interests", "characteristics"]

        checkbox_selections = {}

        final_info_types = []
        
        selected_locations = db.ddict.loc[db.ddict["info_type"] == "location", "var_name"].tolist()

        for info_type in checkbox_info_types:
            st.markdown(f"### {info_type.title()}")

            choose_specific = f"Choose specific {info_type}"

            any_or_specific = st.radio(
                label = f"Select {info_type}",
                options = ["Any", choose_specific],
            )
            
            if any_or_specific == choose_specific:
                final_info_types.append(info_type)

                # Check first which options were actually answered by respondents.
                all_options = db.ddict.loc[
                    (db.ddict["info_type"] == info_type),
                    "var_name",
                ]

                num_answers_per_option = db.main[all_options].sum(axis = 0)
                final_options = num_answers_per_option.loc[num_answers_per_option > 0].index.tolist()

                mask = (
                    (db.ddict["var_name"].isin(final_options))
                    &
                    # Note bitwise NOT
                    ~(db.ddict["college_type"].isin(set_exclude_college_types))
                )

                reference_df = db.ddict.loc[mask]

                var_to_long = {
                    row["var_name"]: row["long_name"]
                    for index, row in reference_df.iterrows()
                }

                multi = st.multiselect(
                    label = "Click the bar to see a dropdown list. You may also type a word inside the bar in order to search for it.",
                    options = var_to_long.keys(),
                    format_func = lambda x: var_to_long[x],
                    key = f"{info_type} {str_college_types}",
                )

                if len(multi) == 0:
                    st.warning("No options are selected. Please select at least 1.")
                checkbox_selections[info_type] = multi

    # Show rankings

    st.markdown("## Rankings")

    # Warning if there are missing options

    missing_selection = any([len(item) == 0 for item in checkbox_selections.values()])

    if missing_selection:
        st.warning("Please go back and finish selecting options.")
        st.stop()

    # Put location info in `selected_locations`
    if "location" in checkbox_selections:
        selected_locations = checkbox_selections["location"]
        del checkbox_selections["location"]

    # Check if filtering options were chosen
    selected_columns = []
    for info_type, multi in checkbox_selections.items():
        selected_columns.extend(multi)

    no_filter = len(selected_columns) == 0

    if no_filter:
        st.markdown("No specific interests or characteristics were selected, so colleges will be ranked by number of students who applied.")
    else:
        st.markdown("Some specific interests or characteristics were selected. These will be considered when ranking colleges.")

    # Calculate rankings
    if not st.checkbox("Calculate rankings"):
        st.stop()

    initial_columns = ["index", "respondent_code", "name", "location", "college_type"]

    get_columns = initial_columns + selected_columns

    # Remove colleges that are not in the chosen locations
    location_mask = db.main.loc[:, selected_locations].any(axis = 1)

    rank_df = db.main.loc[location_mask, get_columns]

    # Warning if rank_df is empty
    if rank_df.shape[0] == 0:
        st.warning("No data is available on colleges in the selected locations. Please select other locations.")
        st.stop()

    if no_filter:
        # If no filtering options were chosen, simply rank colleges by number of students.

        coll_type_mask = rank_df["college_type"].isin(set_college_types)

        rank_df = rank_df.loc[coll_type_mask]
        rank_df["num_students"] = 1
        rank_df = (
            rank_df.pivot_table(
                index = ["name", "location"],
                values = "num_students",
                aggfunc = "sum",
            )
            .reset_index(drop = False)
            .sort_values("num_students", ascending = False)
            .reset_index(drop = False)
        )

        # Let user select how many colleges to show

        total_num_colleges = rank_df.shape[0]

        default_value = 10 if total_num_colleges >= 10 else total_num_colleges

        show_top = st.number_input(
            "Show how many colleges?",
            min_value = 1,
            max_value = total_num_colleges,
            value = default_value,
        )

        for i, row_rank in rank_df.iterrows():

            rank = i + 1
            if rank > show_top:
                st.stop()

            college_name = row_rank['name']
            num_students = row_rank["num_students"]
            locn = row_rank["location"]

            st.markdown(f"{rank}. {college_name}")

            with st.expander("More information", expanded = False):

                st.markdown(f"Number of applicants: {num_students}")
                st.markdown(f"Location: {locn}")

    else:
        # Rank using filtering options

        rank_df = (
            rank_df
            .pivot_table(
                index = ["name", "location"],
                values = selected_columns,
                aggfunc = "sum",
            )
            .reset_index(drop = False)
        )

        score_cols = []

        for col in selected_columns:
            # Do modified min-max scaling, such that the modified minimum is (1/100)(range) below the real minimum.
            real_min = rank_df[col].min()
            real_max = rank_df[col].max()
            rng = (real_max - real_min)

            modified_min = real_min - (rng / 100)
            modified_rng = real_max - modified_min

            score_col_name = f"{col}_score"
            score_cols.append(score_col_name)

            rank_df[score_col_name] = rank_df[col].sub(modified_min).div(modified_rng)

        # Calculate final score of each college as the product of its individual scores.
        rank_df["final_score"] = rank_df[score_cols].product(axis = 1)

        # Sort by score
        rank_df = (
            rank_df.sort_values("final_score", ascending = False)
            .reset_index(drop = True)
        )

        # Show rankings

        total_num_colleges = rank_df.shape[0]

        default_value = 10 if total_num_colleges >= 10 else total_num_colleges

        show_top = st.number_input(
            "Show how many colleges?",
            min_value = 1,
            max_value = total_num_colleges,
            value = default_value,
        )

        selected_reference_df = db.ddict.loc[db.ddict["var_name"].isin(selected_columns)]

        for i, row_rank in rank_df.iterrows():

            rank = i + 1
            if rank > show_top:
                st.stop()

            college_name = row_rank['name']

            st.markdown(f"{rank}. {college_name}")

            with st.expander(label = "More information", expanded = False):

                for info_type in final_info_types:

                    st.markdown(f"{info_type.title()}:")

                    if info_type == "location":
                        st.markdown(row_rank["location"])

                    else:

                        filtered_reference_df = selected_reference_df.loc[
                            selected_reference_df["info_type"] == info_type
                        ]
                        
                        for j, row_reference in filtered_reference_df.iterrows():
                            var_name = row_reference["var_name"]
                            long_name = row_reference['long_name']
                            num_students = row_rank[var_name]

                            st.markdown(f"- {long_name}: **{num_students} students**")

                    st.markdown("---")