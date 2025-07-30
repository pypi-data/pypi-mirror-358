import threading
import time
from pathlib import Path
from shutil import copy2

import numpy as np
import pytest
import yaml
from astropy.io import fits
from rucio.client.downloadclient import DownloadClient
from rucio.client.replicaclient import ReplicaClient
from rucio.common.utils import adler32

from bdms.acada_ingest_cli import main as ingest_cli
from bdms.acada_ingest_cli import parse_args_and_config
from bdms.tests.utils import reset_xrootd_permissions

ONSITE_RSE = "STORAGE-1"


@pytest.mark.usefixtures("_auth_proxy", "lock_for_ingestion_daemon")
@pytest.mark.parametrize("dry_run", [True, False], ids=["dry_run", "no_dry_run"])
def test_cli_ingestion(
    storage_mount_path, test_vo, test_scope, subarray_test_file, tmp_path, dry_run
):
    """
    Test CLI ACADA ingestion.
    """
    filename = Path(subarray_test_file).name
    acada_path = (
        storage_mount_path / test_vo / test_scope / "test_cli_ingestion" / filename
    )
    acada_path.parent.mkdir(parents=True, exist_ok=True)
    copy2(subarray_test_file, str(acada_path))
    reset_xrootd_permissions(storage_mount_path)

    expected_lfn = f"/{acada_path.relative_to(storage_mount_path)}"
    lock_file = tmp_path / "cli_test.lock"

    def run_daemon():
        args = [
            f"--data-path={storage_mount_path}",
            f"--rse={ONSITE_RSE}",
            f"--vo={test_vo}",
            f"--scope={test_scope}",
            "--workers=1",
            f"--lock-file={lock_file}",
            "--polling-interval=0.5",
            "--disable-metrics",
            f"--log-file={tmp_path / 'daemon.log'}",
        ]

        if dry_run:
            args.append("--dry-run")

        ingest_cli(args=args)

    # Start daemon
    daemon_thread = threading.Thread(target=run_daemon, daemon=True)
    daemon_thread.start()
    time.sleep(1.0)  # time for daemon to initialize

    if not dry_run:
        trigger_file = Path(str(acada_path) + ".trigger")
        trigger_file.symlink_to(acada_path.relative_to(acada_path.parent))

        # Wait for ingestion to complete
        replica_client = ReplicaClient()
        for _ in range(30):
            try:
                replicas = list(
                    replica_client.list_replicas(
                        dids=[{"scope": test_scope, "name": expected_lfn}]
                    )
                )
                if replicas:
                    break
            except Exception:
                pass
            time.sleep(1.0)
        else:
            pytest.fail(f"No replica found for {expected_lfn}")

        for _ in range(10):
            if not trigger_file.exists():
                break
            time.sleep(1.0)

        # lock file cleanup
        if lock_file.exists():
            lock_file.unlink()

        # Clean up filelock file
        filelock_file = Path(str(lock_file) + ".lock")
        if filelock_file.exists():
            filelock_file.unlink()

        # verify download
        download_spec = {
            "did": f"{test_scope}:{expected_lfn}",
            "base_dir": str(tmp_path),
            "no_subdir": True,
        }

        download_client = DownloadClient()
        download_client.download_dids([download_spec])

        download_path = tmp_path / expected_lfn.lstrip("/")
        assert download_path.is_file(), f"Download failed at {download_path}"
        assert adler32(str(download_path)) == adler32(
            str(subarray_test_file)
        ), "Downloaded file content does not match the original."


def parse_args_and_check_error(args, error_message):
    """
    Helper function to run the CLI and check for expected errors.
    """
    if error_message:
        with pytest.raises(SystemExit) as e:
            parse_args_and_config(args=args)
        assert error_message in e.value.__context__.message
    else:
        # Run without exceptions
        return parse_args_and_config(args=args)


