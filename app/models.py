from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from sqlalchemy import exc
from flask_login import UserMixin


class BaseModel(db.Model):
    __abstract__ = True

    @staticmethod
    def get_by_id(user_id):
        return Users.query.filter_by(id=user_id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()


class Users(BaseModel, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    register_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password: write only field')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return Users.query.filter_by(username=username).first()

    @staticmethod
    def create_new(username, plain_password):
        try:
            user = Users(username=username, password_hash=plain_password)
            user.save()
            return True
        except exc.SQLAlchemyError:
            raise Exception("Username already taken")

    def __repr__(self):
        return '<User %r>' % self.username


class Clients(BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(30))
    retail_type = db.Column(db.String(30))
    name = db.Column(db.String(100))
    payment_scheme = db.Column(db.String(30))
    statement_delivery_method = db.Column(db.String(30))
    delivery_time = db.Column(db.DateTime)
    phone_one = db.Column(db.String(30))
    phone_two = db.Column(db.String(30))
    email_one = db.Column(db.String(100))
    email_two = db.Column(db.String(100))
    address = db.Column(db.String(250))
    zone = db.Column(db.String(30))
    door_code = db.Column(db.String(100))
    contact_person = db.Column(db.String(100))
    wechat_id = db.Column(db.String(100))
    other_info = db.Column(db.String(255))
    create_date = db.Column(db.TIMESTAMP)

    def __repr__(self):
        return '<Client %r>' % self.name
