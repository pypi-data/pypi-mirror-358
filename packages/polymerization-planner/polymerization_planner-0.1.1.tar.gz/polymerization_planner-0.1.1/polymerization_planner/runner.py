import argparse
from polymerization_planner.atrp import atrp_planner
from polymerization_planner.pet_raft import pet_raft_planner

import pandas as pd

required_version = "2.2.2"
if pd.__version__ != required_version:
    raise RuntimeError(f"This script requires pandas version {required_version}, but found {pd.__version__}.")


def main():
    parser = argparse.ArgumentParser(description="Polymerization Planner CLI")
    parser.add_argument('--mode', choices=['atrp', 'pet'], required=True, help='Choose the polymerization mode')
    parser.add_argument('--file', type=str, required=True, help='Path to Excel file')

    args = parser.parse_args()

    if args.mode == 'atrp':
        print("\n🧪 Running ATRP planner...\n")
        result_df = atrp_planner(args.file)
    elif args.mode == 'pet':
        print("\n🔆 Running PET-RAFT planner...\n")
        result_df = pet_raft_planner(args.file)
    else:
        raise ValueError("Unsupported mode selected.")

    output_path = args.file.replace(".xlsx", f"_{args.mode}_recipes.xlsx")
    result_df.to_excel(output_path, index=False)
    print(f"\n✅ Recipes saved to: {output_path}\n")


if __name__ == "__main__":
    main()
