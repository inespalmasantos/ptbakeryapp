from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, validators


# Private Client Form Class
class PrivateClientForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=100)])
    payment_scheme = SelectField('Payment scheme',
                                 choices=[('Post delivery', 'Post delivery'), ('Prepayment', 'Prepayment')])
    phone_one = StringField('Phone', [validators.Length(max=30)])
    email_one = StringField('Email', [validators.Length(max=100)])
    address = StringField('Address', [validators.Length(min=1, max=255)])
    door_code = StringField('Door code', [validators.Length(max=100)])
    zone = SelectField('Zone',
                       choices=[('Macau', 'Macau'), ('Taipa', 'Taipa'), ('Coloane', 'Coloane'), ('Cotai', 'Cotai')])


# Retail Client Form Class
class RetailClientForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=100)])
    retail_type = SelectField('Retail type', choices=[('Restaurant', 'Restaurant'), ('Supermarket', 'Supermarket')])
    delivery_time = SelectField('Delivery time', choices=[])
    payment_scheme = SelectField('Payment scheme', choices=[('CoD', 'CoD'), ('WB', 'WB'), ('MB', 'MB'), ('TBC', 'TBC')])
    statement_delivery_method = SelectField('Statement delivery method',
                                            choices=[('By email', 'By email'), ('By wechat', 'By wechat'),
                                                     ('By hand', 'By hand'), ('Not applicable', 'Not applicable')])
    contact_person = StringField('Contact person', [validators.Length(max=100)])
    phone_one = StringField('Phone', [validators.Length(max=30)])
    email_one = StringField('Email', [validators.Length(max=100)])
    wechat_id = StringField('Wechat id', [validators.Length(max=100)])
    salesperson = SelectField('Salesperson', choices=[])
    other_info = StringField('Other info', [validators.Length(max=255)])
