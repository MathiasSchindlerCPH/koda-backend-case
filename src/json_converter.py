import pandas as pd
import os
import json

class JsonConverter:
    def __init__(self, input_path: str, output_path: str):
        """
        Konverterer en JSON-file til fladt format.

        Args:
            input_path: Sti til input JSON-fil.
            output_path: Sti til output konverteret, flad JSON-struktur til CSV-eksport.
        """
        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        with open(self.input_path, "r") as f:
            data = json.load(f)    

        if len(data["rapportering"]) != 1:
            raise ValueError(f"Expected exactly 1 rapportering entry, but found {len(data['rapportering'])}")

        # Præprocesser data ved at fjerne overflødige keys
        udsendelser_data = data["rapportering"][0]["udsendelser"]        
        
        udsendelser_data_flat = []
        for udsendelse in udsendelser_data:
            # For hver udesendelse, ekstraher "udesendelse"-værdi og sæt i ny, ren liste
            udsendelse_flat = udsendelse["udsendelse"]
            udsendelser_data_flat.append(udsendelse_flat)

            # For hver udesendelse, ekstraher "udesendelse"-værdi og sæt i ny, ren liste
            indslag_data_flat = []
            for indslag in udsendelse_flat["udsendelse_indslag"]:
                indslag_flat = indslag["indslag"]
                indslag_data_flat.append(indslag_flat)

            # Overskriv oprindelig datastruktur med indslag
            udsendelse_flat["udsendelse_indslag"] = indslag_data_flat

        # Overskriv oprindelige datastruktur med udsendelser
        data["rapportering"][0]["udsendelser"] = udsendelser_data_flat

        # Opret df med "udsendelser" data
        broadcasts = data["rapportering"][0]["udsendelser"]
        df_broadcasts = pd.json_normalize(broadcasts, record_path=["udsendelse_indslag"])

        # Håndter nested rettighedshavere
        if "rettighedshaver" in df_broadcasts.columns:
            df_broadcasts = df_broadcasts.explode("rettighedshaver").reset_index(drop=True)
            
            # If rettighedshaver is a dict, expand its fields
            rettighedshaver_cols = pd.json_normalize(df_broadcasts["rettighedshaver"])
            df_broadcasts = pd.concat([df_broadcasts, rettighedshaver_cols], axis=1)
            df_broadcasts = df_broadcasts.drop("rettighedshaver", axis=1)

        # Opret df med "headers" data
        headers = data["rapportering"][0]["header"]
        df_header = pd.DataFrame([headers] * len(df_broadcasts))

        # Opret endelig df
        df = pd.concat([df_header, df_broadcasts], axis=1)

        # Gem som csv-fil
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        df.to_csv(self.output_path, index=False)
        print(f"✓JSON transformed → {self.output_path}")

        return df


if __name__ == "__main__":
    input_path = "./data/MOCK_STREAMING_Q4_2023.json"
    output_path = "./output/MOCK_STREAMING_Q4_2023_transformed.csv"

    converter = JsonConverter(input_path, output_path)
    df = converter.run()

    print(df.head())