======================================
SimPipe - the CTAO Simulation Pipeline
======================================

The **CTAO Simulation Production Pipeline (SimPipe)** provides the
software, workflows, and data models for generating Monte Carlo
simulations for the CTAO observatory.

`SimPipe <ctao-simpipe_>`_ is part of the CTAO Data Processing and Preservation System (DPPS).
It integrates all simulation pipeline components into a versioned, reproducible, and validated production system.
This package:

- uses input from the `Calibration Pipeline (CalibPipe) <cta-calibpipe_>`_ to model the CTAO observatory.
- generates simulated events for processing by the `Data Processing Pipeline (DataPipe) <cta-datapipe>`_ to create instrument response functions.
- uses CTAO computing infrastructure through interfaces with the `Workload Management System (WMS) <cta-wms_>`_ and `Bulk Data Management System (BDMS) <cta-bdms_>`_.

SimPipe is the CTAO-specific version of the simtools_ package.
For a detailed user guide, refer to the `simtools documentation`_

.. toctree::
    :maxdepth: 1
    :caption: Contents:
    :hidden:

    installation
    changelog
    chart


Components
==========

- `simtools`_ - toolkit for model parameter management, production configuration, setting, validation workflows.
- `CORSIKA`_ - air shower simulations.
- `sim_telarray`_ - telescope simulations for ray tracing, trigger, read, and camera simulation.
- `simulation models <ctao-simulation-model-database_>`_ - model parameters and production definitions
- `simulation model setting <ctao-simulation-model-parameter-setting_>`_ - workflows for setting, derivation, and validation of model parameters.

.. _ctao-simpipe: https://gitlab.cta-observatory.org/cta-computing/dpps/simpipe/simpipe
.. _simtools: https://github.com/gammasim/simtools
.. _`simtools documentation`: https://gammasim.github.io/simtools/
.. _CORSIKA: https://www.iap.kit.edu/corsika/
.. _sim_telarray: https://gitlab.cta-observatory.org/Konrad.Bernloehr/sim_telarray
.. _ctao-simulation-model-database: https://gitlab.cta-observatory.org/cta-science/simulations/simulation-model/simulation-models
.. _ctao-simulation-model-parameter-setting: https://gitlab.cta-observatory.org/cta-science/simulations/simulation-model/simulation-model-parameter-setting
.. _cta-bdms: http://cta-computing.gitlab-pages.cta-observatory.org/dpps/bdms/bdms/latest/
.. _cta-wms: http://cta-computing.gitlab-pages.cta-observatory.org/dpps/workload/wms/latest/
.. _cta-calibpipe: http://cta-computing.gitlab-pages.cta-observatory.org/dpps/calibrationpipeline/calibpipe/latest/
.. _cta-datapipe: http://cta-computing.gitlab-pages.cta-observatory.org/dpps/datapipe/datapipe/latest/

Primary functions
=================

- Generate simulations of the CTAO observatory instrument response function calculation.
- Manage CTAO simulation models and their parameters.
- Simulate calibration data for the CTAO observatory.
