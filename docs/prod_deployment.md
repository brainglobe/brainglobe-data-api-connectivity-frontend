# Deploying the app

NOTE: these deployment instructions are a work in progress.

## Installation

You will need to make sure [Docker](https://www.docker.com/) is installed on your server, and [docker compose](https://docs.docker.com/compose/) is available.

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


