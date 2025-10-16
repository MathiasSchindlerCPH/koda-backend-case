import pandas as pd
import os
import json

def transform_json(json_path = "./data", json_filename="MOCK_STREAMING_Q4_2023.json"):
    json_fullpath = os.path.join(json_path, json_filename)

    with open(json_fullpath, "r") as f:
        data = json.load(f)    

    if len(data["rapportering"]) != 1:
        raise ValueError(f"Expected exactly 1 rapportering entry, but found {len(data['rapportering'])}")
        

    # Create df with broadcasts data
    broadcasts = data["rapportering"][0]["udsendelser"]
    df_broadcasts = pd.json_normalize(
        broadcasts, 
        record_path=[
            "udsendelse", 
            "udsendelse_indslag",
            ], 
        meta=[
            ["udsendelse", "alt_udsendelses_titel"],
            ["udsendelse", "episode_nr"],
            ["udsendelse", "ondemandviews"],
            ["udsendelse", "producent"],
            ["udsendelse", "produktions_aar"],
            ["udsendelse", "produktions_land"],
            ["udsendelse", "produktions_nr"],
            ["udsendelse", "program_kode"],
            ["udsendelse", "udsendelse_varighed"],
            ["udsendelse", "udsendelses_titel"],
            ]
    )

    if "indslag.rettighedshaver" in df_broadcasts.columns:
        df_broadcasts = df_broadcasts.explode("indslag.rettighedshaver").reset_index(drop=True)
        
        # If rettighedshaver is a dict, expand its fields
        rettighedshaver_cols = pd.json_normalize(df_broadcasts["indslag.rettighedshaver"]).add_prefix("rettighedshaver.")
        df_broadcasts = pd.concat([df_broadcasts.drop(columns=["indslag.rettighedshaver"]), rettighedshaver_cols], axis=1)


    # Create df with "headers" data
    headers = data["rapportering"][0]["header"]
    df_header = pd.DataFrame([headers] * len(df_broadcasts))

    # Create final df
    df = pd.concat([df_header, df_broadcasts], axis=1)

    return df


if __name__ == "__main__":
    df = transform_json()
    print(df)

    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "MOCK_STREAMING_Q4_2023_transformed.csv"), index=False)