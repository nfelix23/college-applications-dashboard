import streamlit as st

def feature_methodology():

    # Methodology
    st.markdown(
"""## Methodology

### Data Collection

The overall purpose of this study was to enable incoming Grade 12 students to make guided decisions in choosing schools to apply to based on the choices of the previous Grade 12 batch.

The data to be visualized in the ASHS College Apps Dashboard was taken from a survey in the study titled, “The Which and Whys: A Quantitative Study on the Universities ASHS Grade 12 Students Applied for and their Reasons for Choosing Them,” which was disseminated to S.Y. 2021-2022 Grade 12 Students of the Ateneo de Manila Senior High School from April 6, 2022 to April 16, 2022. The survey asked students about which specific schools they applied to, their interests in courses offered in these schools, where these schools are located, and why else they considered these schools. The survey was also divided into a local schools and international schools section to maximize the data to be collected.

The given interests in courses were taken from senior high school strands such as STEM, ABM, and HUMSS, as well as senior high school tracks like Arts & Design, Sports, and Technical-Vocational Livelihood. The given characteristics, on the other hand, are taken from common factors students consider in a school such as its quality of education, the specificity of its courses, or its employability of students, and many more.

### Dashboard

The survey data was cleaned to follow a standardized format, then uploaded to a private Google Sheets file where it can be accessed by the dashboard. Then, the dashboard was coded using the Python programming language. Notably, the Streamlit package (Treuille et al., 2019/2021) was used as the framework for making a web application, while the pandas package (The pandas development team, 2021) was used for data transformation and the Altair package (VanderPlas et al., 2018) was used to generate graphs. The source code was published to a public GitHub repository, then the dashboard was deployed online using Streamlit Cloud so that anyone can use it by visiting the link.

The first page of the dashboard is the Overview Charts page. The first chart shows how many ASHS Grade 12 students answered the survey. The second chart is a histogram showing the distribution of the number of colleges that the respondents applied to. The next three charts show which locations, interests (STEM, ABM, etc.), and characteristics (high quality of education, higher employability, etc.) were considered most by the respondents. The scores were calculated by dividing the number of college applications where each respondent chose a particular option by the total number of college applications they submitted, then taking the mean average across all respondents. The user can choose whether to look at the data for local colleges, international colleges, or both.

The second page is Filter and Rank Colleges. The user can filter colleges using several criteria: college type (local or international), location, interests, and characteristics. For the latter three variables, multiple items may be selected. Once the user has chosen filters, they may click the button to calculate college rankings. By default, the colleges are simply ranked by how many respondents applied to them. If filtering options were chosen, the colleges are ranked based on those criteria. Here is a simplified explanation. For example, if the user chooses “STEM-oriented” as their interest (A), and “Perceived reputation of professors” as their preferred characteristic (B), then the dashboard uses a scoring system where A and B are multiplied together. In this way, it determines which colleges match the criteria best.

The third page is the College Info Charts page. The user can use the drop-down box to select one college out of those that showed up in the survey data. The page then shows the college’s location, as well as which interests and characteristics were considered by the most students when applying to this college."""
    )

    # Recommendations
    st.markdown(
"""## Recommendations

a. Utilize a more diverse respondent range. 

The study participants were limited to a single grade level from only one institution due to the difficulty of finding respondents in the current online setup. Therefore, due to the lack of diversity of the respondents, the data collected may not be an accurate representation of the reason as to why they chose the colleges and universities that they applied to. Furthermore, the demographics may have significantly affected the data collected since their situations and experiences directly affect their views and opinions. It would be more preferable to distribute the surveys to students from other senior high schools inside and outside Metro Manila in order for colleges to be represented better. Also, distributing a future survey much earlier into the school year would have increased the number of participants from the ASHS.

b. Collect more comprehensive data.

Since the study utilized the use of google form surveys, we were not able to get a detailed response from the participants as to why they selected their chosen schools. Aside from the “others” function that we were able to put in the survey, there were no other ways in which we could get an in-depth response from the respondents, and conducting interviews and FGDs might be a solution to that. Students’ interests were also limited to strand and track groups instead of actual college programs. Researchers may explore other research instruments to accommodate more specific responses."""
    )

    # References
    st.markdown(
"""## References

Python Software Foundation. (2021). Python programming language (3.8.11) [Computer software]. https://docs.python.org/3.8/
The pandas development team. (2021). pandas-dev/pandas: Pandas 1.3.2 (1.3.2) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.5203279

Treuille, A., Teixeira, T., & Kelly, A. (2021). Streamlit (1.3.1) [TypeScript]. Streamlit. https://github.com/streamlit/streamlit (Original work published 2019)

VanderPlas, J., Granger, B. E., Heer, J., Moritz, D., Wongsuphasawat, K., Satyanarayan, A., Lees, E., Timofeev, I., Welsh, B., & Sievert, S. (2018). Altair: Interactive Statistical Visualizations for Python. Journal of Open Source Software, 3(32), 1057. https://doi.org/10.21105/joss.01057"""
    )