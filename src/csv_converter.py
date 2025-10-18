import os
import pandas as pd

class CsvConverter:
    def __init__(
        self, 
        input_path: str, 
        output_path: str,
        timestamp_col: str = "Timestamp",
        duration_col: str = "Played_Duration",
        split_col: str = "Artist_Title",
        split_col_name_by_delimiter: str = "_",
        split_col_data_by_regex: str = r"\s[-—_|]\s"
    ):
        r"""
        Konverterer en CSV file til rent format.

        Args:
            input_path: Sti til input CSV-fil.
            output_path: Sti til output konverteret CSV-fil.
            timestamp_col: Kolonnenavn for timestamps.
            duration_col: Kolonnenavn for afspilningsvarighed.
            split_col: Kolonne der indeholder kombineret information (fx 'Artist_Title').
            split_col_name_by_delimiter: Tegn der bruges til at splitte kolonnennavnet i kolonnen 'split_col'.
            split_col_data_by_regex: RegEx der bruges til at splitte værdierne i kolonnen 'split_col'. Default er "\s[-—_|]\s" der splitter omkring enten "-", "—", "_" eller "|" med leading og trailing whitespace 
        """
        self.input_path = input_path
        self.output_path = output_path
        self.timestamp_col = timestamp_col
        self.duration_col = duration_col
        self.split_col = split_col
        self.split_col_name_by_delimiter = split_col_name_by_delimiter
        self.split_col_data_by_regex = split_col_data_by_regex

        # Dynamisk genereret liste over kolonner der skal være til stede
        self.required_cols = [self.timestamp_col, self.duration_col, self.split_col]

    def run(self) -> pd.DataFrame:
        # Indlæs data
        df = self.read_csv()

        # Validér data
        self.validate_columns(df)

        # Transformer data
        df = self.convert_timestamps(df)
        df = self.convert_durations(df)
        df = self.split_combined_column(df)

        # Strukturer data
        df = self.rearrange_columns(df)

        return df

    def read_csv(self) -> pd.DataFrame:
        return pd.read_csv(self.input_path)

    def validate_columns(self, df:pd.DataFrame) -> None:
        """Bekræft nødvendige kolonner eksisterer i df - ellers rejs ValueError."""
        missing = [col for col in self.required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Mangler kolonne(r): {', '.join(missing)}")

    def convert_timestamps(self, df:pd.DataFrame) -> pd.DataFrame:
        """
        Konverter timestamp kolonner til ISO8601.
        Tag højde for misformaterrede datoer.
        """
        df[self.timestamp_col] = pd.to_datetime(df[self.timestamp_col], format="mixed", dayfirst=True)
        df[self.timestamp_col] = df[self.timestamp_col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        return df

    def convert_durations(self, df:pd.DataFrame) -> pd.DataFrame:
        """Konverter kolonne til HH:MM:SS format"""
        df[self.duration_col] = pd.to_datetime(df[self.duration_col], unit="s").dt.strftime("%H:%M:%S")

        return df

    def split_combined_column(self, df:pd.DataFrame) -> pd.DataFrame:
        """
        Split kolonne ved første bindestreg og gem i to nye kolonner.
        Fjern leading og trailing whitespace fra nye kolonner
        """
        new_split_cols = self.split_col.split(self.split_col_name_by_delimiter)  # Byg nye kolonner ved split oprindeligt kolonnenavn ved underscore

        # Validér input kolonnenavn splitter i præcis 2 dele
        if len(new_split_cols) != 2:
            raise ValueError(
                f"Forventede split_col '{self.split_col}' til at dele i 2 dele, "
                f"med fik {len(new_split_cols)} ({new_split_cols})"
            )

        # Split data i split-kolonne i ved regex fra input-parameter "split_col_data_by_regex"
        df[new_split_cols] = df[self.split_col].str.split(self.split_col_data_by_regex, n=1, expand=True)
        
        # Fjern leading og trailing whitespace fra nye kolonner
        col_1, col_2 = new_split_cols       # unpack kolonner fra liste
        df[col_1] = df[col_1].str.strip()     
        df[col_2] = df[col_2].str.strip()           

        return df

    def rearrange_columns(self, df:pd.DataFrame) -> pd.DataFrame:
        """
        Omrokkerer DataFrame-kolonner, så de to nye kolonner fra split (fx 'Artist', 'Title')
        erstatter den oprindelige kombinerede kolonne (fx 'Artist_Title') i samme position.
        Fjerner den oprindelige split-kolonne fra DataFrame.
        """
        # Find nye kolonnenavne fra split:
        new_split_cols = self.split_col.split(self.split_col_name_by_delimiter)     # Byg nye kolonner ved split oprindeligt kolonnenavn ved underscore
        col_1, col_2 = new_split_cols                                               # unpack kolonner fra liste
        
        col_order = df.columns.to_list()            
        if col_1 in df.columns and col_2 in df.columns:
            # Fjern de to sidst tilføjede kolonner (de nye split-kolonner) fra kolonneordenen
            col_order.remove(col_1)
            col_order.remove(col_2)

            # Find index position i kolonneordenen for split_col og erstat med de to nye kolonner
            idx = col_order.index(self.split_col)
            col_order[idx:idx+1] = [col_1, col_2]
        else:
            raise ValueError(f"Nødvendige kolonner ikke fundet: '{col_1}', '{col_2}'")

        # Slet den oprindelige split_col fra df og omroker kolonner i den nye rækkefølge
        df = df.drop(columns=self.split_col)
        df = df[col_order]

        return df

    def export_csv(self, df: pd.DataFrame) -> None:
        """Eksporterer DataFrame til CSV-fil på output_path."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        df.to_csv(self.output_path, index=False)

        print(f"✓CSV converted → {self.output_path}")


if __name__ == "__main__":
    input_path = "./data/RADIO_MOCK_FM.csv"
    output_path = "./output/RADIO_MOCK_FM_converted.csv"

    csv_task = CsvConverter(input_path, output_path)
    df = csv_task.run()

    csv_task.export_csv(df)

    print(df.head())