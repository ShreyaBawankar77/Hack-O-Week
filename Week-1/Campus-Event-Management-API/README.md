#WEEK 1 TASK
#Campus Event Management REST API

A Flask backend for campus event creation, management, and student registrations. It uses SQLAlchemy, SQLite by default, and JWT bearer-token authentication.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

The API starts at `http://127.0.0.1:5000`. Set `JWT_SECRET_KEY` and `DATABASE_URL` in production. For MySQL, install a suitable driver (for example `PyMySQL`) and set `DATABASE_URL` to a SQLAlchemy MySQL URL.

## Endpoints

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Create a student or organizer account |
| POST | `/api/auth/login` | Obtain an access token |
| GET | `/api/events` | List events |
| GET | `/api/events/{id}` | Get an event |
| POST | `/api/events` | Create event (organizer) |
| PUT | `/api/events/{id}` | Update event (owning organizer) |
| DELETE | `/api/events/{id}` | Delete event (owning organizer) |
| POST | `/api/events/{id}/register` | Register for an event |
| DELETE | `/api/events/{id}/register` | Cancel own registration |
| GET | `/api/events/{id}/registrations` | View registrations (owning organizer) |

Pass JWTs as `Authorization: Bearer <access_token>`.

### Example event request

```json
{
  "title": "Tech Fest",
  "description": "Annual technology festival",
  "venue": "Main Auditorium",
  "event_date": "2026-08-01T10:00:00",
  "capacity": 200
}
```

## Test

```powershell
python -m unittest discover -s tests
```
