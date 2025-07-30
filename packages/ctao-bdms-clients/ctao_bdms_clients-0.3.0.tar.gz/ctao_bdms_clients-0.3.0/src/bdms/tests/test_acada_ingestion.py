"""Tests for onsite ingestion and replication into the BDMS system using the IngestionClient.

This module contains tests for the IngestionClient class, focusing on the conversion of ACADA paths to Logical File Names (LFNs), the registration of replicas in Rucio,
and the replication of data between Rucio storage elements (RSEs).
"""

import logging
import os
import re
import subprocess
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from shutil import copy2
from urllib.request import urlopen

import numpy as np
import pytest
from astropy.io import fits
from astropy.table import Table
from rucio.client import Client
from rucio.client.downloadclient import DownloadClient
from rucio.client.replicaclient import ReplicaClient
from rucio.client.ruleclient import RuleClient
from rucio.common.exception import RucioException
from rucio.common.utils import adler32
from watchdog.events import FileMovedEvent

from bdms.acada_ingestion import (
    DETECTED_NEW_TRIGGER_FILE,
    INGEST_SUCCESS_MESSAGE,
    TRIGGER_SUFFIX,
    Ingest,
    IngestionClient,
    IngestStatus,
    TriggerFileHandler,
    process_file,
)
from bdms.tests.utils import reset_xrootd_permissions, wait_for_replication_status

LOGGER = logging.getLogger(__name__)

ONSITE_RSE = "STORAGE-1"
OFFSITE_RSE_1 = "STORAGE-2"
OFFSITE_RSE_2 = "STORAGE-3"

TEST_FILE_TRIGGER = "test_file.trigger"


def test_shared_storage(storage_mount_path: Path):
    """Test that the shared storage path is available."""

    msg = f"Shared storage {storage_mount_path} is not available on the client"
    assert storage_mount_path.exists(), msg


def trigger_judge_repairer() -> None:
    """Trigger the rucio-judge-repairer daemon to run once and fix any STUCK rules."""

    try:
        cmd = [
            "./kubectl",
            "exec",
            "deployment/bdms-judge-evaluator",
            "--",
            "/usr/local/bin/rucio-judge-repairer",
            "--run-once",
        ]
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        LOGGER.info("Triggered rucio-judge-repairer daemon: %s", result.stdout)
    except FileNotFoundError as e:
        LOGGER.error("kubectl command not found: %s", str(e))
        raise RuntimeError(
            "kubectl command not found. Ensure kubectl is in the PATH or working directory."
        ) from e
    except subprocess.CalledProcessError as e:
        LOGGER.error("Failed to trigger rucio-judge-repairer daemon: %s", e.stderr)
        raise


def test_acada_to_lfn(storage_mount_path: Path, test_vo: str):
    """Test the acada_to_lfn method of IngestionClient with valid and invalid inputs."""

    ingestion_client = IngestionClient(storage_mount_path, ONSITE_RSE, vo=test_vo)

    # Test Case 1: valid acada_path
    acada_path = (
        f"{ingestion_client.data_path}/{ingestion_client.vo}/{ingestion_client.scope}/DL0/LSTN-01/events/2023/10/13/"
        "Subarray_SWAT_sbid008_obid00081_0.fits.fz"
    )

    expected_lfn = (
        f"/{ingestion_client.vo}/{ingestion_client.scope}/DL0/LSTN-01/events/2023/10/13/"
        "Subarray_SWAT_sbid008_obid00081_0.fits.fz"
    )
    lfn = ingestion_client.acada_to_lfn(acada_path=acada_path)

    msg = f"Expected {expected_lfn}, got {lfn}"
    assert lfn == expected_lfn, msg

    # Test Case 2: Non-absolute acada_path (empty string)
    with pytest.raises(ValueError, match="acada_path must be absolute"):
        ingestion_client.acada_to_lfn(acada_path="")

    # Test Case 3: Non-absolute acada_path (relative path)
    with pytest.raises(ValueError, match="acada_path must be absolute"):
        ingestion_client.acada_to_lfn(acada_path="./test.fits")

    # Test Case 4: acada_path not within data_path
    invalid_acada_path = "/invalid/path/file.fits.fz"
    with pytest.raises(ValueError, match="is not within data_path"):
        ingestion_client.acada_to_lfn(acada_path=invalid_acada_path)

    # Test Case 5: acada_path does not start with <vo>/<scope>
    wrong_prefix_path = (
        f"{ingestion_client.data_path}/wrong_vo/wrong_scope/DL0/LSTN-01/file.fits.fz"
    )
    with pytest.raises(ValueError, match="must start with"):
        ingestion_client.acada_to_lfn(acada_path=wrong_prefix_path)

    # Test Case 6: acada_path starts with <vo> but wrong <scope>
    wrong_scope_path = f"{ingestion_client.data_path}/{ingestion_client.vo}/wrong_scope/DL0/LSTN-01/file.fits.fz"
    with pytest.raises(ValueError, match="must start with"):
        ingestion_client.acada_to_lfn(acada_path=wrong_scope_path)


@pytest.mark.usefixtures("_auth_proxy")
def test_check_replica_exists(
    storage_mount_path: Path,
    test_scope: str,
    onsite_test_file: tuple[Path, str],
    test_vo: str,
):
    """Test the check_replica_exists method of IngestionClient."""

    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo=test_vo,
        scope=test_scope,
    )

    acada_path, _ = onsite_test_file

    # Generate the LFN
    lfn = ingestion_client.acada_to_lfn(acada_path)

    # Test Case 1: No replica exists yet
    msg = f"Expected no replica for LFN {lfn} before registration"
    assert not ingestion_client.check_replica_exists(lfn), msg

    # Register the replica in Rucio
    ingestion_client.add_onsite_replica(acada_path)

    # Test Case 2: Replica exists with a valid PFN
    msg = f"Expected replica to exist for LFN {lfn} after registration"
    assert ingestion_client.check_replica_exists(lfn), msg

    # Test Case 3: Non-existent LFN
    nonexistent_lfn = lfn + ".nonexistent"
    msg = f"Expected no replica for nonexistent LFN {nonexistent_lfn}"
    assert not ingestion_client.check_replica_exists(nonexistent_lfn), msg


@pytest.fixture
def file_location(request):
    return request.getfixturevalue(request.param)


