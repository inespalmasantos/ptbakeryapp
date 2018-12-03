from wtforms import Form, DateField, DecimalField, FormField, FieldList, \
    StringField, SelectField, IntegerField, validators


# Delivery Time Form Class
class DeliveryTimeForm(Form):
    time = StringField('Time', [validators.Length(min=1, max=20)])


# Product Form Class
class ProductForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    product_type = SelectField('Type', choices=[('Bakery', 'Bakery'), ('Pastry', 'Pastry')])
    nr_pieces_per_bag = SelectField('Number of pieces per bag', choices=[(x, x) for x in range(1, 41)], coerce=int)
    aggregate_to = SelectField('Aggregate to', choices=[])


# Price Form Class
class PriceForm(Form):
    # product = StringField('Product', [validators.Length(min=1, max=100)])
    product = SelectField('Product', choices=[])
    client_type = SelectField('Client type', choices=[('Private', 'Private'), ('Retail', 'Retail')])
    price_type = SelectField('Price type', choices=[('Standard', 'Standard'), ('Special', 'Special')])
    # client_name = StringField('Client name', [validators.Length(min=1, max=100)])
    client_name = SelectField('Client name', choices=[])
    unit_price = DecimalField('Unit price', places=2, rounding=None)


# Salesperson Form Class
class SalespersonForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=30)])


# Private Client Invoice Form Class
class PrivateClientInvoiceForm(Form):
    invoice_id = IntegerField('Invoice #')
    client_id = IntegerField('Client id')
    client_n = StringField('Client name')
    delivery_day = DateField('Delivery day', format='%Y-%m-%d')
    total_amount = DecimalField('Total amount', places=2, rounding=None)
    payment_status = SelectField('Payment status', choices=[('Not paid', 'Not paid'), ('Paid', 'Paid')])
    payment_date = DateField('Payment date', format='%Y-%m-%d')
    payment_method = SelectField('Payment method', choices=[('Bank transfer', 'Bank transfer'), ('Cash', 'Cash')])
    payment_details = StringField('Payment details', [validators.Length(max=255)])
    other_info = StringField('Other info', [validators.Length(max=255)])


# Ordered Items Form Class
class OrderedItemsForm(Form):
    product = SelectField('', choices=[])
    quantity = SelectField('', choices=[(x, x) for x in range(1, 101)], coerce=int)
    unit_price = DecimalField('', places=2, rounding=None)
    amount = DecimalField('', places=2, rounding=None)


# Private Client Add Invoice Form Class
class PrivateClientAddInvoiceForm(Form):
    client_id = SelectField('Client id / Client name', choices=[], coerce=int)
    delivery_day = DateField('Delivery day', format='%Y-%m-%d')
    total_amount = DecimalField('Total amount', places=2, rounding=None)
    items = FieldList(FormField(OrderedItemsForm), min_entries=5, max_entries=5)
    product_one = SelectField('', choices=[])
    quantity_one = SelectField('', choices=[(x, x) for x in range(1, 101)], coerce=int)
    unit_price_one = DecimalField('', places=2, rounding=None)
    amount_one = DecimalField('', places=2, rounding=None)
