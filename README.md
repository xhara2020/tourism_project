# Tourism Portal (Django + PostGIS)

Quickstart (Windows - dev):

1. Create Python virtualenv and activate

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Create Postgres database with PostGIS enabled (see docs). Update `.env` from `.env.example`.

4. Run migrations

```powershell
python manage.py migrate
python manage.py createsuperuser
```

5. Run dev server

```powershell
python manage.py runserver
```