@pytest.mark.parametrize(
    ("file_location", "metadata_dict"),
    [
        (
            "subarray_test_file",
            {
                "observatory": "CTA",
                "start_time": "2025-02-04T21:34:05",
                "end_time": "2025-02-04T21:43:12",
                "subarray_id": 0,
                "sb_id": 2000000066,
                "obs_id": 2000000200,
            },
        ),
        (
            "tel_trigger_test_file",
            {
                "observatory": "CTA",
                "start_time": "2025-02-04T21:34:05",
                "end_time": "2025-02-04T21:43:11",
                "tel_ids": [1],
                "sb_id": 2000000066,
                "obs_id": 2000000200,
            },
        ),
        (
            "tel_events_test_file",
            {
                "observatory": "CTA",
                "start_time": "2025-04-01T15:25:02",
                "end_time": "2025-04-01T15:25:03",
                "sb_id": 0,
                "obs_id": 0,
            },
        ),
    ],
    indirect=["file_location"],
)
@pytest.mark.usefixtures("_auth_proxy")
@pytest.mark.verifies_usecase("UC-110-1.1.1")
def test_add_onsite_replica_with_minio_fits_file(
    file_location: str,
    metadata_dict: dict,
    test_scope: str,
    tmp_path: Path,
    storage_mount_path,
    test_vo: str,
    caplog,
):
    """Test the add_onsite_replica method of IngestionClient using a dummy file."""

    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo=test_vo,
        scope=test_scope,
    )

    filename = str(file_location).split("/")[-1]
    acada_path = storage_mount_path / test_vo / test_scope / filename
    acada_path.parent.mkdir(parents=True, exist_ok=True)
    copy2(file_location, str(acada_path))
    reset_xrootd_permissions(storage_mount_path)

    # Use add_onsite_replica to register the replica
    lfn, skipped = ingestion_client.add_onsite_replica(acada_path=acada_path)

    # Verify the LFN matches the expected LFN
    expected_lfn = ingestion_client.acada_to_lfn(acada_path)
    msg = f"Expected LFN {expected_lfn}, got {lfn}"
    assert lfn == expected_lfn, msg

    msg = "Expected the file to be newly ingested, but it was skipped"
    assert not skipped, msg

    # Download the file using the LFN
    download_spec = {
        "did": f"{ingestion_client.scope}:{lfn}",
        "base_dir": str(tmp_path),
        "no_subdir": True,
    }
    download_client = DownloadClient()
    download_client.download_dids([download_spec])

    # Verify the downloaded file
    download_path = tmp_path / lfn.lstrip("/")
    msg = f"Download failed at {download_path}"
    assert download_path.is_file(), msg

    msg = "Downloaded file content does not match the original."
    assert adler32(download_path) == adler32(file_location), msg

    # Check for don't ingest again if its already registered
    caplog.clear()
    lfn_check, skipped_check = ingestion_client.add_onsite_replica(
        acada_path=acada_path
    )
    msg = f"LFN mismatch on second ingestion attempt: expected {lfn}, got {lfn_check}"
    assert lfn_check == lfn, msg

    msg = (
        "Expected the file to be skipped on second ingestion, but it was ingested again"
    )
    assert skipped_check, msg

    msg = f"'Replica already exists for lfn '{lfn}', skipping' in caplog records"
    assert f"Replica already exists for lfn '{lfn}', skipping" in [
        r.message for r in caplog.records
    ], msg

    # Retrieve metadata using the DIDClient
    did_client = Client()
    retrieved_metadata = did_client.get_metadata(
        scope=ingestion_client.scope, name=lfn, plugin="JSON"
    )

    # Verify the metadata matches the expected metadata
    for key, value in metadata_dict.items():
        msg = (
            f"Metadata mismatch for key '{key}'. "
            f"Expected: {value}, Got: {retrieved_metadata.get(key)}"
        )
        assert retrieved_metadata.get(key) == value, msg


def test_rses():
    """Test that the expected RSEs are configured."""
    client = Client()
    result = list(client.list_rses())

    rses = [r["rse"] for r in result]
    msg = f"Expected RSE {ONSITE_RSE} not found in {rses}"
    assert ONSITE_RSE in rses, msg

    msg = f"Expected RSE {OFFSITE_RSE_1} not found in {rses}"
    assert OFFSITE_RSE_1 in rses, msg

    msg = f"Expected RSE {OFFSITE_RSE_2} not found in {rses}"
    assert OFFSITE_RSE_2 in rses, msg


@pytest.fixture
def pre_existing_lfn(
    onsite_test_file: tuple[Path, str],
    test_scope: str,
    test_vo: str,
) -> str:
    """Fixture to provide an LFN for a replica pre-registered in Rucio without using IngestionClient."""

    # Construct the LFN manually based on the test file and scope
    acada_path, _ = onsite_test_file
    relative_path = str(acada_path).split(f"{test_vo}/{test_scope}/", 1)[-1]
    lfn = f"/{test_vo}/{test_scope}/{relative_path}"
    checksum = adler32(acada_path)

    # Construct the DID
    did = {"scope": test_scope, "name": lfn}

    # Register the replica directly using ReplicaClient
    replica_client = ReplicaClient()
    replica = {
        "scope": test_scope,
        "name": lfn,
        "bytes": acada_path.stat().st_size,  # File size
        "adler32": checksum,
    }
    try:
        replica_client.add_replicas(rse=ONSITE_RSE, files=[replica])
    except RucioException as e:
        LOGGER.error(
            "Failed to pre-register replica for LFN %s on %s: %s",
            lfn,
            ONSITE_RSE,
            str(e),
        )
        raise

    # Verify the replica is registered
    replicas = list(replica_client.list_replicas(dids=[did]))
    msg = f"Failed to verify pre-registration of replica for LFN {lfn} on {ONSITE_RSE}"
    assert replicas, msg

    return lfn


@pytest.mark.usefixtures("_auth_proxy")
@pytest.mark.verifies_usecase("UC-110-1.6")
def test_add_offsite_replication_rules(
    pre_existing_lfn: str,
    test_scope: str,
    test_vo: str,
    storage_mount_path: Path,
    tmp_path: Path,
    onsite_test_file: tuple[Path, str],
    caplog,
):
    """Test the add_offsite_replication_rules method of IngestionClient."""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo=test_vo,
        scope=test_scope,
    )

    # Replicate the ACADA file to two offsite RSEs
    lfn = pre_existing_lfn
    did = {"scope": test_scope, "name": lfn}

    _, test_file_content = onsite_test_file  # Get the test file content

    offsite_rse_expression = "OFFSITE"
    copies = 2
    rule_ids = ingestion_client.add_offsite_replication_rules(
        lfn=lfn,
        offsite_rse_expression=offsite_rse_expression,
        copies=copies,
        lifetime=None,
    )

    rule_id_offsite_1 = rule_ids[0]
    rule_id_offsite_2 = rule_ids[1]
    rule_client = RuleClient()

    # Wait for the first offsite rule to complete (OFFSITE_RSE_1)
    wait_for_replication_status(rule_client, rule_id_offsite_1, expected_status="OK")

    # Verify the replica exists on either OFFSITE_RSE_1 or OFFSITE_RSE_2 after the first rule
    replica_client = ReplicaClient()
    replicas = next(replica_client.list_replicas(dids=[did]))
    states = replicas.get("states", {})
    msg = f"Expected replica on either {OFFSITE_RSE_1} or {OFFSITE_RSE_2} to be AVAILABLE after first rule: {states}"
    assert (
        states.get(OFFSITE_RSE_1) == "AVAILABLE"
        or states.get(OFFSITE_RSE_2) == "AVAILABLE"
    ), msg

    # Manually trigger the judge-repairer to ensure the second rule doesn't get stuck
    trigger_judge_repairer()

    # Wait for the second offsite rule to complete (OFFSITE_RSE_2)
    wait_for_replication_status(rule_client, rule_id_offsite_2, expected_status="OK")

    # Verify the replica exists on all RSEs
    replica_client = ReplicaClient()
    replicas = next(replica_client.list_replicas(dids=[did]))
    states = replicas.get("states", {})
    LOGGER.info(
        "Replica states for DID %s in test_replicate_acada_data_to_offsite: %s",
        did,
        states,
    )

    msg = f"Expected replica on {ONSITE_RSE} to be AVAILABLE: {states}"
    assert states.get(ONSITE_RSE) == "AVAILABLE", msg

    msg = f"Expected replica on {OFFSITE_RSE_1} to be AVAILABLE: {states}"
    assert states.get(OFFSITE_RSE_1) == "AVAILABLE", msg

    msg = f"Expected replica on {OFFSITE_RSE_2} to be AVAILABLE: {states}"
    assert states.get(OFFSITE_RSE_2) == "AVAILABLE", msg

    # Download the file from OFFSITE_RSE_2 to verify its content
    download_spec = {
        "did": f"{test_scope}:{lfn}",
        "base_dir": str(tmp_path),
        "no_subdir": True,
        "rse": OFFSITE_RSE_2,
    }
    download_client = DownloadClient()
    download_client.download_dids([download_spec])

    # Verify the downloaded file content
    download_path = tmp_path / lfn.lstrip("/")
    msg = f"Download failed at {download_path}"
    assert download_path.is_file(), msg

    downloaded_content = download_path.read_text()
    msg = (
        f"Downloaded file content does not match the original. "
        f"Expected: {test_file_content}, Got: {downloaded_content}"
    )
    assert downloaded_content == test_file_content, msg


