# SecureMe

SecureMe is an early stage email exposure calculator for everyday people.

It turns public email/domain signals and user-confirmed account controls into a clear security score, exposure band, vector string, and prioritized recommendations.

## Stack

- Django + Django REST Framework API
- Supabase
- Redis + Celery
- Vue + Vite
- Docker

## Project structure

```text
Backend/    Django API, Celery app, security scoring module
Frontend/   Vue + Vite app
```

## Local development

```bash
docker compose up --build
```

Then opn:

- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/api/health/
- Django admin: http://localhost:8000/admin/

Run migrations once the backend container is up:

```bash
docker compose exec backend python manage.py migrate
```

## Supabase database

Create a local `.env` file from `.env.example` and set `DATABASE_URL` to your Supabase Postgres connection string.

```bash
cp .env.example .env
```
Then run:

```bash
docker compose up --build
docker compose exec backend python manage.py migrate
```

