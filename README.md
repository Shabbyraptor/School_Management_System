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
