# Cleaning part 3: Normalize the column of college names.

#%%
import pandas as pd
import numpy as np
import Levenshtein

survey_df = pd.read_csv("./private/cleaning_outputs/expanded_with_other.csv")

survey_df.head()
# %%
name_freq = survey_df["name"].value_counts(sort = "descending")

name_freq.head(30)
#%%
# Check if certain UP campuses are in the data.
# Note that we already know UP Diliman and Manila are in the data.
up_list = [
    "Los Banos",
    "Baguio",
    "Visayas",
    "Mindanao",
    "Cebu",
    "Open", # UP Open University
]

name_series = name_freq.index.to_series()

# Make a mask of college names that contain any of the strings in up_list
final_mask = [False for i in range(len(name_series))]

for campus in up_list:
    mask = name_series.str.contains(campus)
    # Merge mask into final_mask using bitwise OR
    final_mask = final_mask | mask

up_matches = name_freq.loc[final_mask]
up_matches
#%%
common_names = (
    pd.read_csv("./private/college_names/common_names.csv")
    .iloc[:, 0]
)

common_names
#%%
# Preprocessing

preprocess = lambda series: (
    series
    .str.lower()
    .str.strip()
    .str.replace(r"[^a-zA-Z0-9]", "", regex = True)
)

common_pp = preprocess(common_names)
survey_pp = survey_df[["index", "name", "location"]].copy()

survey_pp["name_pp"] = preprocess(survey_pp["name"])

survey_pp.head(10)
#%%
# Matching

# Function that can be used in df.apply()
def lv_ratio(s1, s2):
    return Levenshtein.ratio(s1, s2)

match_row_list = []

for sur_index, sur_row in survey_pp.iterrows():
    # The new row will include the original name and the index, but not the preprocessed name.
    new_row = sur_row[["index", "name", "location"]].copy()

    name = sur_row["name"]
    name_pp = sur_row["name_pp"]
    scores = common_pp.apply(lv_ratio, s2 = name_pp)
    best_index = scores.idxmax()
    best_score = scores.loc[best_index]

    # If score is lower than 80%, it is likely that the match is wrong. Thus, the "best match" should just be replaced by the original name.
    if best_score < 0.8:
        best_score = 0
        best_match = name
    else:
        best_match = common_names.loc[best_index]

    new_row["score"] = best_score
    new_row["match"] = best_match

    match_row_list.append(new_row)

match_df = (
    pd.DataFrame(match_row_list)
    .sort_values(by = ["score", "index"], ascending = True)
)

match_df.to_csv("./private/cleaning_outputs/match_df.csv", index = False)

match_df.head()
#%%