# School_Management_System

Django REST API for the Scholaris school management frontend.

## Run locally

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows; `source .venv/bin/activate` elsewhere
pip install -r requirements.txt
cd Managementsystem
python manage.py migrate
python manage.py seed_dev       # optional: dev superuser + a small base dataset
python manage.py runserver 127.0.0.1:8000
```

`seed_dev` creates a local sign-in account; its credentials are in
`Managementsystem/core/management/commands/seed_dev.py`. Local development only.

The API lives under `/api/` (`/api/accounts/auth/login/` issues JWTs). The frontend's
origin must be allowed by CORS: the defaults cover `localhost:5180`, `localhost:5173` and
`localhost:8080`; override with a comma-separated `CORS_ALLOWED_ORIGINS` environment variable.

Tests: `python manage.py test`

## Configuration

Everything environment-specific is read from the environment, or from a `.env` file
beside `manage.py`. See `Managementsystem/.env.example`; `.env` is git-ignored and
real secrets never belong in `settings.py`.

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Required whenever `DJANGO_DEBUG=False`; startup fails without it rather than using a default. |
| `DJANGO_DEBUG` | `False` on any deployed server. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames. Render's own hostname is added automatically. |
| `CORS_ALLOWED_ORIGINS` | The frontend's origin, scheme included. Empty outside debug, so it must be set. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Needed for session/form POSTs behind HTTPS, e.g. the admin. |
| `DATABASE_URL` | Postgres when set, otherwise the local SQLite file. |
| `RUN_SEED` / `SEED_ADMIN_PASSWORD` | See below. |

With `DJANGO_DEBUG=False` the standard hardening switches on: HTTPS redirect, HSTS,
secure cookies, `nosniff` and `X-Frame-Options: DENY`. `manage.py check --deploy`
reports no issues once a real key is set.

## Deploying

`render.yaml` is a Render blueprint: creating a Blueprint from this repo provisions
the web service and a managed Postgres database, runs `build.sh` (install,
`collectstatic`, `migrate`, optional seed), and starts gunicorn. `/healthz/` is the
health check — it is the only endpoint that answers without a token.

Enter the secrets in the Render dashboard (`sync: false` in the blueprint keeps them
out of git). To load the demo data and the eight role logins, set
`SEED_ADMIN_PASSWORD` to a strong password and `RUN_SEED=1` for the **first deploy
only**, then set it back to `0`.

Two limits of the free tier to know about:

- **Uploads are not durable.** `MEDIA_ROOT` is on the instance's ephemeral disk, so
  student photos and documents are lost on every deploy. Move `MEDIA_ROOT` to object
  storage before anyone relies on them.
- **Free Postgres expires** after its trial period, and free web services sleep after
  15 minutes idle, so the first request after a pause takes about 30 seconds.