@pytest.mark.usefixtures("_auth_proxy")
@pytest.mark.verifies_usecase("UC-110-1.6")
def test_add_offsite_replication_rules_single_copy(
    pre_existing_lfn: str,
    test_scope: str,
    test_vo: str,
    storage_mount_path: Path,
    tmp_path: Path,
    onsite_test_file: tuple[Path, str],
    caplog,
):
    """Test the add_offsite_replication_rules method of IngestionClient with a single copy (copies=1)."""

    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo=test_vo,
        scope=test_scope,
    )

    # Replicate the ACADA file to one offsite RSE
    lfn = pre_existing_lfn
    did = {"scope": test_scope, "name": lfn}

    _, test_file_content = onsite_test_file

    offsite_rse_expression = "OFFSITE"
    copies = 1
    rule_ids = ingestion_client.add_offsite_replication_rules(
        lfn=lfn,
        offsite_rse_expression=offsite_rse_expression,
        copies=copies,
        lifetime=None,
    )

    # Verify that only one rule was created
    msg = f"Expected exactly 1 rule ID, got {len(rule_ids)}: {rule_ids}"
    assert len(rule_ids) == 1, msg

    rule_id_offsite_1 = rule_ids[0]
    rule_client = RuleClient()

    # Wait for the offsite rule to complete
    wait_for_replication_status(rule_client, rule_id_offsite_1, expected_status="OK")

    # Verify the replica exists on exactly one of the offsite RSEs (either OFFSITE_RSE_1 or OFFSITE_RSE_2)
    replica_client = ReplicaClient()
    replicas = next(replica_client.list_replicas(dids=[did]))
    states = replicas.get("states", {})
    LOGGER.info(
        "Replica states for DID %s in test_add_offsite_replication_rules_single_copy: %s",
        did,
        states,
    )
    # Check that the replica exists on exactly one offsite RSE
    offsite_replica_count = sum(
        1 for rse in [OFFSITE_RSE_1, OFFSITE_RSE_2] if states.get(rse) == "AVAILABLE"
    )
    msg = f"Expected exactly 1 offsite replica (on either {OFFSITE_RSE_1} or {OFFSITE_RSE_2}), got {offsite_replica_count}: {states}"
    assert offsite_replica_count == 1, msg

    # Determine which offsite RSE the replica was created on
    target_offsite_rse = (
        OFFSITE_RSE_1 if states.get(OFFSITE_RSE_1) == "AVAILABLE" else OFFSITE_RSE_2
    )

    # Download the file from the target offsite RSE to verify its content
    download_spec = {
        "did": f"{test_scope}:{lfn}",
        "base_dir": str(tmp_path),
        "no_subdir": True,
        "rse": target_offsite_rse,
    }
    download_client = DownloadClient()
    download_client.download_dids([download_spec])

    # Verify the downloaded file content
    download_path = tmp_path / lfn.lstrip("/")
    msg = f"Download failed at {download_path}"
    assert download_path.is_file(), msg
    downloaded_content = download_path.read_text()
    msg = (
        f"Downloaded file content does not match the original. "
        f"Expected: {test_file_content}, Got: {downloaded_content}"
    )
    assert downloaded_content == test_file_content, msg


def test_verify_fits_file(tel_events_test_file):
    from bdms.acada_ingestion import verify_fits_checksum

    with fits.open(tel_events_test_file) as hdul:
        verify_fits_checksum(hdul)


@pytest.fixture
def broken_checksum(tmp_path):
    # create a fits file with a broken checksum
    path = tmp_path / "invalid.fits"

    table = Table({"foo": [1, 2, 3], "bar": [4.0, 5.0, 6.0]})
    hdul = fits.HDUList([fits.PrimaryHDU(), fits.BinTableHDU(table)])
    hdul.writeto(path, checksum=True)

    # break it
    with path.open("rb+") as f:
        # FITS files are stored in blocks of 2880 bytes
        # first chunk should be the primary header
        # second chunk the header of the bintable
        # third chunk the payload of the bintable
        # we write garbage somewhere into the payload of the table
        f.seek(2 * 2880 + 10)
        f.write(b"\x12\x34\xff")
    return path


def test_verify_fits_file_invalid_checksum(broken_checksum):
    from bdms.acada_ingestion import FITSVerificationError, verify_fits_checksum

    with fits.open(broken_checksum) as hdul:
        with pytest.raises(FITSVerificationError, match="CHECKSUM verification failed"):
            verify_fits_checksum(hdul)


def test_ingest_init(storage_mount_path):
    """Test that Ingest initializes correctly with given parameters."""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo="ctao",
        scope="acada",
    )

    ingest = Ingest(
        client=ingestion_client,
        top_dir=storage_mount_path,
        num_workers=3,
        lock_file_path=storage_mount_path / "lockfile.lock",
        polling_interval=0.5,
        check_interval=0.2,
    )
    assert ingest.client == ingestion_client
    assert ingest.top_dir == storage_mount_path
    assert ingest.num_workers == 3
    assert ingest.lock_file_path == storage_mount_path / "lockfile.lock"
    assert ingest.polling_interval == 0.5
    assert ingest.check_interval == 0.2
    assert not ingest.stop_event.is_set()  # check stop_event initial state
    assert hasattr(ingest, "result_queue")
    assert hasattr(ingest, "task_counter")
    assert hasattr(ingest, "submitted_tasks")
    assert ingest.task_counter == 0
    assert len(ingest.submitted_tasks) == 0


