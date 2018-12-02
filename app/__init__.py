from flask import Flask
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config.from_object(config)

mysql = MySQL(app)
db = SQLAlchemy(app)

from app import models, views
