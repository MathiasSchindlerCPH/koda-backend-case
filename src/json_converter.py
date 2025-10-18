import os
import json
import pandas as pd

class JsonConverter:
    def __init__(self, input_path: str, output_path: str):
        """
        Konverterer en JSON-file til fladt format.

        Args:
            
        """
        self.input_path = input_path
        self.output_path = output_path

    def run(self) -> pd.DataFrame:
        # Indlæs data
        data = self.open_json()

        # Validér data
        self.validate_structure(data)

        # Præprocesser data
        data_udsendelser = self.preprocess_udsendelser(data)

        # Normalisér JSON til DataFrame
        df = self.normalize_udsendelser(data_udsendelser)
        df = self.normalize_rettighedsholdere(df)

        # Formater data
        df = self.combine_with_headers(data, df)

        return df

    def open_json(self) -> dict:
        """Indlæser JSON-data fra fil."""
        with open(self.input_path, "r") as file:
            return  json.load(file)    

    def validate_structure(self, data: dict) -> None:
        """Flader nested udsendelse og indslag ud i én samlet struktur."""
        if "rapportering" not in data:
            raise ValueError("JSON mangler 'rapportering'-nøglen.")
        if len(data["rapportering"]) != 1:
            raise ValueError(f"Forventede præcis 1 felt 'rapportering', men fandt {len(data['rapportering'])}")

    def preprocess_udsendelser(self, data: dict) -> dict:
        """Præprocessering: Fladgør JSON ved at fjerne nested udsendelse og indslag igennem fjernelse af overflødige nøgler"""
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
        return data

    def normalize_udsendelser(self, data: dict) -> pd.DataFrame:
        """Konverterer udsendelser og indslag til DataFrame."""
        broadcasts = data["rapportering"][0]["udsendelser"]
        return pd.json_normalize(broadcasts, record_path=["udsendelse_indslag"])

    def normalize_rettighedsholdere(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ekspanderer nested rettighedshaver til flade kolonner."""
        if "rettighedshaver" not in df.columns:
            return df
        else:
            # Ekspander rettighedshaver felt
            df = df.explode("rettighedshaver").reset_index(drop=True)
            expanded = pd.json_normalize(df["rettighedshaver"])

            # Tilføj rettighedshaver felt tilbage til oprindeligt df
            df = pd.concat([df, expanded], axis=1)
            df.drop("rettighedshaver", axis=1, inplace=True)

            return df

    def combine_with_headers(self, data: dict, df: pd.DataFrame) -> pd.DataFrame:
        """Tilføjer header-data til hver række i DataFrame."""
        headers = data["rapportering"][0]["header"]
        df_header = pd.DataFrame([headers] * len(df))

        df_combined = pd.concat([df_header, df], axis=1)

        return df_combined

    def export_csv(self, df: pd.DataFrame) -> None:
        """Eksporterer DataFrame til CSV-fil på output_path."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        df.to_csv(self.output_path, index=False)

        print(f"✓JSON transformed → {self.output_path}")


if __name__ == "__main__":
    input_path = "./data/MOCK_STREAMING_Q4_2023.json"
    output_path = "./output/MOCK_STREAMING_Q4_2023_transformed.csv"

    json_task = JsonConverter(input_path, output_path)
    df = json_task.run()

    json_task.export_csv(df)

    print(df.head())