def test_check_directory_valid(storage_mount_path, tmp_path, caplog):
    """Test _check_directory with a valid, readable directory."""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo="ctao",
        scope="acada",
    )

    ingest_instance = Ingest(
        client=ingestion_client,
        top_dir=tmp_path,
        num_workers=1,
        lock_file_path=storage_mount_path / "bdms_ingest.lock",
        polling_interval=0.5,
        check_interval=0.5,
    )

    ingest_instance.top_dir = tmp_path
    ingest_instance._check_directory()


def test_check_directory_invalid(storage_mount_path, tmp_path, caplog):
    """Test _check_directory with an invalid directory."""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo="ctao",
        scope="acada",
        logger=LOGGER,
    )

    invalid_dir = tmp_path / "nonexistent"

    ingest_instance = Ingest(
        client=ingestion_client,
        top_dir=invalid_dir,
        num_workers=1,
        lock_file_path=storage_mount_path / "bdms_ingest.lock",
        polling_interval=0.5,
        check_interval=0.5,
    )

    with pytest.raises(RuntimeError, match=f"Cannot read directory {invalid_dir}"):
        ingest_instance._check_directory()
    assert f"Cannot read directory {invalid_dir}" in caplog.text


@pytest.mark.usefixtures("_auth_proxy")
def test_process_file_success(
    storage_mount_path, caplog, onsite_test_file, test_vo, test_scope
):
    """Test for checking successful ingestion with trigger file clean-up, depends on IngestionClient"""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo=test_vo,
        scope=test_scope,
    )

    acada_path, _ = onsite_test_file
    test_file = acada_path
    trigger_file = Path(str(test_file) + TRIGGER_SUFFIX)
    trigger_file.symlink_to(test_file)
    result = process_file(ingestion_client, str(test_file))
    assert result == IngestStatus.SUCCESS
    assert not trigger_file.exists()
    assert INGEST_SUCCESS_MESSAGE in caplog.text


@pytest.mark.usefixtures("_auth_proxy")
def test_process_file_skipped(
    storage_mount_path, caplog, onsite_test_file, test_vo, test_scope
):
    """Test for checking skipped ingestion when replica already exists"""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo=test_vo,
        scope=test_scope,
    )

    acada_path, _ = onsite_test_file
    test_file = acada_path
    trigger_file = Path(str(test_file) + TRIGGER_SUFFIX)
    trigger_file.symlink_to(test_file)
    process_file(ingestion_client, str(test_file))
    caplog.clear()
    result = process_file(ingestion_client, str(test_file))
    assert result == IngestStatus.SKIPPED
    assert "Replica already exists" in caplog.text


@pytest.mark.usefixtures("_auth_proxy")
def test_process_file_failure(storage_mount_path, caplog, tmp_path):
    """Test for checking failure for invalid file paths"""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo="ctao",
        scope="acada",
    )

    invalid_file = tmp_path / "invalid_file.fits"
    invalid_file.write_text("dummy content")
    trigger_file = Path(str(invalid_file) + TRIGGER_SUFFIX)
    trigger_file.symlink_to(invalid_file)

    # The file path is outside the data_path causing a ValueError in acada_to_lfn
    result = process_file(ingestion_client, str(invalid_file))

    # Verify the function returns FAILURE status instead of raising an exception
    assert result == IngestStatus.FAILURE

    # Check for the actual error message that gets logged
    assert "Exception in process_file" in caplog.text
    # Verify the file path is in the error message
    assert str(invalid_file) in caplog.text

    # Verify that no success message was logged
    assert INGEST_SUCCESS_MESSAGE not in caplog.text

    # Trigger file should still exist since ingestion failed
    msg = "Trigger file should not be removed when ingestion fails"
    assert trigger_file.exists(), msg


def test_trigger_file_handler_init(storage_mount_path):
    """Test TriggerFileHandler initialization."""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo="ctao",
        scope="acada",
    )

    ingest_instance = Ingest(
        client=ingestion_client,
        top_dir=storage_mount_path,
        num_workers=1,
        lock_file_path=storage_mount_path / "bdms_ingest.lock",
        polling_interval=0.5,
        check_interval=0.5,
    )

    handler = TriggerFileHandler(ingest_instance)
    assert handler.ingest == ingest_instance


def test_trigger_file_handler_on_moved_missing_data_file(
    storage_mount_path, tmp_path, caplog
):
    """Test on_moved skips when data file is missing."""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo="ctao",
        scope="acada",
    )

    ingest_instance = Ingest(
        client=ingestion_client,
        top_dir=storage_mount_path,
        num_workers=1,
        lock_file_path=storage_mount_path / "bdms_ingest.lock",
        polling_interval=0.5,
        check_interval=0.5,
    )

    handler = TriggerFileHandler(ingest_instance)
    trigger_file = tmp_path / TEST_FILE_TRIGGER
    data_file = tmp_path / "test_file"

    # Create symlink to non-existent data file
    trigger_file.symlink_to(data_file)

    # Create FileMovedEvent (simulating ln -s)
    event = FileMovedEvent(src_path=str(data_file), dest_path=str(trigger_file))
    handler.on_moved(event)

    assert (
        f"Data file {data_file} for trigger {trigger_file} does not exist, skipping"
        in caplog.text
    )
    assert (
        DETECTED_NEW_TRIGGER_FILE not in caplog.text
    )  # Skips processing since the data file is missing


def test_trigger_file_handler_on_moved_success(
    storage_mount_path, tmp_path, onsite_test_file, test_vo, test_scope, caplog
):
    """Test on_moved successfully processing a valid trigger file."""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo=test_vo,
        scope=test_scope,
    )

    ingest_instance = Ingest(
        client=ingestion_client,
        top_dir=storage_mount_path,
        num_workers=1,
        lock_file_path=storage_mount_path / "bdms_ingest.lock",
        polling_interval=0.5,
        check_interval=0.5,
    )

    # Create ProcessPoolExecutor for the ingest instance
    with ProcessPoolExecutor(max_workers=1) as executor:
        ingest_instance.executor = executor

        handler = TriggerFileHandler(ingest_instance)
        acada_path, _ = onsite_test_file
        test_file = acada_path
        trigger_file = Path(str(test_file) + TRIGGER_SUFFIX)
        trigger_file.symlink_to(test_file)

        # Create FileMovedEvent (simulating ln -s)
        event = FileMovedEvent(src_path=str(test_file), dest_path=str(trigger_file))

        # Record initial state
        initial_task_counter = ingest_instance.task_counter
        initial_total_tasks = ingest_instance.total_tasks_submitted
        initial_submitted_tasks_count = len(ingest_instance.submitted_tasks)

        handler.on_moved(event)

        # Verify the expected log message
        msg = f"'Detected new trigger file {trigger_file}, submitting data file {test_file}' in caplog"
        assert (
            f"Detected new trigger file {trigger_file}, submitting data file {test_file}"
            in caplog.text
        ), msg

        # Verify task submission metrics were updated
        assert ingest_instance.task_counter == initial_task_counter + 1
        assert ingest_instance.total_tasks_submitted == initial_total_tasks + 1
        assert len(ingest_instance.submitted_tasks) == initial_submitted_tasks_count + 1

        # Verify the task was submitted with correct file path
        submitted_task_files = list(ingest_instance.submitted_tasks.values())
        assert str(test_file) in submitted_task_files

        # Give some time for the task to potentially complete
        time.sleep(0.5)


