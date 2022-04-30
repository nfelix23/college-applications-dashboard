import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

# Import custom functions for graph creation
from app_graph_functions import select_college_types, make_perc_col, chart_checkbox

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

        str_coll_types, set_coll_types = select_college_types(st_key = "num_colleges_applied")

        filtered = (
            db.apps
            .loc[
                db.apps["college_type"].isin(set_coll_types)
            ]
            .pivot_table(index = "respondent_code", values = "num_apps", aggfunc = "sum")
            .reset_index(drop = False)
        )

        total_students = filtered["respondent_code"].drop_duplicates().shape[0]

        median_colls = int(filtered["num_apps"].median())

        aggregated = (
            filtered
            .pivot_table(index = "num_apps", values = "respondent_code", aggfunc = "count")
            .reset_index(drop = False)
            .rename(columns = {"respondent_code": "num_students"})
        )

        aggregated["perc"] = (
            aggregated["num_students"]
            / total_students
            * 100
        ).round(2)

        aggregated["perc_str"] = make_perc_col(aggregated["perc"])

        aggregated["is_median"] = aggregated["num_apps"].eq(median_colls).apply(lambda x: "Yes" if x else "No")

        st.metric(
            "Median Number of Colleges Applied To",
            median_colls
        )

        st.caption("The orange bar indicates the median.")

        base = (
            alt.Chart(aggregated)
        )
        bar = (
            base
            .mark_bar()
            .encode(
                x = alt.Y("num_apps:O", title = "Number of Colleges"),
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

    chart_checkbox(
        db = db,
        info_type = "location",
        singular = "location",
        intro = "## Locations of Colleges\n\nThis chart shows the locations of the colleges where students applied.",
        st_key = "location_chart",
    )

    # Interests

    chart_checkbox(
        db = db,
        info_type = "interests",
        singular = "interest",
        intro = "## Interests\n\nThis chart is about the fields of study that were the reasons behind students' college application choices.",
        st_key = "interests_chart",
    )

    # Characteristics

    chart_checkbox(
        db = db,
        info_type = "characteristics",
        singular = "characteristic",
        intro = "## Characteristics\n\nThis chart is about the college characteristics that were the reasons behind students' application choices.",
        st_key = "characteristics_chart",
    )