import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

def select_college_types(st_key):
    """Let the user select one or both college types."""
    options_dct = {
        "local": set(["local"]),
        "international": set(["international"]),
        "local and international": set(["local", "international"]),
    }

    str_selection = st.radio(
        "Include college types:",
        options = options_dct.keys(),
        key = st_key,
    )

    lst_selection = options_dct[str_selection]

    return str_selection, lst_selection

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

def feature_overview(db):
    st.markdown("""## Overview Charts\n\nThis section provides a general overview of the survey results.""")

    # Respondent Turnout

    st.markdown("## Respondent Turnout")

    def chart_respondent_turnout(db = db):

        total_g12 = 919
        num_respondents = db.main["respondent_code"].drop_duplicates().shape[0]
        num_other = total_g12 - num_respondents
        
        perc_respondents = round((num_respondents / total_g12) * 100, 2)
        str_perc_respondents = f"{perc_respondents}%"

        st.metric(
            "Percentage of Grade 12 Students who Responded",
            str_perc_respondents,
        )

        res_df = pd.DataFrame(
            {
                "responded": ["No", "Yes"],
                "number": [num_other, num_respondents],
            }
        )

        res_df["perc"] = (res_df["number"] / total_g12 * 100).round(2)

        res_df["perc_str"] = make_perc_col(res_df["perc"])

        base = (
            alt.Chart(res_df)
            .mark_bar()
            .encode(
                x = alt.X("number:Q", title = "Number of Students"),
                y = alt.Y("responded:N", title = "Responded"),
                tooltip = [alt.Tooltip("number:Q", title = "Number of Students")],
            )
        )

        text = base.mark_text(
            align = "left",
            baseline = "middle",
            # Nudge text to right so it doesn't appear on top of the bar
            dx = 3,
        ).encode(
            text = "perc_str:N"
        )

        chart = base + text

        st.altair_chart(chart, use_container_width = True)

        return

    chart_respondent_turnout()

    # Number of Colleges Applied To

    st.markdown("## Number of Colleges Applied To")

    def chart_num_colleges(db = db):

        coll_per_student = (
            db.main
            .pivot_table(index = ["respondent_code", "college_type"], values = "index", aggfunc = "count")
            .rename(columns = {"index": "num_colleges"})
            .reset_index(drop = False)
        )

        str_coll_types, lst_coll_types = select_college_types(st_key = "num_colleges_applied")

        filtered = (
            coll_per_student
            .loc[
                coll_per_student["college_type"].isin(lst_coll_types)
            ]
            .pivot_table(index = "respondent_code", values = "num_colleges", aggfunc = "sum")
            .reset_index(drop = False)
        )

        total_students = filtered["respondent_code"].drop_duplicates().shape[0]

        median_colls = int(filtered["num_colleges"].median())

        aggregated = (
            filtered
            .pivot_table(index = "num_colleges", values = "respondent_code", aggfunc = "count")
            .reset_index(drop = False)
            .rename(columns = {"respondent_code": "num_students"})
        )

        aggregated["perc"] = (
            aggregated["num_students"]
            / total_students
            * 100
        ).round(2)

        aggregated["perc_str"] = make_perc_col(aggregated["perc"])

        aggregated["is_median"] = aggregated["num_colleges"].eq(median_colls).apply(lambda x: "Yes" if x else "No")

        st.metric(
            "Median Number of Colleges Applied To",
            median_colls
        )

        base = (
            alt.Chart(aggregated)
        )
        bar = (
            base
            .mark_bar()
            .encode(
                x = alt.Y("num_colleges:O", title = "Number of Colleges"),
                y = alt.X("num_students:Q", title = "Number of Students"),
                color = alt.Color("is_median:N", legend = None),
                tooltip = [
                    alt.Tooltip("num_students:Q", title = "Number of Students"),
                ]
            )
        )
        text = (
            bar.mark_text(
                align = "center",
                baseline = "middle",
                dy = -4,
            ).encode(
                text = "perc_str:N"
            )
        )
        # rotate x labels so they are horizontal, not vertical
        chart = (
            (bar + text)
            .configure_axisX(labelAngle = 0, labelFontSize = 20)
        )

        st.altair_chart(chart, use_container_width = True)

        return

    chart_num_colleges()

    # Location

    st.markdown("## Locations of Colleges")

    def chart_locations(db = db):

        to_count = select_to_count(st_key = "locations")

        str_coll_types, lst_coll_types = select_college_types(st_key = "locations")

        if to_count == "applications":

            locations = (
                db.main
                .loc[db.main["college_type"].isin(lst_coll_types)]
                .pivot_table(index = ["location", "college_type"], values = "index", aggfunc = "count")
                .reset_index(drop = False)
                .rename(columns = {"index": "num"})
            )

        elif to_count == "students":
            locations = (
                db.main
                .loc[
                    db.main["college_type"].isin(lst_coll_types),
                    ["index", "location", "college_type", "respondent_code"]
                ]
                .drop_duplicates(["location", "college_type", "respondent_code"])
                .pivot_table(index = ["location", "college_type"], values = "index", aggfunc = "count")
                .reset_index(drop = False)
                .rename(columns = {"index": "num"})
            )

        total_num = locations["num"].sum()

        locations["perc"] = (locations["num"] / total_num * 100).round(2)
        locations["perc_str"] = make_perc_col(locations["perc"])

        top_index = locations["num"].idxmax()
        top_name = locations.at[top_index, "location"]
        top_score = locations.at[top_index, "perc_str"]

        st.write(f"Top location: **{top_name}**, with {top_score} of {to_count} with regard to {str_coll_types} colleges.")

        var_title = f"Number of {to_count}"

        source = alt.Chart(locations)

        y_sort = alt.EncodingSortField("num", order = "descending")

        bar = (
            source
            .mark_bar()
            .encode(
                x = alt.X("num:Q", title = var_title),
                y = alt.Y("location:N", title = "Location", sort = y_sort),
                color = alt.Color("college_type:N", title = "College Type"),
                tooltip = [alt.Tooltip("num:Q", title = var_title)],
            )
        )
        text = (
            source
            .mark_text()
            .encode(
                text = alt.Text("perc_str:N"),
                y = alt.Y("location:N", title = "Location", sort = y_sort, axis = None),
            )
            .properties(width = 50)
        )
        chart = alt.hconcat(bar, text, spacing = 0)

        st.altair_chart(chart, use_container_width = True)

        return

    chart_locations()

    # Function for both interests and characteristics

    def chart_checkbox(
        info_type, # str, whether interests or characteristics
        singular, # str, singular form of info_type, for grammar purposes
        intro, # str, the introductory text for the chart
        db = db,
    ):
        st.markdown(intro)

        to_count = select_to_count(st_key = info_type)

        str_coll_types, lst_coll_types = select_college_types(st_key = info_type)

        reference_df = db.ddict.loc[
            db.ddict["info_type"] == info_type,
            ["var_name", "long_name"]
        ]
        
        info_type_cols = reference_df["var_name"].tolist()

        var_to_long = {
            row["var_name"]: row["long_name"]
            for index, row in reference_df.iterrows()
        }

        id_vars = ["index", "respondent_code", "college_type"]
        cols_to_take = id_vars + info_type_cols

        filtered_df = db.main[cols_to_take]

        filtered_df = filtered_df.loc[filtered_df["college_type"].isin(lst_coll_types)]

        melted = (
            pd.melt(
                filtered_df,
                id_vars = id_vars,
                value_vars = info_type_cols,
                value_name = "checked",
            )
            .rename(columns = {"variable": "option"})
        )

        if to_count == "students":
            total_num = filtered_df.drop_duplicates("respondent_code").shape[0]

            aggregated = (
                melted
                .pivot_table(
                    index = ["option", "respondent_code"],
                    values = ["checked"],
                    aggfunc = "any",
                )
                .reset_index(drop = False)
                .pivot_table(
                    index = ["option"],
                    values = ["checked"],
                    aggfunc = "sum",
                )
                .reset_index(drop = False)
                .rename(columns = {"checked": "num"})
            )

        elif to_count == "applications":
            total_num = filtered_df.shape[0]

            aggregated = (
                melted
                .pivot_table(
                    index = ["option"],
                    values = ["checked"],
                    aggfunc = "sum",
                )
                .reset_index(drop = False)
                .rename(columns = {"checked": "num"})
            )
        
        # Add column indicating whether it is an Other option
        aggregated = aggregated.merge(
            db.ddict[["var_name", "is_other"]],
            how = "left",
            left_on = "option",
            right_on = "var_name",
        )

        aggregated["option_type"] = aggregated["is_other"].replace(
            {
                True: "Other Option",
                False: "Given Option",
            }
        )

        aggregated["long_name"] = aggregated["option"].replace(var_to_long)

        aggregated["perc"] = (aggregated["num"] / total_num * 100).round(2)
        aggregated["perc_str"] = make_perc_col(aggregated["perc"])

        top_index = aggregated["num"].idxmax()
        top_name = aggregated.at[top_index, "long_name"]
        top_score = aggregated.at[top_index, "perc_str"]

        st.write(f"Top {singular}: **{top_name}**, with {top_score} of {to_count} with regard to {str_coll_types} colleges.")

        num_var_title = f"Number of {to_count}"
        opt_var_title = singular.title()

        source = alt.Chart(aggregated)

        y_sort = alt.EncodingSortField("num", order = "descending")

        bar = (
            source
            .mark_bar()
            .encode(
                x = alt.X("num:Q", title = num_var_title),
                y = alt.Y("option:N", title = opt_var_title, sort = y_sort),
                color = alt.Color("option_type:N", title = "Option Type"),
                tooltip = [
                    alt.Tooltip("long_name:N", title = "Option"),
                    alt.Tooltip("num:Q", title = num_var_title),
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
                y = alt.Y("option:N", title = opt_var_title, sort = y_sort, axis = None),
            )
            .properties(width = 50)
        )
        chart = alt.hconcat(bar, text, spacing = 0)

        st.altair_chart(chart, use_container_width = True)

        st.caption("Percentages may not add up to exactly 100% because respondents were allowed to check multiple options for each application.")

        return

    # Interests

    chart_checkbox(
        "interests",
        "interest",
        "## Interests\n\nThis chart is about the fields of study that were the reasons behind students' college application choices."
    )

    # Characteristics

    chart_checkbox(
        "characteristics",
        "characteristic",
        "## Characteristics\n\nThis chart is about the college characteristics that were the reasons behind students' application choices."
    )