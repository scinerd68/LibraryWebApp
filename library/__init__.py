from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from library.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from library.users.routes import users
    from library.books.routes import books
    from library.borrows.routes import borrows
    from library.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(books)
    app.register_blueprint(borrows)
    app.register_blueprint(main)

    return app