![](https://img.shields.io/badge/Code-Python-informational?style=flat&logo=python&logoColor=white&color=008000)
![](https://img.shields.io/badge/Database-SQLite-informational?style=flat&logo=sqlite&logoColor=white&color=060080)
![](https://img.shields.io/badge/ORM-SQLAlchemy-informational?style=flat&logo=SQLAlchemy&logoColor=white&color=060080)
![](https://img.shields.io/badge/Migrations-Alembic-informational?style=flat&logoColor=white&color=060080)
![](https://img.shields.io/badge/Broker-Redis-informational?style=flat&logo=redis&logoColor=white&color=758000)
![](https://img.shields.io/badge/Tools-Docker-informational?style=flat&logo=docker&logoColor=white&color=802d00)
![](https://img.shields.io/badge/Tools-Poetry-informational?style=flat&logo=poetry&logoColor=white&color=00806b)
![](https://img.shields.io/badge/Tools-Celery-informational?style=flat&logo=celery&logoColor=white&color=4d0080)
![](https://img.shields.io/badge/Tools-pre--commit-informational?style=flat&logo=pre-commit&logoColor=white&color=800029)

This app is used to request rates from [Riskbank](https://www.riksbank.se/en-gb/) via [Swea API](https://developer.api.riksbank.se/api-details#api=swea-api).

# Installation and usage
There are two ways to run the app: **with Docker** or **without Docker**.

## Docker instructions
If you have Docker installed, then clone the project and do the following steps:
- Create ***.env*** file in project root and specify it according to ***.env.example***, or copy ***.env.default***
- Run `docker-compose build` from the project root directory to build images
- Run `docker-compose up` from the project root directory to run containers

## No Docker instructions
To run the app you will need Python of [*3.10.8*](https://www.python.org/downloads/release/python-3108/) version,
[poetry](https://python-poetry.org/) for managing dependencies and [Redis](https://redis.io/) as broker for Celery.
Or you can run test script without Redis and Celery, to do so go to [Debug Instructions](#debug-instructions) section.
If you have tool mentioned above, do the following steps:
- Create ***.env*** file in project root and specify it according to ***.env.example***, or copy ***.env.default***
- Run `poetry install --no-root` to create venv and install all the dependencies
- Run `poetry env activate` to activate venv
- Run `poetry run alembic upgrade head` to run DB migrations
- Run Redis server depending on your OS
- Run `poetry run celery -A app.scheduler.celery worker --loglevel=info` to start Celery worker
- Run `poetry run celery -A app.scheduler.celery beat --loglevel=info` to start Celery beat

*Notice, that worker and beat must be run in different terminals.*

# Debug Instructions
There is a way to manually run task to request small amount of data and insert it into the DB without Celery and Redis.
There is a file ***app/main.py*** which does so. You can just run it with `poetry run python -m app.main` or customize params inside
to change the work of API.

# How It Works
The main task is to make request and store data in DB daily at certain time. For that purposes I use **Celery**. The idea is
that you run docker containers and **Celery Beat** will make task on schedule. The schedule can be configured in
***app/scheduler/celery.py***. The task itself is in ***app/scheduler/tasks.py***.

For storing data **SQLite** is used. **SQLAlchemy** is used as ORM and **Alembic** for migrations. The
***app/db/database.py*** has **Base** model for creating DB models and **SessionLocal** for interaction with DB.
***app/db/database.py*** has **Rate** model where requested rates are stored.
The file ***app/db/\_\_init\_\_.py*** must contain **Base** model and all other models, as they are used in ***migrations/env.py***.
***alembic.ini*** contains path to DB file in **87-th** line.

The interaction with API is done via **SweaRatesAPI** from ***app/api.py***. The principle is to request all available
series and get data of each one. The important fact to know, is that by default API allows to send 5 requests
per minute ([docs](https://www.riksbank.se/en-gb/statistics/interest-rates-and-exchange-rates/retrieving-interest-rates-and-exchange-rates-via-api/faq--the-api-for-interest-rates-and-exchange-rates/)), so there is a logic to follow this restriction and hold on requests if limit is hit.

There is also a logger to keep track of main actions done by the app, ***app/logger.py***.
