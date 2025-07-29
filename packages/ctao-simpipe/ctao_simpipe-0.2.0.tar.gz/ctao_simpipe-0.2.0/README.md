# DPPS SimPipe: Integration and Release

The **CTAO DPPS Simulation Production Pipeline (SimPipe)** provides the software, workflows, and data models for generating accurate Monte Carlo simulations of the CTAO observatory.

## Installation

The following installation procedures are implemented in the gitlab CI/CD pipeline:

- simtools is installed using pip
- CORSIKA is installed using a tar-file (currently downloaded from a cloud storage)
- sim_telarray is installed using a tar-file (currently downloaded from a cloud storage); planned to be installed from gitlab
- simulation model databases - no installed required; configuration of secrets for access

Download of corsika / sim_telarray is facilitated by a private upload to the DESY Sync&Share.
Ask the maintainers to provide the token to you and define it in a `.env` file in this repository:

```console
SOFTWARE_DOWNLOAD_SECRET=<the token received from the maintainers>
```

Then run `make build-dev-docker` to build the simpipe container locally.

## SimPipe Maintainer Documentation

The following section is preliminary and the setup is still in development (especially a simplification of the updating process).

### Updating submodules `dpps-aiv-toolkit` and `simtools`

The `dpps-aiv-toolkit` and `simtools` are submodules of the `dpps-simpipe` repository. To update them, follow these steps (identical for both):

```bash
cd dpps-aiv-toolkit
git checkout <branch-or-commit>
cd ..
git add dpps-aiv-toolkit
git commit -m "Update dpps-aiv-toolkit submodule to latest version"
git push
```

### Updating SimPipe components

1. `simtools`:
   - update the submodule in `simtools` to the latest version (see above)
   - update gammasimtools version in `pyproject.toml`
   - update gammasimtools version in `chart/templates/bootstrapSimulationModel.yaml`
   - update gammasimtools version in `Dockerfile`
2. Production and model parameters (SimulationModels):
   - update `SimulationModels` version in `./chart/values.yaml`
3. `CORSIKA` and `sim_telarray`:
   - update versions in `.gitlab-ci.yml` (this is propagated into the docker file)
4. For a new DPPS release:
   - update DPPS release version in aiv-config.yml