def test_trigger_file_handler_on_moved_stop_event_set(
    storage_mount_path, tmp_path, caplog
):
    """Test on_moved skips processing when stop_event is set."""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo="ctao",
        scope="acada",
    )

    ingest_instance = Ingest(
        client=ingestion_client,
        top_dir=storage_mount_path,
        num_workers=1,
        lock_file_path=storage_mount_path / "bdms_ingest.lock",
        polling_interval=0.5,
        check_interval=0.5,
    )

    handler = TriggerFileHandler(ingest_instance)
    trigger_file = tmp_path / TEST_FILE_TRIGGER
    data_file = tmp_path / "test_file"
    data_file.write_text("data")  # Data file exists
    trigger_file.symlink_to(data_file)

    # Create FileMovedEvent
    event = FileMovedEvent(src_path=str(data_file), dest_path=str(trigger_file))

    # Set stop event
    ingest_instance.stop_event.set()

    # Record initial state
    initial_task_counter = ingest_instance.task_counter
    initial_total_tasks = ingest_instance.total_tasks_submitted

    try:
        handler.on_moved(event)

        # Should not process anything when stop_event is set
        assert ingest_instance.task_counter == initial_task_counter
        assert ingest_instance.total_tasks_submitted == initial_total_tasks
        assert DETECTED_NEW_TRIGGER_FILE not in caplog.text

    finally:
        ingest_instance.stop_event.clear()  # Reset for other tests


def test_trigger_file_handler_on_moved_directory_event(
    storage_mount_path, tmp_path, caplog
):
    """Test on_moved skips directory events."""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo="ctao",
        scope="acada",
    )

    ingest_instance = Ingest(
        client=ingestion_client,
        top_dir=storage_mount_path,
        num_workers=1,
        lock_file_path=storage_mount_path / "bdms_ingest.lock",
        polling_interval=0.5,
        check_interval=0.5,
    )

    handler = TriggerFileHandler(ingest_instance)
    trigger_dir = tmp_path / "some_directory.trigger"
    source_dir = tmp_path / "source_directory"
    source_dir.mkdir()
    trigger_dir.mkdir()

    # Create directory move event
    event = FileMovedEvent(src_path=str(source_dir), dest_path=str(trigger_dir))
    event.is_directory = True  # mark as directory event

    # Record initial state
    initial_task_counter = ingest_instance.task_counter
    initial_total_tasks = ingest_instance.total_tasks_submitted

    handler.on_moved(event)

    # Should not process directory events
    assert ingest_instance.task_counter == initial_task_counter
    assert ingest_instance.total_tasks_submitted == initial_total_tasks
    assert DETECTED_NEW_TRIGGER_FILE not in caplog.text


def test_trigger_file_handler_on_moved_with_actual_processing(
    storage_mount_path, tmp_path, onsite_test_file, test_vo, test_scope, caplog
):
    """Test on_moved with successfully processing a valid trigger file."""
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo=test_vo,
        scope=test_scope,
    )

    ingest_instance = Ingest(
        client=ingestion_client,
        top_dir=storage_mount_path,
        num_workers=1,
        lock_file_path=storage_mount_path / "bdms_ingest.lock",
        polling_interval=0.5,
        check_interval=0.5,
    )

    # Start the result processing thread manually for this test
    result_thread = threading.Thread(
        target=ingest_instance._process_results, daemon=True
    )
    result_thread.start()

    with ProcessPoolExecutor(max_workers=1) as executor:
        ingest_instance.executor = executor

        handler = TriggerFileHandler(ingest_instance)
        acada_path, _ = onsite_test_file
        test_file = acada_path
        trigger_file = Path(str(test_file) + TRIGGER_SUFFIX)
        trigger_file.symlink_to(test_file)

        # Create FileMovedEvent
        event = FileMovedEvent(src_path=str(test_file), dest_path=str(trigger_file))

        handler.on_moved(event)

        # Wait for processing to complete
        timeout = 10.0
        start_time = time.time()
        processed = False

        while time.time() - start_time < timeout:
            # Check if task was completed (removed from submitted_tasks)
            if len(ingest_instance.submitted_tasks) == 0:
                processed = True
                break
            time.sleep(0.1)

        # Stop the result processing thread
        ingest_instance.stop_event.set()
        result_thread.join(timeout=2.0)

        # Verify processing occurred
        msg = "Task was not processed within timeout"
        assert processed, msg

        msg = f"'Detected new trigger file {trigger_file}, submitting data file {test_file}' in caplog"
        assert (
            f"Detected new trigger file {trigger_file}, submitting data file {test_file}"
            in caplog.text
        ), msg

        # Check that a result was logged (either success, failure, or error)
        result_logged = any(
            phrase in caplog.text
            for phrase in ["Processed file", "failed:", "Exception in process_file"]
        )
        msg = "No processing result was logged"
        assert result_logged, msg