@pytest.mark.parametrize(
    ("port", "error_message"),
    [
        (1234, None),
        (80, "Metrics port must be between 1024"),
        ("invalid_metrics", "Metrics port must be an integer"),
    ],
    ids=["valid_port", "low_port", "invalid_port"],
)
def test_cli_metrics_port_validation(port, error_message):
    """
    Test CLI ACADA ingestion exceptions.
    """

    parse_args_and_check_error(
        [
            f"--metrics-port={port}",
        ],
        error_message,
    )


@pytest.mark.parametrize(
    ("polling_interval", "error_message"),
    [
        (1, None),
        (0, "Polling interval must be positive"),
        ("invalid", "Polling interval must be a number, got"),
    ],
    ids=["valid_offsite", "negative_offsite", "invalid_offsite"],
)
def test_cli_polling_interval(polling_interval, error_message):
    """
    Test CLI ACADA ingestion with offsite copies.
    """
    parse_args_and_check_error(
        [
            f"--polling-interval={polling_interval}",
        ],
        error_message,
    )


@pytest.mark.parametrize(
    ("check_interval", "error_message"),
    [
        (1.0, None),
        (0.0, "Check interval must be positive"),
        ("invalid", "Check interval must be a number, got "),
    ],
    ids=["valid_check_interval", "zero_check_interval", "invalid_check_interval"],
)
def test_cli_check_interval_validation(check_interval, error_message):
    """
    Test CLI ACADA ingestion with check interval validation.
    """

    parse_args_and_check_error(
        [
            f"--check-interval={check_interval}",
        ],
        error_message,
    )


@pytest.mark.usefixtures("_auth_proxy", "lock_for_ingestion_daemon")
def test_cli_ingestion_parallel(storage_mount_path, test_vo, test_scope, tmp_path):
    """Test CLI with 7 files and 4 workers for parallel ingestion."""

    test_dir = storage_mount_path / test_vo / test_scope
    test_dir.mkdir(parents=True, exist_ok=True)

    test_files = []
    rng = np.random.default_rng()
    for i in range(7):
        test_file = test_dir / f"testfile_{i}_20250609.fits"
        hdu = fits.PrimaryHDU(rng.random((50, 50)))
        hdu.writeto(test_file, overwrite=True, checksum=True)
        test_files.append(test_file)

    reset_xrootd_permissions(storage_mount_path)

    lock_file = tmp_path / "ingestion_queue_test.lock"

    def run_daemon():
        ingest_cli(
            args=[
                f"--data-path={storage_mount_path}",
                f"--rse={ONSITE_RSE}",
                f"--vo={test_vo}",
                f"--scope={test_scope}",
                "--workers=4",
                f"--lock-file={lock_file}",
                "--polling-interval=0.5",
                "--disable-metrics",
            ]
        )

    # Start daemon
    daemon_thread = threading.Thread(target=run_daemon, daemon=True)
    daemon_thread.start()
    time.sleep(1.0)

    for test_file in test_files:
        trigger_file = Path(str(test_file) + ".trigger")
        trigger_file.symlink_to(test_file.relative_to(test_file.parent))

    # Wait for all files to be processed, ingestion done
    replica_client = ReplicaClient()
    for _ in range(30):
        processed = 0
        for test_file in test_files:
            lfn = f"/{test_file.relative_to(storage_mount_path)}"
            try:
                replicas = list(
                    replica_client.list_replicas(
                        dids=[{"scope": test_scope, "name": lfn}]
                    )
                )
                if replicas:
                    processed += 1
            except Exception:
                pass

        if processed == 7:
            break
        time.sleep(1.0)
    else:
        pytest.fail("Not all files were processed")

    # Cleanup
    for test_file in test_files:
        test_file.unlink()

    if lock_file.exists():
        lock_file.unlink()

    filelock_file = Path(str(lock_file) + ".lock")
    if filelock_file.exists():
        filelock_file.unlink()


def test_parse_config(tmp_path):
    config_path = tmp_path / "config.yaml"
    with config_path.open("w") as f:
        yaml.dump({"workers": 12, "polling_interval": 60.0}, f)

    args = parse_args_and_config([f"--config={config_path}", "--polling-interval=30.0"])
    # config is parsed
    assert args.workers == 12
    # but cli args override config
    assert args.polling_interval == 30.0
