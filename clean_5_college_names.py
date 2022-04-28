# Cleaning part 5: Revise the data to put the final college names.

#%%
import pandas as pd
import numpy as np

#%%

survey_df = pd.read_csv("./private/cleaning_outputs/cleaned_college_names_not_final.csv")

survey_df.head()
# %%
names_final_df = pd.read_csv("./private/college_names/names_locations_manually_fixed.csv")

names_final_df = names_final_df.loc[names_final_df["final_name"].notnull()]

names_final_df.head()
#%%
new_row_list = []
changed_row_list = []
for sur_index, sur_row in survey_df.iterrows():
    new_row = sur_row.copy()
    changed = False

    for nf_index, nf_row in names_final_df.iterrows():
        if sur_row["name"] == nf_row["name_choice"]:
            changed = True
            new_row["name"] = nf_row["final_name"]
    
    new_row_list.append(new_row)

    if changed:
        changed_row = new_row.copy()
        changed_row["orig_name"] = sur_row["name"]
        changed_row = changed_row[["index", "name", "orig_name"]]
        changed_row_list.append(changed_row)

cleaned_df = pd.DataFrame(new_row_list)

cleaned_df.head()
#%%
# Remove unnecessary text from location column
cleaned_df["location"] = cleaned_df["location"].str.replace(
    "Campus is located in ",
    "",
    regex = False,
)

cleaned_df.location.value_counts()
#%%
# Compare original and new
changed_df = pd.DataFrame(changed_row_list)

changed_df
#%%
# Final check by summarizing unique college names
names_last_check = (
    cleaned_df[["name"]]
    .drop_duplicates()
    .sort_values("name")
)

names_last_check.to_csv("./private/cleaning_outputs/names_last_check.csv", index = False)

names_last_check.head()
#%%
# If last check shows no problems, save the final cleaned dataset.
cleaned_df.to_csv("./private/cleaning_outputs/cleaned_college_names_final.csv", index = False)

#%%