def test_sequential_exclusion_lock_prevention(storage_mount_path, tmp_path):
    """Test that a second daemon instance cannot start when first is already running.

    This test validates sequential exclusion: when one ingestion daemon is already
    running and has acquired the lock, any subsequent attempt to start another
    daemon instance should fail with a clear error message.
    """
    lock_file = tmp_path / "sequential_test.pid"

    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo="ctao",
        scope="acada",
    )

    # Create first instance
    instance1 = Ingest(
        client=ingestion_client,
        top_dir=tmp_path,
        lock_file_path=lock_file,
        num_workers=1,
        polling_interval=0.1,
        check_interval=0.1,
    )

    # Create second instance with same lock file
    instance2 = Ingest(
        client=ingestion_client,
        top_dir=tmp_path,
        lock_file_path=lock_file,
        num_workers=1,
        polling_interval=0.1,
        check_interval=0.1,
    )

    results = {}
    first_instance_started = threading.Event()

    def run_first_instance():
        """Run first instance - should succeed and run until manually stopped."""
        try:
            # signal: about to start daemon
            first_instance_started.set()
            instance1.run()
            results["first"] = "success"
        except Exception as e:
            results["first"] = f"error: {str(e)}"

    def run_second_instance():
        """Try to run second instance while first is running - should fail with lock conflict."""
        try:
            # Verify first instance has actually acquired the lock
            lock_acquired_timeout = 15.0
            start_wait = time.time()
            while time.time() - start_wait < lock_acquired_timeout:
                if lock_file.exists():
                    break
                time.sleep(0.1)
            else:
                results["second"] = "first_instance_never_acquired_lock"
                return

            # This should fail because first instance holds the lock
            instance2.run()
            results["second"] = "unexpected_success"  # Should not reach here
        except RuntimeError as e:
            error_msg = str(e)
            if "Another ingestion process is already running" in error_msg:
                results["second"] = f"expected_lock_conflict: {str(e)}"
            else:
                results["second"] = f"unexpected_runtime_error: {str(e)}"
        except Exception as e:
            results["second"] = f"unexpected_error: {str(e)}"

    # Start first instance with non-daemon thread
    thread1 = threading.Thread(target=run_first_instance, daemon=False)
    thread1.start()

    # Wait for first instance to signal it's starting
    msg = "First instance failed to start"
    assert first_instance_started.wait(timeout=10), msg

    # Give first instance time to acquire lock and initialize
    time.sleep(3.0)

    # Verify first instance has acquired lock with content validation
    msg = "First instance should have created PID file"
    assert lock_file.exists(), msg

    # Read PID and verify it's valid
    pid_content = lock_file.read_text().strip()
    msg = f"PID file should contain a number, got: {pid_content}"
    assert pid_content.isdigit(), msg

    # Verify the lock file contains current process PID or a valid PID
    current_pid = os.getpid()
    stored_pid = int(pid_content)
    # The stored PID should be current process since we're running in same process
    msg = f"Expected PID {current_pid}, got {stored_pid}"
    assert stored_pid == current_pid, msg

    # Now try to start second instance - this should fail
    thread2 = threading.Thread(target=run_second_instance, daemon=False)
    thread2.start()

    # Wait for second instance to complete with better timeout handling
    # FileLock timeout is 10 seconds, so we give a bit more time
    thread2.join(timeout=15)

    # Explicit check for thread completion
    if thread2.is_alive():
        # Force stop and fail the test
        instance1.stop_event.set()
        thread1.join(timeout=5)
        pytest.fail("Second instance thread did not complete within expected timeout")

    # Stop first instance now that we've tested the lock
    instance1.stop_event.set()
    thread1.join(timeout=10)

    # Ensure first thread also terminates
    if thread1.is_alive():
        pytest.fail("First instance thread did not terminate within timeout")

    # Verify results
    msg = f"Second instance should have completed. Results: {results}"
    assert "second" in results, msg

    # More specific assertion for expected lock conflict
    second_result = results["second"]
    msg = f"Second instance should have failed with lock conflict. Got: {second_result}"
    assert second_result.startswith("expected_lock_conflict"), msg

    # Verify the error message is the expected one from Ingest class
    msg = f"Expected specific error message, got: {second_result}"
    assert "Another ingestion process is already running" in second_result, msg

    # First instance should have run successfully (we stopped it manually)
    if "first" in results:
        msg = f"First instance should succeed, got: {results['first']}"
        assert results["first"] == "success", msg

    # Improved cleanup verification with timeout-based checking
    cleanup_timeout = 5.0
    start_cleanup_wait = time.time()
    while time.time() - start_cleanup_wait < cleanup_timeout:
        if not lock_file.exists():
            break
        time.sleep(0.1)

    msg = "PID file should be cleaned up after first instance stops"
    assert not lock_file.exists(), msg

    # logging
    LOGGER.info("Sequential exclusion test completed successfully")
    LOGGER.info("First instance: %s", results.get("first", "stopped manually"))
    LOGGER.info("Second instance correctly failed with: %s", second_result)


def test_concurrent_exclusion_lock_prevention(storage_mount_path, tmp_path):
    """Test FileLock behavior under true concurrent access - simultaneous daemon startup attempts.

    This test validates real concurrent scenario where multiple daemon instances
    attempt to acquire the same lock simultaneously, simulating race conditions
    that occur in production environments.
    """
    lock_file = tmp_path / "concurrent_test.pid"

    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo="ctao",
        scope="acada",
    )

    # Create both instances
    instance1 = Ingest(
        client=ingestion_client,
        top_dir=tmp_path,
        lock_file_path=lock_file,
        num_workers=1,
        polling_interval=0.1,
        check_interval=0.1,
    )
    instance2 = Ingest(
        client=ingestion_client,
        top_dir=tmp_path,
        lock_file_path=lock_file,
        num_workers=1,
        polling_interval=0.1,
        check_interval=0.1,
    )

    results = {}

    # Synchronization barrier - both threads wait here until released
    start_barrier = threading.Barrier(3)  # 2 worker threads + 1 main thread

    def run_instance(instance_id, instance):
        """Run instance - both will try to start simultaneously."""
        try:
            # Wait for barrier - ensures simultaneous start
            start_barrier.wait()  # All threads start together!

            instance.run()
            results[instance_id] = "success"
        except RuntimeError as e:
            if "Another ingestion process is already running" in str(e):
                results[instance_id] = f"lock_conflict: {str(e)}"
            else:
                results[instance_id] = f"unexpected_error: {str(e)}"
        except Exception as e:
            results[instance_id] = f"error: {str(e)}"

    # Create both threads
    thread1 = threading.Thread(
        target=run_instance, args=("first", instance1), daemon=False
    )
    thread2 = threading.Thread(
        target=run_instance, args=("second", instance2), daemon=False
    )

    # Start both threads - they will wait at the barrier
    thread1.start()
    thread2.start()

    # Give threads time to reach barrier
    time.sleep(0.5)

    # Release the barrier - both threads start simultaneously
    start_barrier.wait()

    # Wait for both to complete the lock acquisition attempt
    thread1.join(timeout=15)
    thread2.join(timeout=15)

    # Stop whichever instance succeeded
    if "first" in results and results["first"] == "success":
        instance1.stop_event.set()
    if "second" in results and results["second"] == "success":
        instance2.stop_event.set()

    # Ensure threads complete
    if thread1.is_alive():
        instance1.stop_event.set()
        thread1.join(timeout=5)
    if thread2.is_alive():
        instance2.stop_event.set()
        thread2.join(timeout=5)

    # Verify results - Exactly ONE should succeed, ONE should fail
    msg = f"Both instances should complete, got: {results}"
    assert len(results) == 2, msg

    success_count = sum(1 for result in results.values() if result == "success")
    conflict_count = sum(1 for result in results.values() if "lock_conflict" in result)

    msg = f"Exactly ONE instance should succeed, got {success_count}: {results}"
    assert success_count == 1, msg

    msg = f"Exactly ONE instance should get lock conflict, got {conflict_count}: {results}"
    assert conflict_count == 1, msg

    # Verify the lock conflict has correct error message
    conflict_result = [r for r in results.values() if "lock_conflict" in r][0]
    msg = "Expected 'Another ingestion process is already running' message in conflict result"
    assert "Another ingestion process is already running" in conflict_result, msg

    # Verify cleanup
    cleanup_timeout = 5.0
    start_cleanup = time.time()
    while time.time() - start_cleanup < cleanup_timeout:
        if not lock_file.exists():
            break
        time.sleep(0.1)
    msg = "Lock file should be cleaned up"
    assert not lock_file.exists(), msg

    LOGGER.info("True Concurrency tests: %s", results)
    LOGGER.info("Real concurrent lock acquisition tested successfully!")


