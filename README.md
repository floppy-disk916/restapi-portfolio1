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

```bash
git clone https://github.com/floppy-disk916/restapi-portfolio1.git
cd restapi-portfolio1
cp .env.example .env

docker compose up --build --detach

To destroy the compose
```bash
docker compose down
