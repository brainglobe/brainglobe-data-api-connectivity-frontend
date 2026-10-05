# brainglobe-data-api-connectivity-frontend

A frontend to browse brain connectivity data.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Running the web app locally

### Docker

Install [Docker](https://www.docker.com/) by following the instructions for your operating system.

Make sure [docker compose](https://docs.docker.com/compose/) is available. Depending on your Docker installation method, you may have to install this separately.

### Clone the repository

```bash
git clone https://github.com/brainglobe/brainglobe-data-api-connectivity-frontend
cd brainglobe-data-api-connectivity-frontend
```

### Run the app with docker

Build the app:
```bash
docker compose -f docker-compose.local.yml build
```

Run the app:
```bash
docker compose -f docker-compose.local.yml up
```

Go to `http://localhost:8000` in your browser, and you should see the website.

To stop the app:
```bash
docker compose -f docker-compose.local.yml down
```

## Run the tests

We use [`pytest`](https://docs.pytest.org/en/stable/) with [`pytest-django`](https://pytest-django.readthedocs.io/en/stable/) for tests.

Tests that are specific to a particular app, go inside that directory e.g. `brainglobe_data_api_connectivity_frontend/connections/tests`. Tests that aren't for a particular app, go in the top-level `tests/` directory.

Run the tests locally with:
```bash
# Creates a temporary container to run the tests, then removes it when complete
docker compose -f docker-compose.local.yml run --rm django pytest
```

If you'd prefer to run the tests inside an already running container, you can do:
```bash
# Enter a bash terminal inside the running django container
docker exec -it brainglobe_data_api_connectivity_frontend_local_django bash

# Source some required env variables like DATABASE_URL, and make sure failures won't exit the bash terminal
source /entrypoint && set +euo pipefail

pytest
```
