# Deploying the app

## Installation

You will need to make sure [Docker](https://www.docker.com/) is installed on your server, and [docker compose](https://docs.docker.com/compose/) is available.

## Clone the repo onto the server
```bash
git clone https://github.com/brainglobe/brainglobe-data-api-connectivity-frontend
cd brainglobe-data-api-connectivity-frontend
```

## Setting up `.envs/.production` files

You will also need to create a `.envs/.production/.django` file similar to below.
Everything inside `< >` needs to be replaced with your own values.
```
# General
# ------------------------------------------------------------------------------
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=<a long random sequence of letters and numbers>
DJANGO_ADMIN_URL=<url you want your admin interface to appear at>
DJANGO_ALLOWED_HOSTS=<enter the domain name you host the website at>

# Security
# ------------------------------------------------------------------------------
DJANGO_SECURE_SSL_REDIRECT=False

# Gunicorn
# ------------------------------------------------------------------------------
WEB_CONCURRENCY=2

# Redis
# ------------------------------------------------------------------------------
REDIS_URL=redis://redis:6379/0
```

A `.envs/.production/.postgres` file is also required like below. 
Everything inside `< >` needs to be replaced with your own values.
```
# PostgreSQL
# ------------------------------------------------------------------------------
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=brainglobe_data_api_connectivity_frontend
POSTGRES_USER=<a long random sequence of letters and numbers>
POSTGRES_PASSWORD=<a long random sequence of letters and numbers>
```


## Running the app

Build the app:
```bash
docker compose -f docker-compose.production.yml build
```

Run the app:
```bash
docker compose -f docker-compose.production.yml up
```

The first time you run the app, you will also need to run `migrate` to setup the database:
```bash
docker compose -f docker-compose.production.yml run --rm django python manage.py migrate
```

Go to your chosen domain in the browser, and you should see the website.

To stop the app:
```bash
docker compose -f docker-compose.production.yml down
```

**Note**: if you change values in your `.envs` files, you will need to stop and re-start the app to see the effects. If you change the app's dependencies, then you will also need to re-build it.

## Setting up users

To create a super-user for yourself run:
```bash
docker compose -f docker-compose.production.yml run --rm django python manage.py createsuperuser
```

This will prompt you for an email / password to use to access the app. 
This will also give you full access to the admin interface at: `https://neurome.brainglobe.info/DJANGO_ADMIN_URL` (replace DJANGO_ADMIN_URL with the value you set in `.envs/.production/.django`) and the main website.

To add more users:
- login to the admin interface
- Click 'Add' next to Users
- Enter an email and password
- If you want them to be able to login to the admin interface, tick 'staff status'
- If you want them to have full admin rights tick 'superuser status'

## Setting up automated deletion of old results

Result entries in the database (and their associated csv files) can be deleted by running:
```bash
docker compose -f docker-compose.production.yml run --rm django python manage.py cleanup_results
```

We recommend running this command automatically at regular intervals with cron:
```bash
# Open the crontab for editing
crontab -e
```

Inside the file put something like:
```bash
# Every 5 minutes, connect to the docker container and run the cleanup command
*/5 * * * * cd /path/to/cloned/repo && docker compose -f docker-compose.production.yml exec -T django python manage.py cleanup_results >> ~/log/cleanup_results.log 2>&1
```

Check it appears in the list of cron jobs at:
```bash
crontab -l
```

## Caching of neurome data

### Download via pooch

Before every app startup, a management command is run automatically to check 
that the neurome datasets (CSV files) have been downloaded onto the server via pooch: `python manage.py fetch_neurome_data`. 
If they are already present, they will not be downloaded again.

These files are put into a docker volume to allow them to persist between restarts of the containers.
If you would like to force re-download of the datasets (e.g. because a new version is available), you will need to:

```bash
# Make sure containers are down
docker compose -f docker-compose.production.yml down

# Remove the volume containing the neurome datasets
docker volume rm brainglobe-data-api-connectivity-frontend_production_neurome_data
```

The next time the app is started, the datasets will be downloaded fresh.

### In-memory caching

Once the app has started up, the first visit to the queries page (for each sex) will load the stored CSV datasets into a Connections object. This object is cached in-memory, so all subsequent commands will re-use it (avoiding loading from file repeatedly).

Note: you have to be careful with the `WEB_CONCURRENCY` setting (inside [.envs/.production/.django](#setting-up-envsproduction-files)). `WEB_CONCURRENCY` determines the number of gunicorn workers that will be created on app startup (in production). Some important points:
- More workers allow more requests to be handled at the same time
- More workers == higher memory usage. Each worker will have its own copy of the male / female connections object held in memory.

If you start seeing memory errors in your logs, you either need to reduce the number of workers or swap to a larger EC2 instance that has more RAM.