def acada_write_test_files(
    storage_mount_path, test_vo, test_scope, n_files=7
) -> list[Path]:
    """Represents ACADA writing test files to the storage mount path."""

    test_dir = storage_mount_path / test_vo / test_scope
    test_dir.mkdir(parents=True, exist_ok=True)

    # Create seven dummy FITS files
    data_files = []
    rng = np.random.default_rng()
    for i in range(n_files):
        data_file = test_dir / f"testfile_{i}_20250609.fits"
        hdu = fits.PrimaryHDU(rng.random((50, 50)))
        hdu.writeto(data_file, overwrite=True, checksum=True)
        data_files.append(data_file)

        LOGGER.info("Created test file: %s", data_file)

    # Move permission reset before daemon start to avoid timing issues
    reset_xrootd_permissions(storage_mount_path)
    time.sleep(1.0)  # Allow permissions to be applied

    return data_files


def acada_create_trigger_symlink(data_file, creation_results):
    """Represents creating a trigger symlink for a given data file."""

    try:
        trigger_file = Path(str(data_file) + TRIGGER_SUFFIX)
        trigger_file.symlink_to(data_file)
        LOGGER.info("Created trigger file: %s -> %s", trigger_file, data_file)

        # Verify creation was successful
        if trigger_file.exists() and trigger_file.is_symlink():
            creation_results.append({"file": str(data_file), "status": "success"})
        else:
            creation_results.append(
                {"file": str(data_file), "status": "creation_failed"}
            )
    except Exception as e:
        LOGGER.exception("Failed to create trigger for %s: %s", data_file, e)
        creation_results.append({"file": str(data_file), "status": f"error: {str(e)}"})

    return creation_results


def ensure_files_ingested(data_files, storage_mount_path, test_scope, timeout_s=120):
    """Ensure that all files are ingested by checking the IngestStatus."""

    replica_client = ReplicaClient()

    timeout_at = time.time() + timeout_s

    data_file_entries = [
        {
            "file": str(data_file),
            "expected_lfn": f"/{data_file.relative_to(storage_mount_path)}",
            "found": False,
        }
        for data_file in data_files
    ]

    while time.time() < timeout_at and not all(
        status["found"] for status in data_file_entries
    ):
        for data_file_entry in data_file_entries:
            if not data_file_entry["found"]:
                try:
                    replicas = list(
                        replica_client.list_replicas(
                            dids=[
                                {
                                    "scope": test_scope,
                                    "name": data_file_entry["expected_lfn"],
                                }
                            ]
                        )
                    )
                    if not replicas:
                        LOGGER.info(
                            "No replica found for %s", data_file_entry["expected_lfn"]
                        )
                    else:
                        LOGGER.info(
                            "Replica found for %s: %s",
                            data_file_entry["expected_lfn"],
                            replicas[0],
                        )
                        data_file_entry["found"] = True
                except Exception:
                    LOGGER.exception(
                        "Failed to list replicas for %s",
                        data_file_entry["expected_lfn"],
                    )
        time.sleep(1.0)

    if not all(status["found"] for status in data_file_entries):
        pytest.fail(f"Not all replicas found for files: {data_files}")


