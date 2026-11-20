# Restapi-Portfolio1

Technologies used :
- FastAPI with API key header authentication
- SQLAlchemy with PostgreSQL dialect
- Alembic migration

# How to run it
Make sure you already have uv and docker installed
```
git clone https://github.com/floppy-disk916/restapi-portfolio1.git
cd restapi-portfolio1
```
Copy .env.example to .env and fill in your own environment variables
```
cp .env.example .env
docker compose up -d
```
Then access [http://localhost](http://localhost)
