import os
import json
import pandas as pd

CDM_VERSION = "3.0" # <-- change version here
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


with open("data/standards.json", "r") as f:
    standards = json.load(f)
standards = standards["standards"]

with open("data/entity.json", "r") as f:
    entities = json.load(f)
entities = entities["entities"]



file_name = f"CDM {CDM_VERSION}.xlsx"
file_path = os.path.join(ROOT_DIR, file_name)

df = pd.read_excel(file_path, sheet_name=f"CDM {CDM_VERSION}")
if "Mandatory?" not in df.columns:
    df["Mandatory?"] = "N"
df = df[
    [
        "enginebStandard",
        "enginebEntity",
        "enginebAttribute",
        "MS_DataType",
        "Description",
        "Mandatory?",
    ]
]
df["Mandatory?"] = df["Mandatory?"].fillna("N")
eb_cdm = {
    "version": CDM_VERSION,
    "standards": []
}

for standard in df.enginebStandard.unique():
    standard_object = next(filter(lambda x: x["abbreviation"] == standard, standards))
    standard_object = standard_object if standard_object is not None else {
        "name": standard,
        "abbreviation": standard,
    }
    standard_object["entities"] = []
    standard_df = df[df.enginebStandard == standard]
    for entity in standard_df.enginebEntity.unique():
        entity_object = list(filter(lambda x: x["name"] == entity if entity != 'chartOfAccounts' else 'ChartOfAccounts', entities))
        entity_object = entity_object[0] if len(entity_object) > 0 else {
            "display_name": entity,
            "name": entity,
        }
        entity_df = standard_df[standard_df.enginebEntity == entity]
        entity_df = entity_df[
            [
                "enginebAttribute",
                "MS_DataType",
                "Description",
                "Mandatory?",
            ]
        ]
        entity_df.columns = ["name", "data_type", "description", "mandatory"]
        entity_df = entity_df[["name", "description", "data_type", "mandatory"]]
        entity_df["mandatory"] = entity_df.apply(
            lambda x: True if x["mandatory"] == "Y" else False, axis=1
        )
        entity_df.fillna("", inplace=True)
        attributes = entity_df.to_dict(orient="records")
        entity_object["attributes"] = attributes
        standard_object["entities"].append(entity_object)
    eb_cdm["standards"].append(standard_object)

output_file_name = file_name.replace(".xlsx", "").replace(" ", "_").replace(".", "_").lower() + ".json"
output_file_path = os.path.join(ROOT_DIR, "src", "output", output_file_name)

with open(output_file_path, "w") as f:
    json.dump(eb_cdm, f, indent=4)
