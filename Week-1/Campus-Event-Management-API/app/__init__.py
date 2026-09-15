from flask import Flask, jsonify, render_template

from config import Config
from .extensions import db, jwt


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    jwt.init_app(app)

    from .auth import auth_bp
    from .events import events_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(events_bp, url_prefix="/api/events")

    @app.get("/")
    def dashboard():
        return render_template("index.html")

    @app.get("/api/health")
    def health_check():
        return jsonify({"status": "ok", "message": "Campus Event Management API is running"})

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Resource not found"}), 404

    with app.app_context():
        db.create_all()

    return app
