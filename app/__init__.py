"""Create the Flask app and register all blueprints."""
from flask import Flask

import config
from app import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)

    # Close the DB connection after each request
    db.init_app(app)

    # Build the database on first run if it does not exist
    from app import seed
    if not seed.has_tables():
        seed.build_database()
    # Add any missing demo vehicles and users
    seed.ensure_demo_data()

    # Register blueprints
    from app.blueprints.public import public_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.employees import employees_bp
    from app.blueprints.incidents import incidents_bp
    from app.blueprints.tasks import tasks_bp
    from app.blueprints.resources import resources_bp
    from app.blueprints.messages import messages_bp
    from app.blueprints.ops import ops_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(ops_bp)

    # Expose current_user and role labels to every template
    from app.auth_utils import current_user

    role_labels = {
        "admin": "Администратор",
        "dispatcher": "Диспечер",
        "firefighter": "Пожарникар",
    }

    @app.context_processor
    def inject_globals():
        return {"current_user": current_user(), "role_labels": role_labels}

    return app
