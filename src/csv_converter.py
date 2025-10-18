import pandas as pd
import os

class CsvConverter:
    def __init__(self, input_path: str, output_path: str):
        """
        Konverterer en CSV file til rent format.

        Args:
            input_path: Sti til input CSV-fil.
            output_path: Sti til output konverteret CSV-fil.
        """
        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        df = pd.read_csv(self.input_path)

        # Bekræft nødvendige kolonner eksisterer i df; ellers warning
        required_cols = ["Timestamp", "Played_Duration", "Artist_Title"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Konverter timestamp kolonner til ISO8601, tage højde for misformaterrede datoer
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="mixed", dayfirst=True)
        df["Timestamp"] = df["Timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Konverter Played_Duration kolonne til HH:MM:SS format
        df["Played_Duration"] = pd.to_datetime(df["Played_Duration"], unit="s").dt.strftime("%H:%M:%S")

        # Split Artist_Title kolonne i Artist og Title kolonne (split ved første bindestreg)
        df[["Artist", "Title"]] = df["Artist_Title"].str.split("-", n=1, expand=True)

        # Fjern leading og trailing whitespace fra nye kolonner
        df["Artist"] = df["Artist"].str.strip()     
        df["Title"] = df["Title"].str.strip()       

        # Omroker columns
        col_order = df.columns.to_list()            
        if "Artist" in df.columns and "Title" in df.columns:
            col_order = col_order[:-2]              # Slet sidste 2 kolonner, siden det er de nyeste tilføjelser, i.e. Artist og Title
            idx = col_order.index("Artist_Title" )
            col_order[idx:idx+1] = ["Artist", "Title"]
        else:
            raise ValueError(f"Required columns not found: 'Artist', 'Title'")

        # Slet gamle kolonne
        df = df.drop(columns="Artist_Title")
        df = df[col_order]

        # Gem som csv-fil
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        df.to_csv(self.output_path, index=False)
        print(f"✓CSV converted → {self.output_path}")

        return df
        

if __name__ == "__main__":
    input_path = "./data/RADIO_MOCK_FM.csv"
    output_path = "./output/RADIO_MOCK_FM_converted.csv"

    converter = CsvConverter(input_path, output_path)
    df = converter.run()

    print(df.head())