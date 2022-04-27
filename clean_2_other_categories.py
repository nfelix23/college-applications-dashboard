# Cleaning part 2: Combine "Other" options into categories.

#%%
import pandas as pd
import numpy as np
#%%
expanded_df = pd.read_csv("./private/cleaning_outputs/expanded_df.csv")

# Delete the `interests_other` column because it's empty.
expanded_df = expanded_df.drop("interests_other", axis = 1)

expanded_df.head()
# %%
char_answers = pd.read_csv("./private/other_answers/characteristics_other_answers.csv")

category_df = pd.read_csv("./private/other_answers/options_with_others.csv")

category_df = category_df.loc[category_df["is_other"]]

category_df
# %%
new_row_list = []

for exp_index, exp_row in expanded_df.iterrows():
    # New row should not have this column
    new_row = exp_row.copy().drop("characteristics_other")

    answer = exp_row["characteristics_other"]

    # If answer is NaN, add False entries to new row.
    if not isinstance(answer, str):
        for cat_index, cat_row in category_df.iterrows():
            new_row[cat_row["shortcut"]] = False

    for cat_index, cat_row in category_df.iterrows():
        category = cat_row["option"]
        shortcut = cat_row["shortcut"]

        orig_text_list = char_answers.loc[
            char_answers["category"] == category,
            "orig_text"
        ].tolist()

        new_row[shortcut] = answer in orig_text_list

    new_row_list.append(new_row)

new_df = pd.DataFrame(new_row_list).reset_index(drop = True)

new_df.to_csv("./private/cleaning_outputs/expanded_with_other.csv", index = False)

new_df
#%%
# Show summary of new columns made
shortcut_list = category_df["shortcut"].tolist()

summary = new_df[shortcut_list].sum()
total_other = summary.sum()
print(f"Total other: {total_other}")
summary