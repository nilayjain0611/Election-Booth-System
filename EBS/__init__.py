from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# from .models import Voter, SuperUser  

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)

    # Set your secret key for session management
    app.config['SECRET_KEY'] = 'secret_key'

    # Configure your SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configure Flask-Mail for sending emails
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Gmail SMTP server
    app.config['MAIL_PORT'] = 587  # Port for TLS
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'nilayjain987@gmail.com'  # Your Gmail email address
    app.config['MAIL_PASSWORD'] = 'ogirkssplkiaihhy'  # Your Gmail app password
    app.config['MAIL_DEFAULT_SENDER'] = 'nilayjain987@gmail.com'
    app.config['MAIL_DEBUG'] = True


    db.init_app(app)
    mail.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Set the login view for unauthorized users
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Since you have two user models (Voter and SuperUser),
        # you need to check which model the user_id corresponds to
        # and return the user object accordingly.
        from .models import Voter, SuperUser
        voter = Voter.query.get(int(user_id))
        if voter:
            return voter
        superuser = SuperUser.query.get(int(user_id))
        if superuser:
            return superuser
        return None
    
    # Register blueprints
    from .models import Voter  # Import your model to create the tables
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .elections import elections

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(elections)

    with app.app_context():
        db.create_all()

    return app
