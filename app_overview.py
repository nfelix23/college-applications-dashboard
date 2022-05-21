import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

# Import custom functions for graph creation
import app_general_functions as agf

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

        res_df["perc_str"] = agf.make_perc_col(res_df["perc"])

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

    st.info(
"""Of the 919 Grade 12 students from the ASHS, only 178 or 19.37% responded. It should be noted, however, that a respondent is not limited to only one application. In total, the survey obtained data on 549 applications."""
    )

    # Number of Colleges Applied To

    st.markdown("## Number of Colleges Applied To")

    def chart_num_colleges(db = db):

        str_coll_types, set_coll_types = agf.select_college_types(st_key = "num_colleges_applied")

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

        aggregated["perc_str"] = agf.make_perc_col(aggregated["perc"])

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

    st.info(
"""For both local and international colleges, the top number of colleges applied to is two (2) colleges, accounting for 27.53% of the total number of respondents. This is followed by four (4) colleges and three (3) colleges, which garnered 23.60% and 22.47%, respectively. 

The highest number of local colleges applied to by respondents was two (2) colleges with 29.78%, followed by three (3) colleges with 24.72%, and four (4) colleges with 23.60%. Meanwhile, the highest number of international colleges applied to was only one (1) college, which constituted 34.78% of the respondents who applied abroad. This is followed by two (2) colleges at 30.43%, and three (3) colleges at 17.39%. 

The average number of colleges applied to by each respondent for the local, and local & international classifications is three (3) colleges, while, the average number of colleges applied to considering only international schools is two (2) colleges."""
    )

    # Function for all three info_type values
    def chart_checkbox(
        db,
        info_type, # str, whether interests or characteristics
        singular, # str, singular form of info_type, for grammar purposes
        intro, # str, the introductory text for the chart
        st_key, # str, string to put into key argument of streamlit widgets
        debug = False, # bool, whether or not to show the intermediary steps in data transformation
    ):
        """Make an overview chart for a given info_type value (location, interests, or characteristics)."""

        # Display intro text
        st.markdown(intro)

        # Ask for college types
        str_coll_types, set_coll_types = agf.select_college_types(st_key = f"chart_checkbox {st_key}")

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
            ["var_name", "long_name", "is_other", "college_type"]
        ]

        if info_type == "location":
            reference_df = reference_df.loc[
                reference_df["college_type"].isin(set_coll_types)
            ]

        bool_cols = reference_df["var_name"].tolist()

        selection = ["index", "respondent_code"] + bool_cols

        main_filtered = main_filtered.loc[:, selection]
        
        raw_scores = (
            main_filtered
            .pivot_table(
                index = ["respondent_code"],
                values = bool_cols,
                aggfunc = "sum",
            )
            .reset_index(drop = False)
        )

        raw_scores = (
            raw_scores
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

        # option_type column depends on the info_type.
        # for locations, they are grouped into local and international
        # for interests and characteristics, they are grouped into other options and given options
        if info_type == "location":
            scored_df["option_type"] = scored_df["college_type"].apply(
                lambda x: x.title()
            )
        else:
            scored_df["option_type"] = scored_df["is_other"].apply(
                lambda x: "Other Option" if x else "Given Option"
            )

        scored_df["perc_str"] = agf.make_perc_col(scored_df["perc"])

        # Show intermediary steps
        if debug:
            st.write(apps_filtered)
            st.write(main_filtered)
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

        agf.chart_of_percentages(scored_df, num_var_title, opt_var_title)

        return

    # Location

    chart_checkbox(
        db = db,
        info_type = "location",
        singular = "location",
        intro = "## Locations of Colleges\n\nThis chart shows the locations of the colleges where students applied.",
        st_key = "location_chart",
    )

    st.info(
"""Considering both local and international applications, the top location of the colleges that the respondents applied to was the National Capital Region (NCR) within the Philippines, which constituted an average of 93.27% of the college applications. This is then followed by North America, which was an average of 3.81% of the total college applications. 

For the local colleges applied to by students, the top location was the National Capital Region, which accounted for 99.19% of the respondents’ total college applications. This is followed by Luzon (outside NCR), which was chosen by 0.72% of the total applications.

For the locations of the international colleges where students applied, the top location was North America, which accounted for 66.23% of the total college applications submitted by the respondents. The next top location was Asia, which was selected for 16.23% of the international college applications gathered. These are followed by Australia/Oceania and Europe, which accounted for 13.19% and 4.35% of the total international applications, respectively."""
    )

    # Interests

    chart_checkbox(
        db = db,
        info_type = "interests",
        singular = "interest",
        intro = "## Interests\n\nThis chart is about the fields of study that were the reasons behind students' college application choices.",
        st_key = "interests_chart",
    )

    st.info(
"""From local and international colleges, the top interest seen among students is Science, Technology, Engineering, and Mathematics (STEM)-oriented endeavors at 57.91%. After STEM-oriented interests are the following in descending order of popularity: Accountancy, Business, and Management (ABM)-oriented, Humanities, Education, and Social Sciences (HUMSS)-oriented, Arts and Design (AD)-oriented, Sports-oriented, and Technical-Vocational-Livelihood (TVL) -oriented interests. Students chose ABM-oriented and HUMSS-oriented interests for 36.91% and 33.33% of their local and international college applications, respectively. The interests least chosen by students for their local and international college applications are AD-oriented interests with 15.31%, Sports-oriented interests with 5.16%, and TVL-oriented interests with 4.07%. 

Each student chose STEM-oriented as their top interest for 58.60% of their local college applications. Moreover, students also chose ABM-oriented and HUMSS-oriented interests for 37.13% and 33.88% of their local college applications, respectively. The interests least chosen by students for their local college applications are AD-oriented interests with 15.37%, Sports-oriented interests with 5.16%, and TVL-oriented interests with 4.15%. 

Each student chose STEM-oriented as their top interest for 48.26% of their international college applications. Additionally, students also chose ABM-oriented and HUMSS-oriented interests for 33.04% and 30.29% of their international college applications, respectively. The interests least chosen by students for their  international college applications are AD-oriented interests with 21.74%, Sports-oriented interests with 4.35%, and TVL-oriented interests with 2.17%."""
    )

    # Characteristics

    chart_checkbox(
        db = db,
        info_type = "characteristics",
        singular = "characteristic",
        intro = "## Characteristics\n\nThis chart is about the college characteristics that were the reasons behind students' application choices.",
        st_key = "characteristics_chart",
    )

    st.info(
"""For local and international applications combined, the top characteristic considered by students was: **Perceived high quality of education**. On average, each student chose this characteristic for 90.05% of their college applications. Students also valued the availability of specific courses and their perceived employability after graduation, accounting for 50.25% and 47.29% of each respondent's applications, respectively.

The perceived high quality of education, availability of specific courses, rate of employability, popularity, and low tuition fee are the top five qualities considered for local applications. For international applications, the top attributes are comparable, with high-quality education remaining at the top, followed by popularity, availability of specific courses, rate of employability, and the option for financial aid for tuition fee reduction. Low tuition rate, which is the fifth most common factor in each student's local applications, only accounts for 10.87%  of each respondent’s international applications."""
    )