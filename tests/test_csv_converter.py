import os
import pandas as pd
import pytest
from csv_converter import CsvConverter

@pytest.fixture
def sample_csv(tmp_path):
    """Creates a temporary sample CSV for testing."""
    data = {
        "Timestamp": ["2023-01-01 12:00:00", "2023-01-02 14:30:00"],
        "Played_Duration": [120, 240],
        "Artist_Title": ["Radiohead - Creep", "Coldplay — Yellow"]
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "sample.csv"
    df.to_csv(file_path, index=False)
    return file_path

@pytest.fixture
def sample_df():
    """Returns a sample DataFrame for method-level tests."""
    data = {
        "Timestamp": ["2023-01-01 12:00:00", "2023-01-02 14:30:00"],
        "Played_Duration": [120, 240],
        "Artist_Title": ["Radiohead - Creep", "Coldplay — Yellow"]
    }
    return pd.DataFrame(data)

def test_read_csv(sample_csv):
    converter = CsvConverter(str(sample_csv), "dummy.csv")
    df = converter.read_csv()
    assert not df.empty
    assert set(df.columns) == {"Timestamp", "Played_Duration", "Artist_Title"}

def test_validate_columns(sample_df):
    converter = CsvConverter("dummy.csv", "dummy.csv")
    # Should not raise
    converter.validate_columns(sample_df)
    # Remove a column to trigger error
    df_missing = sample_df.drop(columns=["Played_Duration"])
    with pytest.raises(ValueError):
        converter.validate_columns(df_missing)

def test_convert_timestamps(sample_df):
    converter = CsvConverter("dummy.csv", "dummy.csv")
    df = converter.convert_timestamps(sample_df.copy())
    assert df["Timestamp"].str.endswith("Z").all()
    assert df["Timestamp"].str.contains("T").all()

def test_convert_durations(sample_df):
    converter = CsvConverter("dummy.csv", "dummy.csv")
    df = converter.convert_durations(sample_df.copy())
    assert df["Played_Duration"].iloc[0] == "00:02:00"
    assert df["Played_Duration"].iloc[1] == "00:04:00"

def test_split_combined_column(sample_df):
    converter = CsvConverter("dummy.csv", "dummy.csv")
    df = converter.split_combined_column(sample_df.copy())
    assert "Artist" in df.columns
    assert "Title" in df.columns
    assert df["Artist"].iloc[0] == "Radiohead"
    assert df["Title"].iloc[1] == "Yellow"

def test_rearrange_columns(sample_df):
    converter = CsvConverter("dummy.csv", "dummy.csv")
    df = converter.split_combined_column(sample_df.copy())
    df = converter.rearrange_columns(df)
    # Artist_Title should be gone, Artist and Title present
    assert "Artist_Title" not in df.columns
    assert "Artist" in df.columns and "Title" in df.columns

def test_export_csv(sample_df, tmp_path):
    converter = CsvConverter("dummy.csv", str(tmp_path / "out.csv"))
    converter.export_csv(sample_df)
    assert (tmp_path / "out.csv").exists()

def test_csv_conversion_runs(sample_csv, tmp_path):
    """Ensure CsvConverter runs end-to-end without errors."""
    output_path = tmp_path / "converted.csv"
    converter = CsvConverter(str(sample_csv), str(output_path))
    
    df = converter.run()
    converter.export_csv(df)
    
    # Assert: output file exists
    assert output_path.exists()

    # Assert: split columns exist
    assert "Artist" in df.columns
    assert "Title" in df.columns

    # Assert: timestamp formatting looks correct
    assert df["Timestamp"].str.contains("T").all()
