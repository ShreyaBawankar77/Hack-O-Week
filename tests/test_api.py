import unittest

from app import create_app
from app.extensions import db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret-key-that-is-long-enough-for-hmac-sha256"


class CampusEventsApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def auth_header(self, email, password):
        response = self.client.post("/api/auth/login", json={"email": email, "password": password})
        return {"Authorization": f"Bearer {response.get_json()['access_token']}"}

    def test_event_lifecycle_and_registration(self):
        organizer = {"name": "Organizer", "email": "org@example.com", "password": "secret1", "role": "organizer"}
        student = {"name": "Student", "email": "student@example.com", "password": "secret1"}
        self.assertEqual(self.client.post("/api/auth/register", json=organizer).status_code, 201)
        self.assertEqual(self.client.post("/api/auth/register", json=student).status_code, 201)

        event_data = {"title": "Tech Fest", "description": "Annual technology festival", "venue": "Auditorium", "event_date": "2026-08-01T10:00:00", "capacity": 100}
        create = self.client.post("/api/events", json=event_data, headers=self.auth_header("org@example.com", "secret1"))
        self.assertEqual(create.status_code, 201)
        event_id = create.get_json()["event"]["id"]

        registration = self.client.post(f"/api/events/{event_id}/register", headers=self.auth_header("student@example.com", "secret1"))
        self.assertEqual(registration.status_code, 201)
        self.assertEqual(self.client.get("/api/events").get_json()["events"][0]["registered_count"], 1)


if __name__ == "__main__":
    unittest.main()
