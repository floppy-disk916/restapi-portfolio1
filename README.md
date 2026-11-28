# Restapi-Portfolio1

A FastAPI REST API portfolio project with API key header authentication.

## Technologies

- FastAPI with API key header authentication
- SQLAlchemy + PostgreSQL
- Alembic migrations
- Redis
- Docker Compose + Caddy (reverse proxy)

## How to run

Make sure you have Docker and Docker Compose installed.

```
git clone https://github.com/floppy-disk916/restapi-portfolio1.git
cd restapi-portfolio1
cp .env.example .env

docker compose up --build --detach
```

## Performance


It has been tested with locust and viewed with Jaeger (The Jaeger setup is from deepseek AI)

The latest test: 11/28/2026

Environment:
connection pool size: 20


### Description:

P95 highest spike is between 30s to 35s
while its P50 highest spike is between 0s to 5s
when the number of users is 394

![The locust documentation image](images/Locust-Screenshot.png)

with the bottleneck at GET request method
![Jaeger Screenshot 1](images/JaegerUI-Screenshot-1.png)
![Jaeger Screenshot 2](images/JaegerUI-Screenshot-2.png)


with the problem of QueuePool exhaustion
![GET method 1](images/GET-JaegerUI-1.png)
![GET method 2](images/GET-JaegerUI-2.png)

## Some mistakes about this project i can think of
1. Lack of main idea of the project
Which affects the table models and authentication flows

2. Lack of structure and mature architecture planning
Because this is also a learning project, i didn't prepare an actual structure
and plan that make the project more efficient for users and manageable even for me as a
developer

3. Lack of performance optimization skill
including connection pool and its connection states, transaction, and query optimization

4. Lack of security practices
including row level security and CORS

5. Bad git commit and migration messages
Either not representing atomic significant change, or meaningful commit, or else that i also forget
