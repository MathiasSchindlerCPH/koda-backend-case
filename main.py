import os
from src.json_converter import JsonConverter
from src.csv_converter import CsvConverter

def main(): 
    # Sæt op folderstruktur
    data_dir = "./data"
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    # JSON transformation
    json_task = JsonConverter(
        input_path=os.path.join(data_dir, "MOCK_STREAMING_Q4_2023.json"),
        output_path=os.path.join(output_dir, "MOCK_STREAMING_Q4_2023_transformed.csv"),
    )
    json_task.run()

    # CSV konvertering
    csv_task = CsvConverter(
        input_path=os.path.join(data_dir, "RADIO_MOCK_FM.csv"),
        output_path=os.path.join(output_dir, "RADIO_MOCK_FM_converted.csv"),
    )
    csv_task.run()

if __name__ == "__main__":
    main()