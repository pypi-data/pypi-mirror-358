import pandas as pd
import os
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


def atrp_planner(file_path):
    file_path_sheet = file_path
    data_file = pd.read_excel(file_path, sheet_name=None)

    copolymer = len(data_file) > 1
    if copolymer:
        data = {"Sheet1": data_file[list(data_file.keys())[0]]}
        monomer_df = data_file.get(list(data_file.keys())[1], None)
        user_stocks_df = data_file.get(list(data_file.keys())[2], None)
        unique_monomers = get_unique_monomers(data_file)
    else:
        data = data_file
        monomer_df = None
        user_stocks_df = None
    # 2

    # The row parameter is used to match polymer ID in polymer sheet however if sample from that sheet
    # Then the polymer ID wont be the same as the "row" entry so for now chanfed the "row" to be same value as polymer ID

    def calculate_polymer_volume_updated(df):
        results = []
        for index, row in df.iterrows():
            total_volume = 0
            details = {}
            # Calculate the volume needed for the monomer to achieve the final desired concentration
            monomer_volume = (
                row["Monomer"] * row["Mf"] / row["Monomer"] * row["Volume"]
            ) / row["[M]"]
            details["Monomer"] = monomer_volume
            total_volume += monomer_volume

            # Check other components based on their feed ratios
            component_to_column = {
                "Initiator": "[I]",
                "Metal": "[Metal]",
                "Ligand": "[L]",
                "Photo catalyst": "[PC]",
            }
            # This wasnt changed so therefore the calculation wouldnt have been affected for final ratios for things made beofre seems (01152025)
            # As monomer_volume = (row['Mf'] * row['Volume']) / row['[M]'] this was equation since stocks were 2M, (1000mM)*200/2000 = 100 so got lucky it would have been same for DP 200 since same as vol
            for component, concentration_column in component_to_column.items():
                # First find the final concentration of reagent
                cf = row[component] * row["Mf"] / row["Monomer"]
                required_volume = (cf * row["Volume"]) / row[concentration_column]
                total_volume += required_volume
                details[component] = required_volume

            # Calculate the solvent volume required to reach the final volume if total component volumes are less
            if total_volume < row["Volume"]:
                solvent_volume = row["Volume"] - total_volume
                details["Solvent"] = solvent_volume
                total_volume += solvent_volume
            else:
                details["Solvent"] = 0

            # Check if the total volume needed is within the desired final volume and all volumes are above 5 µL

            can_be_made = total_volume <= row["Volume"] and all(
                v >= 5 for v in details.values()
            )
            results.append(
                {
                    "Row": row["Polymer ID"],
                    "Can be made?": "Yes" if can_be_made else "No",
                    "Total Volume Needed": total_volume,
                    "Details": details,
                }
            )

        return results

    # Run the updated function with the new data
    updated_calculate_results = calculate_polymer_volume_updated(data["Sheet1"])
    updated_calculate_results
    polymer_sheet_analysis_df = pd.DataFrame(updated_calculate_results)
    polymers_needing_reag_adjust = polymer_sheet_analysis_df[
        polymer_sheet_analysis_df["Can be made?"] == "Yes"
    ].reset_index(drop=True)

    # 3
    # initializing volumes of reagents
    monomer_vol_needed = 0
    ini_vol_needed = 0
    metal_vol_needed = 0
    ligand_vol_needed = 0
    pc_vol_needed = 0
    solvent_vol_needed = 0

    for current in range(len(polymers_needing_reag_adjust["Can be made?"])):
        # adding vol for each row
        monomer_vol_needed = (
            monomer_vol_needed
            + polymers_needing_reag_adjust["Details"][current]["Monomer"]
        )
        ini_vol_needed = (
            ini_vol_needed
            + polymers_needing_reag_adjust["Details"][current]["Initiator"]
        )
        metal_vol_needed = (
            metal_vol_needed + polymers_needing_reag_adjust["Details"][current]["Metal"]
        )
        ligand_vol_needed = (
            ligand_vol_needed
            + polymers_needing_reag_adjust["Details"][current]["Ligand"]
        )
        pc_vol_needed = (
            pc_vol_needed
            + polymers_needing_reag_adjust["Details"][current]["Photo catalyst"]
        )
        solvent_vol_needed = (
            solvent_vol_needed
            + polymers_needing_reag_adjust["Details"][current]["Solvent"]
        )

    reagent_concentrations = {
        "[L]": user_stocks_df["Ligand"].dropna().tolist(),
        "[Metal]": user_stocks_df["Metal"].dropna().tolist(),
        "[PC]": user_stocks_df["PC"].dropna().tolist(),
    }  # "[Metal]":[22.5,11.25, 5.625,2.8125,1.40625]

    # 4

    # function looking at mult concentrations v3 --issue must be here bc no combination should be chosen if
    # this doesnt meet the criteria overall works but just went through the possible combinations for
    # Issue is that you're dumb and forgot to include the initiator volume

    # If sampling polymer ID wont match row so for now changed that to polymer ID too

    def calculate_polymer_volume_with_detailed_combinations(df, reagent_concentrations):
        import numpy as np
        import itertools

        results = []
        # Iterate over each row in the dataframe
        for index, row in df.iterrows():
            # print('Row------')
            possible_metal = []
            possible_ligand = []
            possible_pc = []
            valid_combinations = []

            # Generate all combinations of reagents
            metal_options = reagent_concentrations["[Metal]"]
            ligand_options = reagent_concentrations["[L]"]
            pc_options = reagent_concentrations["[PC]"]

            all_combinations = list(
                itertools.product(metal_options, ligand_options, pc_options)
            )

            # Check each combination
            for metal_conc, ligand_conc, pc_conc in all_combinations:
                metal_volume = (
                    row["Volume"]
                    * (row["Metal"] * (row["Mf"] / row["Monomer"]))
                    / metal_conc
                )
                ligand_volume = (
                    row["Volume"]
                    * (row["Ligand"] * (row["Mf"] / row["Monomer"]))
                    / ligand_conc
                )
                pc_volume = (
                    row["Volume"]
                    * (row["Photo catalyst"] * (row["Mf"] / row["Monomer"]))
                    / pc_conc
                )
                monomer_volume = (
                    row["Volume"]
                    * (row["Monomer"] * (row["Mf"] / row["Monomer"]))
                    / row["[M]"]
                )
                initiator_volume = (
                    row["Volume"]
                    * (row["Initiator"] * (row["Mf"] / row["Monomer"]))
                    / row["[I]"]
                )
                total_volume = (
                    metal_volume
                    + ligand_volume
                    + pc_volume
                    + monomer_volume
                    + initiator_volume
                )
                solvent_volume = 200 - total_volume
                # Added 01152025 working on proposal as solvent volume wasnt accounted in total vol in this step which would cause the ratios to be wrong
                if solvent_volume > 0 or solvent_volume == 0:
                    total_volume = total_volume + solvent_volume
                if solvent_volume < 0:
                    total_volume = 1000
                # End of addition on 01152025

                if total_volume <= row["Volume"] and all(
                    v >= 5
                    for v in [metal_volume, ligand_volume, pc_volume, solvent_volume]
                ):
                    # print('Solvent accepted')
                    # print(solvent_volume)
                    valid_combinations.append(
                        f"[{metal_conc}, {ligand_conc}, {pc_conc}]"
                    )
                    possible_metal.append(metal_conc)
                    possible_ligand.append(ligand_conc)
                    possible_pc.append(pc_conc)

            # Append the results for this row to the list
            results.append(
                {
                    "Row": row[
                        "Polymer ID"
                    ],  # Same thing here turned row into polymer ID as wont match for a sampled polymer sheet
                    "p[Metal]": ", ".join(map(str, set(possible_metal)))
                    if possible_metal
                    else np.nan,
                    "p[L]": ", ".join(map(str, set(possible_ligand)))
                    if possible_ligand
                    else np.nan,
                    "p[PC]": ", ".join(map(str, set(possible_pc)))
                    if possible_pc
                    else np.nan,
                    "Combination Details": "; ".join(valid_combinations),
                }
            )

        # Create a dataframe from results
        return pd.DataFrame(results)

    # Assuming the reagent_concentrations dictionary and data dataframe have been defined
    # Run the function
    updated_combination_results = calculate_polymer_volume_with_detailed_combinations(
        data["Sheet1"], reagent_concentrations
    )
    updated_combination_results.dropna()  # .reset_index(drop=True)
    # Now need to go through all the combinations and see whcih appear the most, and choose for each polymer
    # the combination that will be used, the combination chosen should be the one that
    # can be used for most, unless this sample only has a combination that works. After that need to find
    # out the volume of each of the concentrations that will be used to know how much of each to make
    # and whether to add this to a SmT or to well plate

    # 5

    from collections import Counter
    # Now need to go through all the combinations and see whcih appear the most, and choose for each polymer
    # the combination that will be used, the combination chosen should be the one that
    # can be used for most, unless this sample only has a combination that works. After that need to find
    # out the volume of each of the concentrations that will be used to know how much of each to make
    # and whether to add this to a SmT or to well plate

    # Splitting the 'Combination Details' into a list of combinations, flattening the list
    unique_combinations = set(
        combination.strip()  # Remove any surrounding whitespace
        for sublist in updated_combination_results["Combination Details"]
        for combination in sublist.split(";")  # Split each entry into combinations
        if combination.strip()  # Ensure the combination is not empty
    )

    # print("Unique Combinations:", unique_combinations)
    # print("Total Unique Combinations:", len(unique_combinations))

    # Looking through all combinations and seeing frequency they appear
    # So then can choose the combinations that appear most so can make less stock solutions

    # Flatten all combinations into a single list
    all_combinations = []
    for combinations in updated_combination_results["Combination Details"]:
        all_combinations.extend(combinations.split("; "))

    # Count each unique combination
    combination_counts = Counter(all_combinations)

    # print("Combination Frequency:", combination_counts)

    # Now going through the dataframe and looking at the possible combinations
    # Here we will make a decision of which to use for a certain polymer
    def select_best_combination(row, combination_counts):
        # Split the combinations in the row
        combinations = row["Combination Details"].split("; ")
        # If only one combination, return it
        if len(combinations) == 1:
            return combinations[0]
        # Find the combination with the highest count
        most_frequent_combination = max(
            combinations, key=lambda x: combination_counts[x]
        )
        return most_frequent_combination

    # Apply the function to each row in the DataFrame
    updated_combination_results["Best Combination"] = updated_combination_results.apply(
        lambda row: select_best_combination(row, combination_counts), axis=1
    )

    # Display the updated DataFrame with the best combination for each polymer
    # print(updated_combination_results[["Row", "Best Combination"]])

    updated_combination_results_wo_Na = updated_combination_results.dropna()
    updated_combination_results_wo_Na.reset_index(drop=True)

    # 6

    import numpy as np
    # Now making a new polymer sheet where we will update the stock concentration of each
    # reagent that will be used based on the chosen best combination, this will be later used to determine
    # what volume of each reagent at a given concentration is necessary (+ some extra for buffer)

    # Merge the best combinations into the original DataFrame based on 'Polymer ID' ('Row for best combs df)
    df = data["Sheet1"].merge(
        updated_combination_results_wo_Na,
        left_on="Polymer ID",
        right_on="Row",
        how="left",
    )

    # Update the DataFrame with new concentrations or NaN

    def update_concentrations(row):
        # First check if the 'Best Combination' is NaN
        if pd.isna(
            row["p[Metal]"]
        ):  # Cant use best combinations column bc we didnt explicitly add an np.nan
            row["[Metal]"], row["[L]"], row["[PC]"] = np.nan, np.nan, np.nan
        else:
            # Split the string and convert to floats only if 'Best Combination' is not NaN
            concentrations = row["Best Combination"].strip("[]").split(",")
            row["[Metal]"] = (
                float(concentrations[0].strip())
                if concentrations[0].strip()
                else np.nan
            )
            row["[L]"] = (
                float(concentrations[1].strip())
                if concentrations[1].strip()
                else np.nan
            )
            row["[PC]"] = (
                float(concentrations[2].strip())
                if concentrations[2].strip()
                else np.nan
            )
        return row

    # Apply the update function to each row
    df = df.apply(update_concentrations, axis=1)

    # Display the updated DataFrame
    df_interest = (
        df[
            [
                "Polymer ID",
                "Monomer",
                "Initiator",
                "Metal",
                "Ligand",
                "Photo catalyst",
                "[M]",
                "[I]",
                "[Metal]",
                "[L]",
                "[PC]",
                "Mf",
                "Volume",
            ]
        ]
        .dropna()
        .reset_index(drop=True)
    )
    # First using same initial function to get volumes (didnt change DF name should be fine as wont use the previous one again)
    updated_calculate_results = calculate_polymer_volume_updated(df)
    updated_calculate_results
    polymer_sheet_analysis_df = pd.DataFrame(updated_calculate_results)
    polymers_needing_reag_adjust = polymer_sheet_analysis_df[
        polymer_sheet_analysis_df["Can be made?"] == "Yes"
    ].reset_index(drop=True)
    polymers_needing_reag_adjust = polymers_needing_reag_adjust  # .dropna().reset_index(drop=True) #This here bc if drop NA here messes up the next step

    # 7

    # Here adding the volumes needed for each reagent at the given concentration for each sample in the DF

    from re import I
    # polymers_needing_reag_adjust['Details'][0]['Monomer']

    mon_vol = []
    ini_vol = []
    metal_vol = []
    ligand_vol = []
    PC_vol = []
    solvent_vol = []
    for i in range(len(polymers_needing_reag_adjust["Row"])):
        current = i
        # polymers_needing_reag_adjust)
        # polymers_needing_reag_adjust['Details'][current]
        mon_vol.append(polymers_needing_reag_adjust["Details"][current]["Monomer"])
        ini_vol.append(polymers_needing_reag_adjust["Details"][current]["Initiator"])
        metal_vol.append(polymers_needing_reag_adjust["Details"][current]["Metal"])
        ligand_vol.append(polymers_needing_reag_adjust["Details"][current]["Ligand"])
        PC_vol.append(
            polymers_needing_reag_adjust["Details"][current]["Photo catalyst"]
        )
        solvent_vol.append(polymers_needing_reag_adjust["Details"][current]["Solvent"])

    volumes_df = pd.DataFrame(
        zip(mon_vol, ini_vol, metal_vol, ligand_vol, PC_vol, solvent_vol),
        columns=[
            "Monomer Volume",
            "Initiator Volume",
            "Metal Volume",
            "Ligand Volume",
            "PC Volume",
            "Solvent Volume",
        ],
    )
    volumes_w_concent_df = (
        pd.concat([df_interest, volumes_df], axis=1)
        .round(
            {
                "Monomer Volume": 2,
                "Initiator Volume": 2,
                "Metal Volume": 2,
                "Ligand Volume": 2,
                "PC Volume": 2,
                "Solvent Volume": 2,
            }
        )
        .dropna()
    )
    volumes_w_concent_df

    # Now getting unique concentrations & storing in a dictionary for some reason some NaNs
    # Show up, I checked but there are non in DF & if check info() on dataframe no values are null
    columns_of_interest = ["[Metal]", "[L]", "[PC]"]

    # Calculate the number of unique values in each of these columns
    unique_entries = volumes_w_concent_df[columns_of_interest].nunique()

    # Display the number of unique entries for each column
    # print(unique_entries)
    # Get and print unique values for each column of interest
    unique_concent_dict = {}
    for column in columns_of_interest:
        unique_values = df[column].unique()
        unique_concent_dict[column] = unique_values
        # print(f"Unique values in {column}: {unique_values}")
    # Just recalculating final concentrations of reagents based on the volumes needed for sanity
    volumes_w_concent_df
    volumes_w_concent_df["Metal Cf"] = (
        volumes_w_concent_df["Metal Volume"]
        * volumes_w_concent_df["[Metal]"]
        / volumes_w_concent_df["Volume"]
    )
    volumes_w_concent_df["Ligand Cf"] = (
        volumes_w_concent_df["Ligand Volume"]
        * volumes_w_concent_df["[L]"]
        / volumes_w_concent_df["Volume"]
    )
    volumes_w_concent_df["PC Cf"] = (
        volumes_w_concent_df["PC Volume"]
        * volumes_w_concent_df["[PC]"]
        / volumes_w_concent_df["Volume"]
    )
    volumes_w_concent_df

    # 8 If they got diff monomers here gonna ask for input
    # Re-import necessary library

    # Find unique monomers
    unique_monomers = (
        set(monomer_df["Mon 1"].dropna())
        | set(monomer_df["Mon 2"].dropna())
        | set(monomer_df["Mon 3"].dropna())
        | set(monomer_df["Mon 4"].dropna())
    )

    # Initialize an empty DataFrame with Polymer ID and unique monomers as columns
    monomer_percent_df = pd.DataFrame(columns=["Polymer ID"] + sorted(unique_monomers))

    # Fill the new DataFrame with Polymer ID and corresponding monomer percentages
    for index, row in monomer_df.iterrows():
        row_data = {"Polymer ID": row["Polymer ID"]}
        for mon_col, perc_col in zip(
            ["Mon 1", "Mon 2", "Mon 3", "Mon 4"],
            ["Mon 1%", "Mon 2%", "Mon 3%", "Mon 4%"],
        ):
            if pd.notna(row[mon_col]):  # Check if monomer exists
                row_data[row[mon_col]] = row[perc_col] if pd.notna(row[perc_col]) else 0

        # Append row to the new DataFrame
        monomer_percent_df = pd.concat(
            [monomer_percent_df, pd.DataFrame([row_data])], ignore_index=True
        )

    # Fill NaN values with 0 for missing monomer percentages
    monomer_percent_df.fillna(0, inplace=True)

    # Merge the monomer_percent_df with volumes_w_concent_df to get the monomer volume for each row
    monomer_volume_df = monomer_percent_df.merge(volumes_w_concent_df, on="Polymer ID")

    # Multiply the percentages by the corresponding monomer volume to get the final volume for each monomer
    for monomer in monomer_percent_df.columns[1:]:  # Skip Polymer ID column
        monomer_volume_df[f"{monomer} Volume"] = (
            monomer_volume_df[monomer] / 100
        ) * monomer_volume_df["Monomer Volume"]

    # Drop the original percentage columns, keeping only the calculated volumes
    monomer_volume_df = monomer_volume_df.drop(columns=monomer_percent_df.columns[1:])

    # Display the final dataframe with monomer volumes

    volumes_w_concent_df = monomer_volume_df

    # Split the path into directory and filename
    # Here just saving and will put the dataframe in the same folder as the input file

    # Saving done outside now
    dir_path, file_name = os.path.split(file_path_sheet)

    # Modify the filename by adding "Synthesis_" before it
    new_file_name = "Volumes_DF_" + file_name

    # Reconstruct the full path
    new_final_path = os.path.join(dir_path, new_file_name)

    # print(new_final_path)

    volumes_w_concent_df.to_excel(new_final_path)

    # Do all your volume calcs and return a final dataframe

    return volumes_w_concent_df


def get_unique_monomers(data_file):
    """
    Gets the number of unique monomers when a data file contains a second sheet
    indicating a copolymer experiment.

    input: dataframe
    output: number of unique monomers (list)

    """
    # Extract the second sheet (monomer composition sheet)
    # Identify unique monomers across all columns Mon 1, Mon 2, Mon 3, Mon 4
    monomer_df = data_file[list(data_file.keys())[1]]

    # Identify unique monomers across all columns Mon 1, Mon 2, Mon 3, Mon 4
    monomer_columns = ["Mon 1", "Mon 2", "Mon 3", "Mon 4"]

    # Flatten and get unique values
    unique_monomers = set()
    for col in monomer_columns:
        unique_monomers.update(monomer_df[col].dropna().unique())

    # Output the unique monomers
    unique_monomers
    return unique_monomers
