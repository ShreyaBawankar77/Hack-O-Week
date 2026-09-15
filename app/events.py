from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .extensions import db
from .models import Event, Registration, User

events_bp = Blueprint("events", __name__)


def current_user():
    return db.session.get(User, int(get_jwt_identity()))


def event_payload(data):
    required = ["title", "description", "venue", "event_date", "capacity"]
    missing = [field for field in required if data.get(field) in (None, "")]
    if missing:
        return None, f"Missing required fields: {', '.join(missing)}"
    try:
        event_date = datetime.fromisoformat(data["event_date"].replace("Z", "+00:00"))
        capacity = int(data["capacity"])
        if capacity < 1:
            raise ValueError
    except (TypeError, ValueError):
        return None, "event_date must be ISO-8601 and capacity must be a positive integer"
    return {"title": data["title"].strip(), "description": data["description"].strip(), "venue": data["venue"].strip(), "event_date": event_date, "capacity": capacity}, None


@events_bp.get("")
def list_events():
    events = Event.query.order_by(Event.event_date.asc()).all()
    return jsonify({"events": [event.to_dict() for event in events]})


@events_bp.get("/<int:event_id>")
def get_event(event_id):
    event = db.get_or_404(Event, event_id)
    return jsonify({"event": event.to_dict()})


@events_bp.post("")
@jwt_required()
def create_event():
    user = current_user()
    if user.role != "organizer":
        return jsonify({"error": "Only organizers can create events"}), 403
    payload, error = event_payload(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    event = Event(**payload, organizer_id=user.id)
    db.session.add(event)
    db.session.commit()
    return jsonify({"message": "Event created", "event": event.to_dict()}), 201


@events_bp.put("/<int:event_id>")
@jwt_required()
def update_event(event_id):
    event = db.get_or_404(Event, event_id)
    user = current_user()
    if user.role != "organizer" or event.organizer_id != user.id:
        return jsonify({"error": "Only the event organizer can update this event"}), 403
    payload, error = event_payload(request.get_json(silent=True) or {})
    if error:
        return jsonify({"error": error}), 400
    if payload["capacity"] < len(event.registrations):
        return jsonify({"error": "Capacity cannot be below the registered count"}), 400
    for field, value in payload.items():
        setattr(event, field, value)
    db.session.commit()
    return jsonify({"message": "Event updated", "event": event.to_dict()})


@events_bp.delete("/<int:event_id>")
@jwt_required()
def delete_event(event_id):
    event = db.get_or_404(Event, event_id)
    user = current_user()
    if user.role != "organizer" or event.organizer_id != user.id:
        return jsonify({"error": "Only the event organizer can delete this event"}), 403
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Event deleted"})


@events_bp.post("/<int:event_id>/register")
@jwt_required()
def register_for_event(event_id):
    event = db.get_or_404(Event, event_id)
    user = current_user()
    if Registration.query.filter_by(user_id=user.id, event_id=event.id).first():
        return jsonify({"error": "You are already registered for this event"}), 409
    if len(event.registrations) >= event.capacity:
        return jsonify({"error": "This event is full"}), 409
    registration = Registration(user_id=user.id, event_id=event.id)
    db.session.add(registration)
    db.session.commit()
    return jsonify({"message": "Registration successful", "registration": registration.to_dict()}), 201


@events_bp.delete("/<int:event_id>/register")
@jwt_required()
def cancel_registration(event_id):
    event = db.get_or_404(Event, event_id)
    registration = Registration.query.filter_by(user_id=int(get_jwt_identity()), event_id=event.id).first()
    if not registration:
        return jsonify({"error": "No registration found"}), 404
    db.session.delete(registration)
    db.session.commit()
    return jsonify({"message": "Registration cancelled"})


@events_bp.get("/<int:event_id>/registrations")
@jwt_required()
def list_registrations(event_id):
    event = db.get_or_404(Event, event_id)
    user = current_user()
    if user.role != "organizer" or event.organizer_id != user.id:
        return jsonify({"error": "Only the event organizer can view registrations"}), 403
    return jsonify({"registrations": [registration.to_dict() for registration in event.registrations]})

