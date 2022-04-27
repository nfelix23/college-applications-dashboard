# Cleaning part 1: Melt and expand the dataset.

#%%
import pandas as pd
import numpy as np
# %%
data_dict = pd.read_csv("./private/initial_inputs/data_dictionary.csv")

data_dict.head()
# %%
survey_df = pd.read_csv("./private/initial_inputs/survey_data_edited.csv")

survey_df.columns = data_dict["new_col_name"].tolist()

survey_df.head()
#%%
unique_col_groups = data_dict["col_group"].dropna().unique()

unique_col_groups
# %%
col_group_lists = {}

for cg in unique_col_groups:
    col_list = data_dict.loc[
        data_dict["col_group"] == cg,
        "new_col_name",
    ].tolist()

    col_group_lists[cg] = col_list
col_group_lists
#%%

college_type_dict = {
    "loc": "local",
    "int": "international",
}

melted_row_list = []

for index, melt_row in survey_df.iterrows():
    res_code = melt_row["respondent_code"]
    for cg in col_group_lists:
        # Make new row with only the columns in the specific column group.
        col_list = col_group_lists[cg]

        new_row = melt_row[col_list].copy()

        index_rename = {}
        for col_name in col_list:
            # Split column name on underscores and take the third item.
            # For example, "loc_1_name" becomes "name".
            info_type = col_name.split("_")[2]
            index_rename[col_name] = info_type

        new_row = new_row.rename(index_rename)

        # Add respondent code
        new_row["respondent_code"] = res_code

        # Add college type
        # Split column group name on underscores and take the first item.
        # For example, "loc_1" becomes "loc".
        indicator = cg.split("_")[0]
        college_type = college_type_dict[indicator]
        new_row["college_type"] = college_type

        melted_row_list.append(new_row)

melted_row_list[0]
# %%
melted_df = (
    pd.DataFrame(melted_row_list)
    .dropna(
        subset = ["name", "interests", "characteristics", "location"],
        how = "all",
    )
    .reset_index(drop = True)
)

melted_df.to_csv("./private/cleaning_outputs/melted_df.csv", index = False)

melted_df.head()
# %%
# Read data on options for each question.
option_df = pd.read_csv(f"./private/initial_inputs/options.csv")

option_df.head()
#%%
# Expand sequence-type columns into boolean columns.
seq_cols = ["interests", "characteristics"]

expanded_row_list = []

for melt_index, melt_row in melted_df.iterrows():
    initial_cols = ["name", "location", "respondent_code", "college_type"]

    expanded_row = melt_row[initial_cols].copy()

    for seq_col in seq_cols:
        sub_df = option_df.loc[
            option_df["info_type"] == seq_col,
            :
        ]

        seq_text = melt_row[seq_col]

        # If the item is not a string, it is a NaN. Populate the new row with False values and skip to the next seq_col.
        if not isinstance(seq_text, str):
            for opt_index, opt_row in sub_df.iterrows():
                option, shortcut, uss = opt_row[["option", "shortcut", "unique_starting_substring"]]

                expanded_row[shortcut] = False
            
            # Make "Other" option empty.
            expanded_row[f"{seq_col}_other"] = np.nan

            continue

        # index at which to start scanning the sequence text
        start_index = 0
        seq_length = len(seq_text)

        def remaining_chars():
            return seq_length - start_index

        for opt_index, opt_row in sub_df.iterrows():
            option, shortcut, uss = opt_row[["option", "shortcut", "unique_starting_substring"]]

            # If there are no more remaining characters, add a False entry and skip to the next option.
            if remaining_chars() == 0:
                expanded_row[shortcut] = False
                continue

            # uss refers to unique starting substring
            uss_length = len(uss)
            opt_length = len(option)

            end_index = start_index + uss_length

            start_text = seq_text[start_index:end_index]

            # boolean indicating whether start_text matches the current option's USS
            match = (start_text == uss)

            # Add new item to expanded_row. Use option's shortcut as index.
            expanded_row[shortcut] = match

            if match:
                # move scan to the right
                start_index += opt_length

                # if there are still remaining characters, move scan by 2 characters. These are the ", " characters separating options.
                if remaining_chars() > 0:
                    start_index += 2
                # If there are no more remaining characters, keep going through the list of options so that all columns are completed. Do not break the loop.

        # if more characters remain after options have been exhausted, it means these characters are the "Other" option, which was manually typed by the respondent.
        other_col = f"{seq_col}_other"

        if remaining_chars() > 0:
            other_text = seq_text[start_index:]
            expanded_row[other_col] = other_text
        else:
            expanded_row[other_col] = np.nan

    # append newly created row to list
    expanded_row_list.append(expanded_row)

expanded_df = (
    pd.DataFrame(expanded_row_list)
    .reset_index(drop = True)
    # Add an index column
    .reset_index(drop = False)
)

expanded_df.to_csv("./private/cleaning_outputs/expanded_df.csv", index = False)

expanded_df.head()
#%%
# Make summary of Other options
other_rows_list = []

location_options = option_df.loc[
    option_df["info_type"] == "location",
    "option"
]
mask_standard_location = (
    expanded_df["location"]
    .isin(location_options)
)
mask_other_location = mask_standard_location.apply(lambda x: not x)
list_other_location = expanded_df.loc[mask_other_location, "location"].tolist()

num_other_location = mask_other_location.sum()

num_other_interests = expanded_df["interests_other"].count()
num_other_characteristics = expanded_df["characteristics_other"].count()

other_rows_list = [
    ["interests", num_other_interests],
    ["characteristics", num_other_characteristics],
    ["location", num_other_location],
]

other_df = pd.DataFrame(other_rows_list)
other_df.columns = ["info_type", "num_other"]

other_df.to_csv("./private/cleaning_outputs/other_df.csv", index = False)

other_df
#%%
series_other_char = expanded_df["characteristics_other"].dropna()

series_other_char.name = "orig_text"

series_other_char.to_csv("./private/cleaning_outputs/characteristics_other.csv", index = False)