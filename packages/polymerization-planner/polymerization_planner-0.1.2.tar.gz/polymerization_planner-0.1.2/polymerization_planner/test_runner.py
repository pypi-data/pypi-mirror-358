# test_runner.py

from polymerization_planner.atrp.calculator import atrp_planner
from polymerization_planner.pet_raft.calculator import pet_raft_planner

# Replace with your own test path
test_path_atrp = "C:/Users/Cesar/Box/Sync files/2023/Experiments/CR1_32 DP Exp HighRes/test/Polymer_sheet_DP Var 05303025 Copoly.xlsx"
# "C:/Users/Cesar/Box/Sync files/2023/Experiments/CR1_32 DP Exp HighRes/test/Polymer_sheet_DP Var 05303025.xlsx"
test_path_pet = "C:/Users/Cesar/Box/Sync files/2023/Experiments/CR1_32 DP Exp HighRes/test\Polymer_sheet_DP RAFT - Copolys.xlsx"
# "C:/Users/Cesar/Box/Sync files/2023/Experiments/CR1_32 DP Exp HighRes/test/Polymer_sheet_DP RAFT - highDP.xlsx"

# Run both planners
df_atrp = atrp_planner(test_path_atrp)
df_pet = pet_raft_planner(test_path_pet)

# Print outputs to verify
print("ATRP Output:\n", df_atrp.head())
print("PET-RAFT Output:\n", df_pet.head())

# Need to run these in one line
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\venv\Scripts\Activate.ps1

