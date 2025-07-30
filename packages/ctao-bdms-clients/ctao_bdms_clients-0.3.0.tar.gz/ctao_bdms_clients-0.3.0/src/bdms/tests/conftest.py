import json
import logging
import os
import subprocess as sp
import time
from datetime import datetime
from pathlib import Path
from secrets import token_hex

import pytest
from filelock import FileLock
from rucio.client.scopeclient import ScopeClient

from bdms.tests.utils import download_test_file, reset_xrootd_permissions

USER_CERT = os.getenv("RUCIO_CFG_CLIENT_CERT", "/opt/rucio/etc/usercert.pem")
USER_KEY = os.getenv("RUCIO_CFG_CLIENT_KEY", "/opt/rucio/etc/userkey.pem")

# Define on-site storage related variables
STORAGE_MOUNT_PATH = Path(os.getenv("STORAGE_MOUNT_PATH", "/storage-1"))
STORAGE_PROTOCOL = "root"  # e.g., root, davs, gsiftp
STORAGE_HOSTNAME = "rucio-storage-1"  # on-site storage container hostname


def pytest_configure():
    # gfal is overly verbose on info (global default), reduce a bit
    logging.getLogger("gfal2").setLevel(logging.WARNING)


@pytest.fixture(scope="session")
def storage_mount_path():
    """Provide the STORAGE_MOUNT_PATH as a fixture"""
    return STORAGE_MOUNT_PATH


@pytest.fixture(scope="session")
def test_user():
    return "root"


@pytest.fixture(scope="session")
def _auth_proxy(tmp_path_factory):
    """Auth proxy needed for accessing RSEs"""
    # Key has to have 0o600 permissions, but due to the way we
    # we create and mount it, it does not. We copy to a tmp file
    # set correct permissions and then create the proxy

    try:
        sp.run(
            [
                "voms-proxy-init",
                "-valid",
                "9999:00",
                "-cert",
                USER_CERT,
                "-key",
                USER_KEY,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    except sp.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        raise pytest.fail(f"VOMS proxy failed: {error_msg}")


@pytest.fixture(scope="session")
def test_vo():
    return "ctao.dpps.test"


@pytest.fixture(scope="session")
def test_scope(test_user):
    """To avoid name conflicts and old state, use a unique scope for the tests"""
    # length of scope is limited to 25 characters
    random_hash = token_hex(2)
    date_str = f"{datetime.now():%Y%m%d_%H%M%S}"
    scope = f"t_{date_str}_{random_hash}"

    sc = ScopeClient()
    sc.add_scope(test_user, scope)
    return scope


@pytest.fixture(scope="session")
def subarray_test_file():
    """Fixture to download a subarray test file"""
    path = "acada-small/DL0/ARRAY/ctao-n-acada/acada-adh/triggers/2025/02/04/SUB000_SWAT000_20250204T213405_SBID0000000002000000066_OBSID0000000002000000200_SUBARRAY_CHUNK000.fits.fz"
    return download_test_file(path)


@pytest.fixture(scope="session")
def tel_trigger_test_file():
    """Fixture to download a telescope trigger test file"""
    path = "acada-small/DL0/ARRAY/ctao-n-acada/acada-adh/triggers/2025/02/04/SUB000_SWAT000_20250204T213405_SBID0000000002000000066_OBSID0000000002000000200_TEL_CHUNK000.fits.fz"
    return download_test_file(path)


@pytest.fixture(scope="session")
def tel_events_test_file():
    """Fixture to download a telescope events test file"""
    path = "acada-small/DL0/LSTN-01/ctao-n-acada/acada-adh/events/2025/02/04/TEL001_SDH0000_20250204T213354_SBID0000000002000000066_OBSID0000000002000000200_CHUNK001.fits.fz"
    return download_test_file(path)


@pytest.fixture
def onsite_test_file(
    storage_mount_path: Path, test_scope: str, test_vo: str
) -> tuple[Path, str]:
    """Create a dummy file in the shared storage for testing."""

    unique_id = f"{datetime.now():%Y%m%d_%H%M%S}_{token_hex(8)}"
    filename = f"testfile_{unique_id}.txt"

    test_file_path = storage_mount_path / test_vo / test_scope / filename
    test_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write a small test content (simulating a .fits.fz file with minimal content for testing)
    test_file_content = f"Test file with random content: {unique_id}"
    test_file_path.write_text(test_file_content)

    # need to change file permissions of created directories so that
    # the xrootd still can read and write there
    reset_xrootd_permissions(storage_mount_path)

    return test_file_path, test_file_content


def run_kubectl(args: list[str]) -> str:
    """Run a kubectl command with the given arguments and return the output."""
    result = sp.run(
        ["./kubectl"] + args,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"kubectl command failed: {result.stderr}")

    return result.stdout.strip()


def wait_for_deployment_ready(deployment_name, replicas):
    """Wait for a deployment to be ready with the specified number of replicas."""

    timeout_stop_at = time.time() + 300
    while True:
        result = run_kubectl(["get", deployment_name, "-o", "json"])
        ready_replicas = json.loads(result)["status"].get("readyReplicas", 0)

        if ready_replicas >= replicas:
            logging.info(
                "%s deployment is ready with %s replicas.",
                deployment_name,
                ready_replicas,
            )
            break

        if time.time() > timeout_stop_at:
            raise TimeoutError(
                f"Timeout while waiting for {deployment_name} deployment to be ready."
            )

        logging.info(
            "Waiting for %s deployment to be ready. Current ready replicas: %s, expected: %s till timeout in %s s",
            deployment_name,
            ready_replicas,
            replicas,
            int(timeout_stop_at - time.time()),
        )

        time.sleep(1)


def deployment_scale(daemon_name: str, replicas: int = 1) -> None:
    """Scale a deployment to a specific number of replicas."""

    deployment_name = "deployment/bdms-" + daemon_name

    run_kubectl(
        [
            "scale",
            deployment_name,
            f"--replicas={replicas}",
        ]
    )

    if replicas > 0:
        wait_for_deployment_ready(deployment_name, replicas)

    # there is a delay between demon writing lock file and the daemon starting to process trigger files
    time.sleep(3)

    # wait for any terminating pods to finish.
    # they tend to linger around and while they do not count as replicas, they may still interfere with tests by modifying the trigger files.
    while True:
        result = run_kubectl(["get", "pods"])

        if "Terminating" not in result:
            break

        logging.info("Waiting for any Terminating pods to disappear...")
        time.sleep(5)


@pytest.fixture
def enable_repearer_daemon():
    """Fixture to enable the repeater daemon during tests."""

    deployment_scale("judge-repairer", 1)
    yield
    deployment_scale("judge-repairer", 0)


@pytest.fixture
def enable_ingestion_daemon():
    """Fixture to enable the ingestion daemon during tests."""

    deployment_scale("ingestion-daemon", 1)
    yield
    deployment_scale("ingestion-daemon", 0)


@pytest.fixture
def disable_ingestion_daemon():
    """Fixture to suspend the ingestion daemon during tests."""
    deployment_scale("ingestion-daemon", 0)


@pytest.fixture
def lock_for_ingestion_daemon():
    """Fixture to prevent daemon tests from running simultaneously."""

    with FileLock(STORAGE_MOUNT_PATH / "ingestion_daemon.lock"):
        yield
