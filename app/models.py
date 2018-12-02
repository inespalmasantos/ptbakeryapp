from app import db
from passlib.hash import sha256_crypt
import datetime
from sqlalchemy import exc


class BaseModel(db.Model):
    __abstract__ = True

    def save(self):
        db.session.add(self)
        db.session.commit()


class Users(BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    register_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def create_new(username, plain_password):
        try:
            user = Users(username=username, password=sha256_crypt.encrypt(str(plain_password)))
            user.save()
            return True
        except exc.SQLAlchemyError:
            raise Exception("Username already taken")

    def is_authorized(self, password):
        return sha256_crypt.verify(password, self.password)

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