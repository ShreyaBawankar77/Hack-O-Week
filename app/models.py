from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    events = db.relationship("Event", backref="organizer", lazy=True, cascade="all, delete-orphan")
    registrations = db.relationship("Registration", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    venue = db.Column(db.String(150), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    registrations = db.relationship("Registration", backref="event", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_registrations=False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "venue": self.venue,
            "event_date": self.event_date.isoformat(),
            "capacity": self.capacity,
            "organizer_id": self.organizer_id,
            "registered_count": len(self.registrations),
            "created_at": self.created_at.isoformat(),
        }
        if include_registrations:
            data["registrations"] = [registration.to_dict() for registration in self.registrations]
        return data


class Registration(db.Model):
    __table_args__ = (db.UniqueConstraint("user_id", "event_id", name="unique_user_event_registration"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    registered_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "registered_at": self.registered_at.isoformat(),
        }
