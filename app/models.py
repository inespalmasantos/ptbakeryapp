from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from sqlalchemy import exc
from flask_login import UserMixin


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    @classmethod
    def get_by_id(cls, id):
        """
        returns model instance of given id
        :parm id: id of the requested model
        return: model instance crosspoding to given id
        """
        return cls.query.filter_by(**{'id': id}).first()

    @classmethod
    def get_all(cls):
        """
            Returns a list of instances
        """
        return cls.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()


class Users(BaseModel, UserMixin):
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

    @staticmethod
    def get_private_clients():
        return Clients.query.filter_by(type='Private').order_by('id').all()

    def __repr__(self):
        return '<Client %r>' % self.name


class SalesPeople(BaseModel):
    name = db.Column(db.String(100), nullable=False)


class DeliveryTimes(BaseModel):
    time = db.Column(db.String(20), nullable=False)


class Products(BaseModel):
    name = db.Column(db.String(100), nullable=True)
    product_type = db.Column(db.String(10), nullable=True)
    nr_pieces_per_bag = db.Column(db.Integer(), autoincrement=False, nullable=True)
    aggregate_to = db.Column(db.String(100), nullable=True)


class Invoices(BaseModel):
    client_id = db.Column(db.Integer(), autoincrement=False, nullable=False)
    delivery_day = db.Column(db.Date, nullable=True)
    delivery_time = db.Column(db.String(20), nullable=True)
    total_amount = db.Column(db.DECIMAL(precision=7, scale=2), nullable=True)
    payment_scheme = db.Column(db.String(20), nullable=True)
    other_comments = db.Column(db.String(255), nullable=True)
    payment_status = db.Column(db.String(20), nullable=True)
    payment_date = db.Column(db.Date(), nullable=True)
    payment_method = db.Column(db.String(20), nullable=True)
    payment_details = db.Column(db.String(255), nullable=True)
    statement_issued = db.Column(db.String(20), nullable=True)
    statement_id = db.Column(db.Integer(), autoincrement=False, nullable=True)
    other_info = db.Column(db.String(255), nullable=True)


class Prices(BaseModel):
    product = db.Column(db.String(100), nullable=True)
    client_type = db.Column(db.String(10), nullable=True)
    price_type = db.Column(db.String(10), nullable=True)
    client_name = db.Column(db.String(100), nullable=True)
    unit_price = db.Column(db.DECIMAL(precision=6, scale=2), nullable=True)


class OrderedItems(BaseModel):
    invoice_id = db.Column(db.Integer(), autoincrement=False, nullable=True)
    product_description = db.Column(db.String(100), nullable=True)
    quantity_ordered = db.Column(db.Integer(), autoincrement=False, nullable=True)
    quantity_returned = db.Column(db.Integer(), autoincrement=False, nullable=True)
    ordered_unit_price = db.Column(db.DECIMAL(precision=6, scale=2), nullable=True)
