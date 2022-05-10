import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

import app_general_functions as agf

def feature_filter_rank(db):

    st.markdown("## Filter and Rank Colleges")

    st.markdown("You may click the `Options` button to select criteria for filtering colleges. Your choices will be summarized under `Selected Filters`. Then, click `Calculate rankings` to see which colleges best match your criteria.")

    with st.expander("Options", expanded = False):

        st.markdown("### College Types")

        str_college_types, set_college_types = agf.select_college_types(st_key = "filter_rank")

        set_exclude_college_types = set(["local", "international"]) - set_college_types

        checkbox_info_types = ["location", "interests", "characteristics"]

        checkbox_selections = {}

        final_info_types = []

        ddict_location_mask = (
            (db.ddict["info_type"] == "location")
            & (db.ddict["college_type"].isin(set_college_types))
        )
        
        selected_locations = db.ddict.loc[ddict_location_mask, "var_name"].tolist()

        for info_type in checkbox_info_types:
            st.markdown(f"### {info_type.title()}")

            choose_specific = f"Choose specific {info_type}"

            any_or_specific = st.radio(
                label = f"Select {info_type}",
                options = ["Any", choose_specific],
                key = f"any_or_specific {info_type}",
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

                var_to_long_filtered = {
                    row["var_name"]: row["long_name"]
                    for index, row in reference_df.iterrows()
                }

                # If user is filtering locations, key of multiselect widget should include the chosen college types.
                # This way, if the user selects a different set of college types, the location multiselect widget will update its options to include only locations that match those college types.
                if info_type == "location":
                    multi_key = f"multiselect {info_type} {str_college_types}"
                else:
                    multi_key = f"multiselect {info_type}"

                multi = st.multiselect(
                    label = "Click the bar to see a dropdown list. You may also type a word inside the bar in order to search for it.",
                    options = var_to_long_filtered.keys(),
                    format_func = lambda x: var_to_long_filtered[x],
                    key = multi_key,
                )

                if len(multi) == 0:
                    st.warning("No options are selected. Please select at least 1.")
                checkbox_selections[info_type] = multi

    # Show summary of filter choices
    st.markdown("## Selected Filters")
    st.markdown(f"College types: {str_college_types}")

    # Dictionary of variable names and corresponding long names
    # Contains variable names from all of the three relevant info types
    var_to_long_general = {
        row["var_name"]: row["long_name"]
        for index, row in db.ddict.iterrows()
    }

    for info_type in checkbox_info_types:
        if info_type in checkbox_selections:
            multi_var_name = checkbox_selections[info_type]
            multi_long_name = [var_to_long_general[v] for v in multi_var_name]
            multi_monospace = [f"`{long_name}`" for long_name in multi_long_name]

            multi_str = " | ".join(multi_monospace)

            st.markdown(f"{info_type.title()}: {multi_str}")
        else:
            st.markdown(f"{info_type.title()}: any")

    # Show rankings

    st.markdown("## Rankings")

    # Warning if there are missing options

    missing_selection = any([len(item) == 0 for item in checkbox_selections.values()])

    if missing_selection:
        st.warning("Please go back and finish selecting options.")
        st.stop()

    # Put location info in `selected_locations`
    if "location" in final_info_types:
        selected_locations = pd.Series(checkbox_selections["location"])
        del checkbox_selections["location"]
    else:
        # If location is not in the list, add it to the start
        final_info_types = ["location"] + final_info_types

    # Check if filtering options were chosen
    selected_columns = []
    for info_type, multi in checkbox_selections.items():
        selected_columns.extend(multi)

    no_filter = len(selected_columns) == 0

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

        show_top = st.slider(
            "Show how many colleges?",
            min_value = 1,
            max_value = total_num_colleges,
            value = default_value,
        )

        st.markdown("---")

        for i, row_rank in rank_df.iterrows():

            rank = i + 1
            if rank > show_top:
                st.stop()

            college_name = row_rank['name']
            num_students = row_rank["num_students"]
            locn = row_rank["location"]

            st.markdown(f"{rank}. **{college_name}**")

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
            # Do min-max scaling and add 0.01 to all numbers to avoid having zeros.
            min_value = rank_df[col].min()
            max_value = rank_df[col].max()
            rng = (max_value - min_value)

            score_col_name = f"{col}_score"
            score_cols.append(score_col_name)

            rank_df[score_col_name] = rank_df[col].sub(min_value).div(rng).add(0.01)

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

                    if info_type == "location":
                        st.markdown(f"{info_type.title()}: {row_rank['location']}")

                    else:
                        st.markdown(f"{info_type.title()}:")

                        filtered_reference_df = selected_reference_df.loc[
                            selected_reference_df["info_type"] == info_type
                        ]
                        
                        for j, row_reference in filtered_reference_df.iterrows():
                            var_name = row_reference["var_name"]
                            long_name = row_reference['long_name']
                            num_students = row_rank[var_name]

                            st.markdown(f"- {long_name}: **{num_students} students**")

                    # Display a newline to add extra space between sections
                    st.markdown("\n")