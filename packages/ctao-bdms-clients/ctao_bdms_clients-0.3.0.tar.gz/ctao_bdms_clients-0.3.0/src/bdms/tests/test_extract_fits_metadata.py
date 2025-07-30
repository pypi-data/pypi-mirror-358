from astropy.io import fits

from bdms.extract_fits_metadata import (
    extract_metadata_from_data,
    extract_metadata_from_headers,
)


def test_extraction_correct_value_subarray_file(subarray_test_file):
    """Test the extraction of metadata from a FITS file."""
    with fits.open(subarray_test_file) as hdul:
        metadata_header = extract_metadata_from_headers(hdul)

    metadata_payload = extract_metadata_from_data(subarray_test_file)
    metadata_fits = {**metadata_header, **metadata_payload}

    assert len(metadata_fits) > 0, "No metadata found in the SUBARRAY FITS"

    expected_keys_in_fits_file = {
        "observatory": "CTA",
        "start_time": "2025-02-04T21:34:05",
        "end_time": "2025-02-04T21:43:12",
        "subarray_id": 0,
        "sb_id": 2000000066,
        "obs_id": 2000000200,
    }

    for key, value in expected_keys_in_fits_file.items():
        assert metadata_fits[key] == value, f"Expected key '{key}' not found."


def test_extraction_correct_value_tel_trigger_file(tel_trigger_test_file):
    """Test the extraction of metadata from a FITS file."""
    with fits.open(tel_trigger_test_file) as hdul:
        metadata_header = extract_metadata_from_headers(hdul)

    metadata_payload = extract_metadata_from_data(tel_trigger_test_file)
    metadata_fits = {**metadata_header, **metadata_payload}

    assert len(metadata_fits) > 0, "No metadata found in the Telescope TRIGGER FITS"

    expected_keys_in_fits_file = {
        "observatory": "CTA",
        "start_time": "2025-02-04T21:34:05",
        "end_time": "2025-02-04T21:43:11",
        "tel_ids": [1],
        "sb_id": 2000000066,
        "obs_id": 2000000200,
    }

    for key, value in expected_keys_in_fits_file.items():
        assert metadata_fits[key] == value, f"Expected key '{key}' not found."


def test_extraction_correct_value_tel_events_file(tel_events_test_file):
    """Test the extraction of metadata from a FITS file."""
    with fits.open(tel_events_test_file) as hdul:
        metadata_header = extract_metadata_from_headers(hdul)

    metadata_payload = extract_metadata_from_data(tel_events_test_file)
    metadata_fits = {**metadata_header, **metadata_payload}

    assert len(metadata_fits) > 0, "No metadata found in the Telescope EVENTS FITS"

    expected_keys_in_fits_file = {
        "observatory": "CTA",
        "start_time": "2025-04-01T15:25:02",
        "end_time": "2025-04-01T15:25:03",
        "sb_id": 0,
        "obs_id": 0,
    }

    for key, value in expected_keys_in_fits_file.items():
        assert metadata_fits[key] == value, f"Expected key '{key}' not found."


def test_extract_metadata_from_data_incorrect_header(tmp_path):
    """Test the extraction of metadata from an empty FITS file header."""
    fits_file_path = tmp_path / "empty_fits.fits.fz"
    hdul = fits.HDUList([fits.PrimaryHDU()])
    hdul.writeto(fits_file_path, checksum=True)

    with fits.open(fits_file_path) as hdul:
        metadata = extract_metadata_from_headers(hdul)

    assert metadata == {}, "Expected empty metadata in the header"


def test_extract_metadata_from_data_incorrect_data(tmp_path):
    """Test the extraction of metadata from an empty FITS file data."""
    fits_file_path = tmp_path / "empty_fits.fits.fz"
    hdul = fits.HDUList([fits.PrimaryHDU()])
    hdul.writeto(fits_file_path, checksum=True)

    metadata = extract_metadata_from_data(fits_file_path)

    assert metadata == {}, "Expected empty metadata in the payload"
