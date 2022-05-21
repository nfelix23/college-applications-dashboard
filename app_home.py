import pandas as pd
import numpy as np
import streamlit as st

def feature_home():
    # Intro
    st.markdown(
"""Welcome to the ASHS College Applications Dashboard! We recommend viewing this on desktop. Use the sidebar on the left side to navigate the app.

Below is a summary of the pages:

- The Methodology and Recommendations page explains how the survey was conducted and the dashboard was made. You don't have to read this to understand the dashboard, so feel free to explore the other pages first.
- The Overview Charts page includes general charts about the popularity of certain locations, interests, and characteristics that were considered when choosing a college.
- The Filter and Rank Colleges page allows the user to select filtering criteria and generate rankings of colleges based on how many respondents applied to them.
- The College Info Charts page allows the user to select one college and view charts about it."""
    )

    # Credits
    st.markdown(
"""## Credits

ASHS Data Analytics Committee '21-'22

- Sourcing Department: In charge of survey creation and dissemination, Methodology, Recommendations, and chart interpretations.
    - Fiona Jao
    - Nish Camacho
    - Andi Faller
    - Theia Pimentel
    - Emman Pabulayan
- Analysis Department: In charge of dashboard development.
    - Migs Germar"""
        )