Build and Install
=================

Install
-------

A container image include all software components of SimPipe (especially CORSIKA, sim_telarray, and simtools)
is available through the `CTAO container registry <https://harbor.cta-observatory.org/harbor/projects/4/repositories/simpipe/artifacts-tab>`_.

To pull e.g., the SimPipe container for version 0.1.0:

.. code-block:: shell

    $ podman pull harbor.cta-observatory.org/dpps/simpipe-prod:v0.1.0

Build
-----

Images are build for each SimPipe release by the gitlab CI/CD pipeline and pushed to the CTAO container registry.