@pytest.mark.usefixtures(
    "_auth_proxy", "lock_for_ingestion_daemon", "disable_ingestion_daemon"
)
@pytest.mark.verifies_usecase("UC-110-1.1.4")
def test_ingest_parallel_submission(storage_mount_path, caplog, test_vo, test_scope):
    """Test parallel file processing: creates multiple FITS files simultaneously and verifies that the
    daemon can detect, process, and ingest them efficiently using parallel workers.
    """
    ingestion_client = IngestionClient(
        data_path=storage_mount_path,
        rse=ONSITE_RSE,
        vo=test_vo,
        scope=test_scope,
    )

    ingest_instance = Ingest(
        client=ingestion_client,
        top_dir=storage_mount_path,
        num_workers=4,
        lock_file_path=storage_mount_path / "bdms_ingest.lock",
        polling_interval=0.5,
        check_interval=0.5,
    )

    data_files = acada_write_test_files(storage_mount_path, test_vo, test_scope)

    # Daemon startup with exception handling
    daemon_exception = None
    daemon_started = threading.Event()

    def run_daemon():
        """Run daemon with exception capture."""
        nonlocal daemon_exception
        try:
            daemon_started.set()  # Signal daemon thread started
            ingest_instance.run()
        except Exception as e:
            daemon_exception = e
            LOGGER.exception("Daemon failed with exception: %s", str(e))

    # Start daemon with non-daemon thread for reliability
    daemon_thread = threading.Thread(target=run_daemon, daemon=False)
    daemon_thread.start()

    # Wait for daemon thread to start
    msg = "Daemon thread failed to start"
    assert daemon_started.wait(timeout=10), msg

    # Daemon initialization verification
    daemon_init_timeout = 20.0  # Increased timeout for robust initialization
    daemon_init_start = time.time()
    required_conditions = {
        "lock_acquired": False,
        "result_thread_started": False,
        "pool_started": False,
        "monitoring_started": False,
        "observer_started": False,
    }

    while time.time() - daemon_init_start < daemon_init_timeout:
        # Check for daemon startup failure early
        if daemon_exception:
            pytest.fail(f"Daemon failed during initialization: {daemon_exception}")

        # Check for lock acquisition (critical for daemon operation)
        if ingest_instance.lock_file_path.exists():
            required_conditions["lock_acquired"] = True

        # Check log messages for initialization steps
        log_text = caplog.text
        if "Result processing thread started" in log_text:
            required_conditions["result_thread_started"] = True

        # Flexible process pool verification to work with any worker count
        if re.search(r"Started process pool with \d+ workers", log_text):
            required_conditions["pool_started"] = True

        if "Starting continuous polling-based monitoring" in log_text:
            required_conditions["monitoring_started"] = True
        if "File monitoring observer started successfully" in log_text:
            required_conditions["observer_started"] = True

        # Check if all conditions are met
        if all(required_conditions.values()):
            break

        time.sleep(0.2)

    # Verify complete initialization or provide diagnostics
    missing_conditions = [k for k, v in required_conditions.items() if not v]
    if missing_conditions:
        ingest_instance.stop_event.set()
        daemon_thread.join(timeout=5)
        pytest.fail(
            f"Daemon initialization incomplete. Missing: {missing_conditions}. Check logs for errors."
        )

    time.sleep(0.5)  # some additional time to stabilize

    # Create trigger files and also track
    trigger_files = []
    natural_start = time.time()

    for data_file in data_files:
        trigger_file = Path(str(data_file) + TRIGGER_SUFFIX)
        trigger_file.symlink_to(data_file)
        trigger_files.append(trigger_file)

    # Test regular detection, looking for MOVE events
    natural_detection_timeout = 30.0
    natural_start = time.time()

    while time.time() - natural_start < natural_detection_timeout:
        # Look for actual processing
        if caplog.text.count("Detected new trigger file") > 0:
            break
        time.sleep(1.0)

    # Count events after the loop completes
    move_events_detected = caplog.text.count("MOVE Event received")

    # Wait for processing with concurrency monitoring
    processing_timeout = 120.0
    processing_start = time.time()
    processed_files = set()
    max_concurrent_samples = []

    while time.time() - processing_start < processing_timeout:
        # Sample concurrent tasks frequently to catch parallelism
        current_concurrent = len(ingest_instance.submitted_tasks)
        max_concurrent_samples.append(current_concurrent)

        # Check processing results
        for data_file in data_files:
            success_pattern = f"Processed file {data_file} with result success"
            skipped_pattern = f"Processed file {data_file} with result skipped"

            if str(data_file) not in processed_files:
                if success_pattern in caplog.text or skipped_pattern in caplog.text:
                    processed_files.add(str(data_file))

        if len(processed_files) == 7:
            break

        if "Fatal error in result processing thread" in caplog.text:
            break

        time.sleep(0.1)  # Sample frequently to catch concurrency

    assert len(processed_files) == 7

    # Record ingestion workflow completion time
    workflow_end_time = time.time()

    # Stop the daemon
    ingest_instance.stop_event.set()
    daemon_thread.join(timeout=10)

    if daemon_thread.is_alive():
        pytest.fail("Ingest Daemon thread did not terminate within timeout")

    # Verify results
    msg = "Process pool startup failed"
    assert "Started process pool with 4 workers" in caplog.text, msg

    msg = "Result processing thread startup failed"
    assert "Result processing thread started" in caplog.text, msg

    # Verify trigger files were cleaned up during successful processing
    remaining_triggers = sum(1 for tf in trigger_files if tf.exists())
    msg = f"Expected all trigger files to be cleaned up, {remaining_triggers} remain"
    assert remaining_triggers == 0, msg

    # Verify clean shutdown
    msg = "Lock file not cleaned up"
    assert not ingest_instance.lock_file_path.exists(), msg

    msg = "Daemon shutdown not logged"
    assert "Stopped ingestion daemon" in caplog.text, msg

    msg = "Result thread shutdown not logged"
    assert "Result processing thread stopped" in caplog.text, msg

    # Clean up data files
    for data_file in data_files:
        if data_file.exists():
            data_file.unlink()

    # Statistics
    # Ingestion workflow time: from trigger detection to ingestion with replication completion
    max_concurrent_observed = (
        max(max_concurrent_samples) if max_concurrent_samples else 0
    )
    max_concurrent_tracked = ingest_instance.max_concurrent_tasks

    detection_to_completion_time = workflow_end_time - natural_start
    processing_rate = (
        len(processed_files) / detection_to_completion_time
        if detection_to_completion_time > 0
        else 0
    )

    total_submitted = ingest_instance.total_tasks_submitted
    tasks_cleaned_up = len(ingest_instance.submitted_tasks) == 0
    max_concurrent_final = max(max_concurrent_tracked, max_concurrent_observed)
    parallel_achieved = max_concurrent_final >= 2

    # Summary
    status = "parallel" if parallel_achieved else "sequential"

    LOGGER.info("=== Parallel Ingestion Test Results ===")
    LOGGER.info(
        "Files processed: %d/7 in %.1fs",
        len(processed_files),
        detection_to_completion_time,
    )
    LOGGER.info("Processing rate: %.1f files/sec", processing_rate)
    LOGGER.info("Max concurrent tasks: %d (mode: %s)", max_concurrent_final, status)
    LOGGER.info("Total tasks submitted: %d", total_submitted)
    LOGGER.info("Task cleanup successful: %s", tasks_cleaned_up)
    LOGGER.info("Event detection: %d move events", move_events_detected)


def fetch_ingestion_daemon_metrics():
    """Fetch metrics from the ingestion daemon to verify its operation."""

    response = urlopen("http://bdms-ingestion-daemon:8000/")

    assert response.status == 200, "Ingestion daemon metrics are not responding"

    n_tasks_metrics = {}
    for line in response.readlines():
        line = line.decode("utf-8").strip()
        if line.startswith("n_tasks_"):
            LOGGER.info("Ingestion daemon metrics: %s", line)
            key, value = line.split(" ", 1)
            n_tasks_metrics[key] = float(value)

    return n_tasks_metrics


@pytest.mark.usefixtures(
    "_auth_proxy", "lock_for_ingestion_daemon", "enable_ingestion_daemon"
)
@pytest.mark.verifies_usecase("UC-110-1.1.4")
def test_ingest_parallel_submission_with_live_daemon(storage_mount_path, test_vo):
    """Test parallel file processing with an already running daemon."""

    # with live test, the daemon is deployed outside of this test, so we need to pick a persistent location, matching the daemon's storage mount path
    # note that if kind cluster creation fixture is used, the directory can be unique per test session
    # this test does only checks that the files are consumed, not that they are replicated

    test_scope = "test_scope_persistent"

    n_tasks_metrics_before_test = fetch_ingestion_daemon_metrics()

    for tf in (storage_mount_path / test_vo / test_scope).glob("*" + TRIGGER_SUFFIX):
        if tf.exists():
            LOGGER.info("Cleaning up existing trigger file: %s", tf)
            tf.unlink()

    data_files = acada_write_test_files(storage_mount_path, test_vo, test_scope)

    creation_results = []
    for data_file in data_files:
        acada_create_trigger_symlink(data_file, creation_results)

    trigger_files = [Path(str(df) + TRIGGER_SUFFIX) for df in data_files]

    timeout = 120.0
    start_time = time.time()

    remaining_triggers = 0
    while time.time() - start_time < timeout:
        # Verify trigger files were cleaned up during successful processing
        remaining_triggers = sum(1 for tf in trigger_files if tf.exists())

        if remaining_triggers == 0:
            LOGGER.info("All trigger files consumed up successfully, exiting test.")
            break
        else:
            LOGGER.info(
                "Waiting for trigger files to be cleaned up, %s remain.",
                remaining_triggers,
            )

        time.sleep(1.0)  # Sample frequently to catch concurrency

    assert remaining_triggers == 0, "Expected all trigger files to be consumed up"

    ensure_files_ingested(data_files, storage_mount_path, test_scope)

    # make sure that metrics are available from the daemon
    n_tasks_metrics = fetch_ingestion_daemon_metrics()

    assert n_tasks_metrics["n_tasks_success_created"] < time.time()
    assert n_tasks_metrics["n_tasks_processed_total"] - n_tasks_metrics_before_test[
        "n_tasks_processed_total"
    ] == len(data_files)
    assert (
        n_tasks_metrics["n_tasks_processed_total"]
        - n_tasks_metrics_before_test["n_tasks_processed_total"]
        == n_tasks_metrics["n_tasks_success_total"]
        + n_tasks_metrics["n_tasks_skipped_total"]
    ), "Ingestion daemon metrics do not match expected values"
