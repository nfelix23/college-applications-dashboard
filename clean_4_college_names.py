# Cleaning part 4: Check the revised column names to see if there are any college names that are very close to each other but not exactly the same.

#%%
import pandas as pd
import numpy as np

survey_df = pd.read_csv("./private/cleaning_outputs/expanded_with_other.csv")

survey_df.head()
# %%
match_edited_df = pd.read_csv("./private/college_names/match_df_manually_fixed.csv")

match_edited_df.head()
#%%

match_edited_cols = match_edited_df[[
    "index",
    "match",
    "name_revised",
    "location_revised",
]]

merged_df = match_edited_cols.merge(
    survey_df,
    on = "index",
    how = "left",
)

merged_df.head()
# %%
def find_choice(row, orig_col, revised_col):
    match = row[orig_col]
    revised = row[revised_col]
    if isinstance(revised, str):
        choice = revised
    else:
        choice = match
    return choice

merged_df["name_choice"] = merged_df.apply(
    find_choice,
    orig_col = "match",
    revised_col = "name_revised",
    axis = 1,
)

merged_df["location_choice"] = merged_df.apply(
    find_choice,
    orig_col = "location",
    revised_col = "location_revised",
    axis = 1,
)

merged_df.head(10)
#%%
output_df = merged_df.copy()

orig_col_list = survey_df.columns

output_df = (
    output_df.drop(["name", "location"], axis = 1)
    .rename({"name_choice": "name", "location_choice": "location"}, axis = 1)
    .loc[:, orig_col_list]
    .sort_values("index", ascending = True)
)

output_df.to_csv("./private/cleaning_outputs/cleaned_college_names_not_final.csv", index = False)
#%%
names_locations = (
    merged_df[["name_choice", "location_choice"]]
    .drop_duplicates()
    .sort_values("name_choice")
)

names_locations.to_csv("./private/cleaning_outputs/names_locations.csv", index = False)

names_locations.head()
#%%