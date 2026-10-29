# brainglobe-data-api-connectivity-frontend

A frontend to browse brain connectivity data.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Below are instructions for running the web app locally for testing and development. For a production deployment, see the [production docs](./docs/prod_deployment.md).

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

### Adding users

The first time you run the app, you will need to create a superuser to allow access. Run:
```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
```

This will prompt you for an email / password to use to access the app. This will also
give you full access to the admin interface at: `http://localhost:8000/admin`.

## Cleanup result files

Result csv files will be written to `brainglobe_data_api_connectivity_frontend/media/results` as you use the app.

To clean up old results, either delete files in this directory manually or run:
```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py cleanup_results
```

This command will delete all result entries older than settings.RESULT_VALIDITY_MINUTES in the database (and their associated files). RESULT_VALIDITY_MINUTES can be adjusted inside `config/settings/base.py`.

In a production deployment, this command will be run automatically at regular intervals using cron.

## Download new neurome datasets

See the [production docs](./docs/prod_deployment.md#download-via-pooch) for information about how datasets are cached.

To force download of new datasets in a local dev environment, run:

```bash
# Make sure containers are down
docker compose -f docker-compose.local.yml down

# Remove the volume containing the neurome datasets
docker volume rm brainglobe-data-api-connectivity-frontend_neurome_data
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

## Run mypy

Run mypy locally with:
```bash
docker compose -f docker-compose.local.yml run --rm django mypy brainglobe_data_api_connectivity_frontend/
```

Or, as in the [testing section](#run-the-tests), you can enter a running container and call:
```bash
mypy brainglobe_data_api_connectivity_frontend/
```
