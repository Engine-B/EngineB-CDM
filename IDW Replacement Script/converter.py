import pandas as pd
import numpy as np
import json

df = pd.read_csv("./EngineBAuditCDMv1.9.csv")
df = df.rename(columns={
    "enginebAttribute": "name",
    "MS_DataType": "dataType",
    "primaryKey": "isNullable",
    "Description": "description"
})

df["isNullable"] = np.where(df["isNullable"].isnull(), "true", "false")
df["displayName"] = df["name"]
df["decimalPlaces"] = np.where(df["dataType"] == "decimal", 5, None)

df_grouped = df.groupby("enginebEntity")

for name, group in df_grouped:
    json_object = {
        "jsonSchemaSemanticVersion": "1.0.0",
        "imports": [
            {
                "corpusPath": "_allImports.cdm.json"
            }
        ],
        "definitions": [
            {
                "entityName": name,
                "extendsEntity": "CdmEntity",
                "hasAttributes": [
                    json.loads(group[["name", "dataType", "isNullable", "displayName", "decimalPlaces", "description"]].to_json(orient="records"))
                ]
            }
        ]
    }
    
    with open(f"./output/{name}.cdm.json", "w") as outfile:
        json.dump(json_object, outfile, indent=4)