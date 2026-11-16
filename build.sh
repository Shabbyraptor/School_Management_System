#!/usr/bin/env bash
# Build step for the deployed API. Render runs this before starting gunicorn.
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

cd Managementsystem

# Collected into STATIC_ROOT and served by WhiteNoise; without it the Django
# admin renders unstyled once DEBUG is off.
python manage.py collectstatic --no-input

python manage.py migrate

# Demo data and the eight role logins. Guarded so a later deploy cannot touch
# real data: set RUN_SEED=1 for the first deploy only, then back to 0.
# SEED_ADMIN_PASSWORD must be set, or every account gets the published dev password.
if [ "$RUN_SEED" = "1" ]; then
  echo "RUN_SEED=1 -> seeding demo data"
  python manage.py seed_dev
else
  echo "RUN_SEED is not 1 -> skipping seed"
fi
