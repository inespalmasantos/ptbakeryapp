from flask import Flask
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
import config

app = Flask(__name__)
app.config.from_object(config)
toolbar = DebugToolbarExtension(app)
mysql = MySQL(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from .auth import auth as auth_blueprint
from .client import client as client_blueprint

app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(client_blueprint, url_prefix="/client")

from app import models, views
