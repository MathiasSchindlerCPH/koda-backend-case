import json
import pytest
import pandas as pd
from json_converter import JsonConverter

@pytest.fixture
def sample_json(tmp_path):
    """Creates a temporary sample JSON structure for testing."""
    data = {
        "rapportering": [{
            "header": {"period": "Q4_2023", "platform": "Streaming"},
            "udsendelser": [{
                "udsendelse": {
                    "udsendelse_indslag": [
                        {"indslag": {"title": "Song A", "rettighedshaver": [{"navn": "Artist A"}]}},
                        {"indslag": {"title": "Song B", "rettighedshaver": [{"navn": "Artist B"}]}}
                    ]
                }
            }]
        }]
    }
    json_path = tmp_path / "sample.json"
    with open(json_path, "w") as f:
        json.dump(data, f)
    return json_path

@pytest.fixture
def sample_data():
    """Returns a sample loaded JSON dict matching expected structure."""
    return {
        "rapportering": [{
            "header": {"period": "Q4_2023", "platform": "Streaming"},
            "udsendelser": [{
                "udsendelse": {
                    "udsendelse_indslag": [
                        {"indslag": {"title": "Song A", "rettighedshaver": [{"navn": "Artist A"}]}},
                        {"indslag": {"title": "Song B", "rettighedshaver": [{"navn": "Artist B"}]}}
                    ]
                }
            }]
        }]
    }

def test_open_json(sample_json):
    converter = JsonConverter(str(sample_json), "dummy.csv")
    data = converter.open_json()
    assert "rapportering" in data

def test_validate_structure(sample_data):
    converter = JsonConverter("dummy.json", "dummy.csv")
    # Should not raise
    converter.validate_structure(sample_data)
    # Should raise if missing key
    with pytest.raises(ValueError):
        converter.validate_structure({})

def test_preprocess_udsendelser(sample_data):
    converter = JsonConverter("dummy.json", "dummy.csv")
    processed = converter.preprocess_udsendelser(sample_data.copy())
    udsendelser = processed["rapportering"][0]["udsendelser"]
    assert isinstance(udsendelser, list)
    assert "udsendelse_indslag" in udsendelser[0]
    assert isinstance(udsendelser[0]["udsendelse_indslag"], list)
    assert "title" in udsendelser[0]["udsendelse_indslag"][0]

def test_normalize_udsendelser(sample_data):
    converter = JsonConverter("dummy.json", "dummy.csv")
    processed = converter.preprocess_udsendelser(sample_data.copy())
    df = converter.normalize_udsendelser(processed)
    assert isinstance(df, pd.DataFrame)
    assert "title" in df.columns

def test_normalize_rettighedsholdere(sample_data):
    converter = JsonConverter("dummy.json", "dummy.csv")
    processed = converter.preprocess_udsendelser(sample_data.copy())
    df = converter.normalize_udsendelser(processed)
    df2 = converter.normalize_rettighedsholdere(df)
    assert "navn" in df2.columns
    assert df2["navn"].iloc[0] == "Artist A"

def test_combine_with_headers(sample_data):
    converter = JsonConverter("dummy.json", "dummy.csv")
    processed = converter.preprocess_udsendelser(sample_data.copy())
    df = converter.normalize_udsendelser(processed)
    df2 = converter.normalize_rettighedsholdere(df)
    df3 = converter.combine_with_headers(sample_data, df2)
    assert "period" in df3.columns
    assert "platform" in df3.columns

def test_export_csv(sample_data, tmp_path):
    converter = JsonConverter("dummy.json", str(tmp_path / "out.csv"))
    processed = converter.preprocess_udsendelser(sample_data.copy())
    df = converter.normalize_udsendelser(processed)
    df2 = converter.normalize_rettighedsholdere(df)
    df3 = converter.combine_with_headers(sample_data, df2)
    converter.export_csv(df3)
    assert (tmp_path / "out.csv").exists()

def test_json_conversion_runs(sample_json, tmp_path):
    """Ensure JsonConverter runs end-to-end without errors."""
    output_path = tmp_path / "converted.csv"
    converter = JsonConverter(str(sample_json), str(output_path))

    df = converter.run()
    converter.export_csv(df)

    assert output_path.exists()
    assert isinstance(df, pd.DataFrame)
    assert "navn" in df.columns  # Expanded from rettighedshaver
