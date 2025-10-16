import pandas as pd
import os

def convert_csv(csv_path = "./data", csv_filename="RADIO_MOCK_FM.csv"):
    csv_fullpath = os.path.join(csv_path, csv_filename)

    try:
        df = pd.read_csv(csv_fullpath)
    except Exception as err:
        raise FileNotFoundError(f"Could not read CSV file: {err}")

    # Check necessary columns exist in df
    required_cols = ["Timestamp", "Played_Duration", "Artist_Title"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Convert timestamp column to ISO8601, taking into account misformatted columns
    try:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="mixed", dayfirst=True)
        df["Timestamp"] = df["Timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception as err:
        raise ValueError(f"Error parsing column 'Timestamp': {err}")

    # Convert Played_Duration column to HH:MM:SS format
    try:
        df["Played_Duration"] = pd.to_datetime(df["Played_Duration"], unit="s").dt.strftime("%H:%M:%S")
    except Exception as err:
        raise ValueError(f"Error parsing column 'Played_Duration': {err}")

    # Split Artist_Title column to Artist and Title column (split by first dash)
    try:
        df[["Artist", "Title"]] = df["Artist_Title"].str.split("-", n=1, expand=True)
        df["Artist"] = df["Artist"].str.strip()     # Trims leading and trailing whitespace
        df["Title"] = df["Title"].str.strip()       # Trims leading and trailing whitespace
    except Exception as err:
        raise ValueError(f"Error splitting 'Artist_Title' column: {err}")

    # Reorder columns
    col_order = df.columns.to_list()            
    if "Artist" in df.columns and "Title" in df.columns:
        col_order = col_order[:-2]              # Remove latter 2 cols since they are newly-added cols
        idx = col_order.index("Artist_Title")
        col_order[idx:idx+1] = ["Artist", "Title"]
    else:
        raise ValueError(f"Required columns not found: 'Artist', 'Title'")
    
    # Drop old column
    df = df.drop(columns="Artist_Title")
    df = df[col_order]

    return df


if __name__ == "__main__":
    df = convert_csv()    
    print(df)

    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, "RADIO_MOCK_F_converted.csv"), index=False)