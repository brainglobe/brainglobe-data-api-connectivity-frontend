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
