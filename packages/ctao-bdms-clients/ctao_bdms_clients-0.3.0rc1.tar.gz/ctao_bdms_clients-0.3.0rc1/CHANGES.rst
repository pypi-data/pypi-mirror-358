BDMS v0.2.1 (2025-06-03)
------------------------

Bugfix release to allow (pre-)production deployment without test storages.

Bug Fixes
~~~~~~~~~

- Allow to further configure first test RSE: set storageclass and make optional. [`!112 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/112>`__]


BDMS 0.2.0 (2025-05-07)
-----------------------


API Changes
~~~~~~~~~~~

- Add basic ingestion of ACADA files (UC-110-1.1.1) [`!76 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/76>`__]

- Replicate Data Products (UC-110-1.6) with test case for copies=2 [`!83 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/83>`__]

- Extraction of metadata from ACADA-LST DL0 FITS files and adding metadata to ingested file (UC-110-1.1.1) [`!85 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/85>`__]

- Add test case for copies=1 for the replication (UC-110-1.6) [`!87 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/87>`__]


Bug Fixes
~~~~~~~~~

- Add missing permissions to fix onsite storage permissions [`!103 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/103>`__]


New Features
~~~~~~~~~~~~

- Adapt one RSE as onsite and exposing its diskspace to client test pod [`!69 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/69>`__]

- Add dcache and its dependencies in the BDMS helm chart (UC-170-1.6) [`!80 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/80>`__]

- Add FITS checksum verification [`!94 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/94>`__]

- Make storage configurable by providing additional config for RSE and also make xrootd image configurable [`!96 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/96>`__]


Maintenance
~~~~~~~~~~~

- Fix rucio server not using correct lfn2pfn algorithm [`!72 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/72>`__]

- Use test_vo fixture for ingestion tests [`!81 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/81>`__]

- Update dpps release for test report and signature matrix [`!82 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/82>`__]

- Update BDMS docs for Rel 0.1 [`!89 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/89>`__]

- Update fts image and toolkit [`!90 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/90>`__]

- Added download_test_file in utils.py to download a FITS file from MinIO server [`!93 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/93>`__]

- Update rucio to 35.7.0 [`!97 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/97>`__]

- Update FTS subchart version [`!99 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/99>`__]

- Resolve Test container build fails due to missing -y in autoremove [`!101 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/101>`__]


Refactoring and Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Update FTS chart to 0.3 to reduce integration test time [`!100 <https://gitlab.cta-observatory.org/cta-computing/dpps/bdms/bdms/-/merge_requests/100>`__]

BDMS v0.1.0 (2025-02-21)
---------------------------

First release of the Bulk Data Management System (BDMS).

* Deployment of Rucio 35.4 using helm.
* Client package pinning the correct rucio and rucio policy package versions.
* Integration tests for DPPS release 0.0 use cases.
