from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from .routes import auth_bp, market_bp
from flask_migrate import Migrate
from os import path
from .extensions import db
import os

# Utility import
from .utils import encode_image_to_base64

# Initialize extensions
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(12).hex())
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, "database.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)  # Initialize Migrate here
   # app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(market_bp, url_prefix='/')

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = 'info'

    # Importing models and routes after initial setup to avoid circular imports
    from .models import User, Song, Rating, Playlist, Album
    from .views import views
    from .auth import auth
    from .songs import songs_blueprint
    from .playlist import playlist_bp
    from .album import album_bp

    # Register blueprints
    app.register_blueprint(songs_blueprint)
    app.register_blueprint(playlist_bp)
    app.register_blueprint(album_bp)
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    # Database creation
    with app.app_context():
        db.create_all()

    # Login manager loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Context processor for injecting user info
    @app.context_processor
    def inject_user_info():
        profile_image_base64 = None
        if current_user.is_authenticated and current_user.image:
            profile_image_base64 = encode_image_to_base64(current_user.image)
        user_info = {
            "current_user": current_user,
            "current_user_profile_image": profile_image_base64,
                    }
        return user_info
    return app

# To avoid executing code at import, guard the main entry point
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
