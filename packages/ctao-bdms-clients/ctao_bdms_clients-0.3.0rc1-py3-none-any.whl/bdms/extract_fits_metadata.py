"""Functions to extract metadata from input files."""

import logging

import numpy as np
from protozfits import File

# Configure logger
logger = logging.getLogger(__name__)

# COMMON HEADER
start_time = "DataStream.DATE"

# COMMON DATA
origin = "DataStream.ORIGIN"
sb_id = "DataStream.sb_id"
obs_id = "DataStream.obs_id"

# -- FOR TEL_TRIG
tel_ids = "DataStream.tel_ids"

# -- FOR TEL_SUB
subarray_id = "DataStream.subarray_id"

METADATA_TEL = {
    "HEADER": {
        "observatory": origin,
        "start_time": start_time,
        "end_time": "Events.DATEEND",
    },
    "PAYLOAD": {
        "sb_id": sb_id,
        "obs_id": obs_id,
    },
}

METADATA_SUB = {
    "HEADER": {
        "observatory": origin,
        "start_time": start_time,
        "end_time": "SubarrayEvents.DATEEND",
    },
    "PAYLOAD": {
        "subarray_id": subarray_id,
        "sb_id": sb_id,
        "obs_id": obs_id,
    },
}

METADATA_TRIG = {
    "HEADER": {
        "observatory": origin,
        "start_time": start_time,
        "end_time": "Triggers.DATEEND",
    },
    "PAYLOAD": {
        "tel_ids": tel_ids,
        "sb_id": sb_id,
        "obs_id": obs_id,
    },
}

#: Mapping from DataStream.PBFHEAD to the metadata items we want to collect
METADATA_SCHEMAS = {
    "DL0v1.Trigger.DataStream": METADATA_TRIG,
    "DL0v1.Subarray.DataStream": METADATA_SUB,
    "DL0v1.Telescope.DataStream": METADATA_TEL,
}


def extract_metadata_from_headers(hdul):
    """Extract metadata from FITS headers of hdul."""
    all_headers = {}
    for hdu in hdul:
        if hdu.is_image:
            continue
        all_headers[hdu.name] = dict(hdu.header)

    try:
        all_headers["DataStream"]
    except KeyError:
        logger.error("No DataStream HDU found in the FITS file.")
        return {}

    pbfhead = all_headers["DataStream"]["PBFHEAD"]
    schema = METADATA_SCHEMAS.get(pbfhead)
    if schema is None:
        logger.error(
            "The PBFHEAD %r does not correspond to any known FITS type.", pbfhead
        )
        return {}

    logger.debug("Headers extracted: %s", all_headers.keys())

    metadata = {}
    for value_name, metadata_path in schema["HEADER"].items():
        extname, header_key = metadata_path.split(".")
        table = all_headers[extname][header_key]
        metadata[value_name] = table

    return metadata


def extract_metadata_from_data(path):
    """Extract metadata from zFITS payload in path."""
    with File(path) as f:
        if not hasattr(f, "DataStream"):
            return {}

        pbfhead = f.DataStream.header["PBFHEAD"]
        schema = METADATA_SCHEMAS.get(pbfhead)
        if schema is None:
            logger.error(
                "The PBFHEAD %r does not correspond to any known FITS type.", pbfhead
            )
            return {}

        metadata = {}
        for value_name, metadata_path in schema["PAYLOAD"].items():
            hdu, column = metadata_path.split(".")
            row = getattr(f, hdu)[0]
            metadata[value_name] = getattr(row, column)

            if isinstance(metadata[value_name], np.ndarray):
                # Convert numpy array to a Python list
                metadata[value_name] = metadata[value_name].tolist()

            logger.debug(
                "Value '%s' from '%s' extracted. (renamed as '%s')",
                column,
                hdu,
                value_name,
            )
        return metadata
