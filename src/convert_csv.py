import pandas as pd
import os

def convert_csv(csv_path = "./data", csv_filename="RADIO_MOCK_FM.csv"):
    csv_fullpath = os.path.join(csv_path, csv_filename)
    df = pd.read_csv(csv_fullpath)

    # Convert timestamp column to ISO8601, taking into account misformatted columns
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="mixed", dayfirst=True)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Convert Played_Duration column to HH:MM:SS format
    df["Played_Duration"] = pd.to_datetime(df["Played_Duration"], unit='s').dt.strftime("%H:%M:%S")

    # Split Artist_Title column to Artist and Title column (split by first dash)
    df[['Artist', 'Title']] = df['Artist_Title'].str.split('-', n=1, expand=True)
    df["Artist"] = df["Artist"].str.strip()     # Trims leading and trailing whitespace
    df["Title"] = df["Title"].str.strip()       # Trims leading and trailing whitespace

    # Reorder columns
    col_order = df.columns.to_list()[:-2]       # Remove latter 2 cols since they are newly-added cols
    idx = col_order.index("Artist_Title")
    col_order[idx:idx+1] = ['Artist', 'Title']
    
    # Drop old column
    df = df.drop(columns="Artist_Title")
    df = df[col_order]

    return df


if __name__ == "__main__":
    df = convert_csv()
    print(df)

    df.to_csv("./output/RADIO_MOCK_F_converted.csv")