datapipe 0.2.1 (2025-06-27)
---------------------------

Maintenance
-----------

- Now ships with: ctapipe-0.26, pyirf-0.13, and eventio-1.16, ctapipe-io-zfits-0.3 [`!39 <https://gitlab.cta-observatory.org/cta-computing/dpps/datapipe/datapipe/-/merge_requests/39>`__]

datapipe v0.2.0 (2025-06-25)
----------------------------

New Features
~~~~~~~~~~~~

- Add CWL workflows for two use cases:

  * UC-DPPS-130-1.9 (Optimize event selection )
  * UC-DPPS-130-1.6 (Compute an IRF)
  * added workflow to optimize cuts and compute an IRF at once, given an analysis name
    used as prefix for the output files. [`!31 <https://gitlab.cta-observatory.org/cta-computing/dpps/datapipe/datapipe/-/merge_requests/31>`__]

- Added CWL workflow for UC-DPPS-130-1.8 (Merge). [`!33 <https://gitlab.cta-observatory.org/cta-computing/dpps/datapipe/datapipe/-/merge_requests/33>`__]

- Added CWL workflow for UC-DPPS-130-1.4 (Apply Reconstruction Models) [`!36 <https://gitlab.cta-observatory.org/cta-computing/dpps/datapipe/datapipe/-/merge_requests/36>`__]

- UC-DPPS-130-1.3 (Train) is verified by inspection [`!37 <https://gitlab.cta-observatory.org/cta-computing/dpps/datapipe/datapipe/-/merge_requests/37>`__]


Maintenance
~~~~~~~~~~~

- - Update docker URL in the installation page of the documentation to point to the CTAO Harbor, where the image is deployed
  - Simplify the README so that it is appropriate for PyPI. [`!22 <https://gitlab.cta-observatory.org/cta-computing/dpps/datapipe/datapipe/-/merge_requests/22>`__]

- Add auto-generated documentation for the DataPipe CWL workflows, including diagrams. This appears in the *Workflows* section of the Sphinx docs. [`!35 <https://gitlab.cta-observatory.org/cta-computing/dpps/datapipe/datapipe/-/merge_requests/35>`__]

datapipe v0.1.0 (2025-04-17)
--------------------------------

This is the first release of the datapipe package.

New Features
~~~~~~~~~~~~

- CWL workflows covering UC-DPPS-130-1.2, 1.2.1, and 1.2.2
