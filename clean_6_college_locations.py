# Cleaning part 6: Create a separate CSV file for colleges and their locations and college types.
# Remove that data from the main CSV file.

#%%
import pandas as pd
import numpy as np
# %%
full_df = pd.read_csv("./private/cleaning_outputs/cleaned_college_names_final.csv")

full_df.head()
# %%
college_df = full_df[["name", "location", "college_type"]].drop_duplicates(keep = "first")

# If there are duplicate colleges, it means that the information about one or more colleges is inconsistent. That is, perhaps one student marked a school as being in NCR while another student marked it as being in Luzon.
no_dupe_colleges = college_df["name"].duplicated().sum() == 0

assert no_dupe_colleges

college_df
# %%
# Save to a file
college_df.to_csv("./private/cleaning_outputs/colleges_sheet.csv", index = False)

# %%
# Remove the separated info from the main sheet

main_df = full_df.drop(["location", "college_type"], axis = 1)

main_df.head()
# %%
main_df.to_csv("./private/cleaning_outputs/main_sheet.csv", index = False)
#%%