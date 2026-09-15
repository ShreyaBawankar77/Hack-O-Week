from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from .extensions import db
from .models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    required = ["name", "email", "password"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if User.query.filter_by(email=data["email"].lower()).first():
        return jsonify({"error": "Email is already registered"}), 409

    role = data.get("role", "student")
    if role not in {"student", "organizer"}:
        return jsonify({"error": "Role must be student or organizer"}), 400

    user = User(name=data["name"].strip(), email=data["email"].lower().strip(), role=role)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered", "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email, password = data.get("email"), data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email.lower().strip()).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"access_token": token, "user": user.to_dict()})

