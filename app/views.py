from flask import render_template, flash, redirect, url_for, session, request, jsonify
from functools import wraps
from app import app, mysql
from models import Users, Clients
from forms import *


# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


# User register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            Users.create_new(form.username.data, form.password.data)
            flash('New user registered', 'success')
            return redirect(url_for('login'))
        except Exception as error:
            flash(error, 'danger')
    return render_template('register.html', form=form)


# User login
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if request.method == 'POST' and form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is not None:
            if user.is_authorized(form.password.data):
                # Passed
                session['logged_in'] = True
                session['username'] = user.username

                # flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid credentials'
        else:
            error = 'Username not found'
    return render_template('login.html', form=form, error=error)


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    # flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


# Clients
@app.route('/clients')
@is_logged_in
def client_view():
    return render_template('clients.html')


# Private Clients
@app.route('/private_clients')
@is_logged_in
def private_clients():
    clients = Clients.query.all()
    if len(clients) > 0:
        return render_template('private_clients.html', clients=clients)
    else:
        msg = 'No Clients Found'
        return render_template('private_clients.html', msg=msg)


# Edit Private Client
@app.route('/private_client', methods=['GET', 'POST'])
@app.route('/private_client/<string:client_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_private_client(client_id=None):
    client = Clients.query.get(client_id) if client_id is not None else Clients()
    form = PrivateClientForm(obj=client)
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(client)
        client.save()
        flash('Client Updated', 'success')
        return redirect(url_for('private_clients'))
    else:
        pass
    return render_template('private_client.html',
                           title='Add private client' if client_id is None else 'Edit private client', form=form)


# Retail Clients
@app.route('/retail_clients')
@is_logged_in
def retail_clients():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get Retail Clients
    result = cur.execute("SELECT * FROM clients WHERE type = 'retail'")

    clients = cur.fetchall()

    if result > 0:
        return render_template('retail_clients.html', clients=clients)
    else:
        msg = 'No Clients Found'
        return render_template('retail_clients.html', msg=msg)

    # Close connection
    cur.close()


# Create choices for delivery_time field
# (for add_retail_client and edit_retail_client views)
def get_delivery_times():
    # Create cursor
    cur = mysql.connection.cursor()
    # Get Delivery Times
    result = cur.execute("SELECT time FROM delivery_times")
    times = cur.fetchall()
    # Close connection
    cur.close()
    # Create choices for the aggregate_to SelectField
    delivery_times = [(d['time'], d['time']) for d in times]
    return delivery_times


# Create choices for salespeople
# (for add_retail_client and edit_retail_client views)
def get_salespeople():
    # Create cursor
    cur = mysql.connection.cursor()
    # Get Salespeople
    result = cur.execute("SELECT name FROM salespeople ORDER BY name")
    names = cur.fetchall()
    # Close connection
    cur.close()
    # Create choices for the aggregate_to SelectField
    salespeople = [(d['name'], d['name']) for d in names]
    return salespeople


# Add Retail Client
@app.route('/add_retail_client', methods=['GET', 'POST'])
@is_logged_in
def add_retail_client():
    form = RetailClientForm(request.form)
    form.delivery_time.choices = get_delivery_times()
    form.salesperson.choices = get_salespeople()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        retail_type = form.retail_type.data
        delivery_time = form.delivery_time.data
        payment_scheme = form.payment_scheme.data
        statement_delivery_method = form.statement_delivery_method.data
        contact_person = form.contact_person.data
        phone_one = form.phone_one.data
        email_one = form.email_one.data
        wechat_id = form.wechat_id.data
        salesperson = form.salesperson.data
        other_info = form.other_info.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute(
            "INSERT INTO clients(name, type, retail_type, delivery_time, payment_scheme, statement_delivery_method, contact_person, phone_one, email_one, wechat_id, salesperson, other_info) VALUES(%s, 'retail', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (name, retail_type, delivery_time, payment_scheme, statement_delivery_method, contact_person, phone_one,
             email_one, wechat_id, salesperson, other_info))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Client Created', 'success')

        return redirect(url_for('retail_clients'))

    return render_template('add_retail_client.html', form=form)


# Edit Retail Client
@app.route('/edit_retail_client/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_retail_client(id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # Get retail client by id
    result = cur.execute("SELECT * FROM clients WHERE id = %s", [id])

    client = cur.fetchone()

    # Get form
    form = RetailClientForm(request.form)
    form.delivery_time.choices = get_delivery_times()
    form.salesperson.choices = get_salespeople()
    form.name.data = client['name']
    form.retail_type.data = client['retail_type']
    form.delivery_time.data = client['delivery_time']
    form.payment_scheme.data = client['payment_scheme']
    form.statement_delivery_method.data = client['statement_delivery_method']
    form.contact_person.data = client['contact_person']
    form.phone_one.data = client['phone_one']
    form.email_one.data = client['email_one']
    form.wechat_id.data = client['wechat_id']
    form.salesperson.data = client['salesperson']
    form.other_info.data = client['other_info']

    if request.method == 'POST' and form.validate():
        name = request.form['name']
        retail_type = request.form['retail_type']
        delivery_time = request.form['delivery_time']
        payment_scheme = request.form['payment_scheme']
        statement_delivery_method = request.form['statement_delivery_method']
        contact_person = request.form['contact_person']
        phone_one = request.form['phone_one']
        email_one = request.form['email_one']
        wechat_id = request.form['wechat_id']
        salesperson = request.form['salesperson']
        other_info = request.form['other_info']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute(
            "UPDATE clients SET name=%s, retail_type=%s, delivery_time=%s, payment_scheme=%s, statement_delivery_method=%s, contact_person=%s, phone_one=%s, email_one=%s, wechat_id=%s, salesperson=%s, other_info=%s WHERE id=%s",
            (name, retail_type, delivery_time, payment_scheme, statement_delivery_method, contact_person, phone_one,
             email_one, wechat_id, salesperson, other_info, id))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Client Updated', 'success')

        return redirect(url_for('retail_clients'))
    else:
        print(form.errors)
    return render_template('edit_retail_client.html', form=form)


# Delivery Times
@app.route('/delivery_times')
@is_logged_in
def delivery_times():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get Delivery Times
    result = cur.execute("SELECT * FROM delivery_times")

    delivery_times = cur.fetchall()

    if result > 0:
        return render_template('delivery_times.html', delivery_times=delivery_times)
    else:
        msg = 'No Delivery Times Found'
        return render_template('delivery_times.html', msg=msg)

    # Close connection
    cur.close()


# Add Delivery Time
@app.route('/add_delivery_time', methods=['GET', 'POST'])
@is_logged_in
def add_delivery_time():
    form = DeliveryTimeForm(request.form)
    if request.method == 'POST' and form.validate():
        time = form.time.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO delivery_times(time) VALUES(%s)", [time])

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Delivery Time Created', 'success')

        return redirect(url_for('delivery_times'))

    return render_template('add_delivery_time.html', form=form)


# Edit Delivery Time
@app.route('/edit_delivery_time/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_delivery_time(id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # Get delivery time by id
    result = cur.execute("SELECT * FROM delivery_times WHERE id = %s", [id])

    delivery_time = cur.fetchone()

    # Get form
    form = DeliveryTimeForm(request.form)

    # Populate delivery time form fields
    form.time.data = delivery_time['time']

    if request.method == 'POST' and form.validate():
        time = request.form['time']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute and update retail clients table
        result = cur.execute("SELECT * FROM delivery_times WHERE id = %s", [id])
        delivery_time = cur.fetchone()
        cur.execute("UPDATE clients SET delivery_time=%s WHERE delivery_time=%s", (time, delivery_time['time']))
        cur.execute("UPDATE delivery_times SET time=%s WHERE id=%s", (time, id))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Delivery Time Updated', 'success')

        return redirect(url_for('delivery_times'))

    return render_template('edit_delivery_time.html', form=form)


# Products
@app.route('/products')
@is_logged_in
def products():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get Products
    result = cur.execute("SELECT * FROM products")

    products = cur.fetchall()

    if result > 0:
        return render_template('products.html', products=products)
    else:
        msg = 'No Products Found'
        return render_template('products.html', msg=msg)

    # Close connection
    cur.close()


# Create choices for aggregate_to field when nr_pieces_per_bag is equal to 1
# (for add_product and edit_product views)
def get_names():
    # Create cursor
    cur = mysql.connection.cursor()
    # Get Products
    result = cur.execute("SELECT name FROM products WHERE nr_pieces_per_bag=1 ORDER BY name")
    products = cur.fetchall()
    # Close connection
    cur.close()
    # Create choices for the aggregate_to SelectField
    names = [(d["name"], d['name']) for d in products]
    return names


# Add Product
@app.route('/add_product', methods=['GET', 'POST'])
@is_logged_in
def add_product():
    form = ProductForm(request.form)
    form.aggregate_to.choices = get_names()

    if request.method == 'POST' and form.validate():
        name = form.name.data
        product_type = form.product_type.data
        nr_pieces_per_bag = form.nr_pieces_per_bag.data
        if int(nr_pieces_per_bag) == 1:
            aggregate_to = "-"
        else:
            aggregate_to = form.aggregate_to.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO products(name, product_type, nr_pieces_per_bag, aggregate_to) VALUES(%s, %s, %s, %s)",
                    (name, product_type, nr_pieces_per_bag, aggregate_to))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Product Created', 'success')

        return redirect(url_for('products'))

    return render_template('add_product.html', form=form)


# Edit Product
@app.route('/edit_product/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_product(id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # Get product by id
    result = cur.execute("SELECT * FROM products WHERE id = %s", [id])
    product = cur.fetchone()

    # Get form
    form = ProductForm(request.form)
    form.aggregate_to.choices = get_names()
    form.name.data = product['name']
    form.product_type.data = product['product_type']
    form.nr_pieces_per_bag.data = product['nr_pieces_per_bag']
    if int(form.nr_pieces_per_bag.data) != 1:
        form.aggregate_to.data = product['aggregate_to']

    if request.method == 'POST' and form.validate():
        name = request.form['name']
        product_type = request.form['product_type']
        nr_pieces_per_bag = request.form['nr_pieces_per_bag']
        if int(nr_pieces_per_bag) == 1:
            aggregate_to = "-"
        else:
            aggregate_to = request.form['aggregate_to']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute and update the products aggregated to the product whose name was changed
        result = cur.execute("SELECT * FROM products WHERE id = %s", [id])
        product = cur.fetchone()
        cur.execute("UPDATE products SET aggregate_to=%s WHERE aggregate_to=%s", (name, product['name']))
        cur.execute("UPDATE prices SET product=%s WHERE product=%s", (name, product['name']))
        cur.execute("UPDATE products SET name=%s, product_type=%s, nr_pieces_per_bag=%s, aggregate_to=%s WHERE id=%s",
                    (name, product_type, nr_pieces_per_bag, aggregate_to, id))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Product Updated', 'success')

        return redirect(url_for('products'))
    # print old_name
    else:
        print(form.errors)
    return render_template('edit_product.html', form=form)


# Prices
@app.route('/prices')
@is_logged_in
def prices():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get Prices
    result = cur.execute("SELECT * FROM prices ORDER BY product, client_type, price_type DESC, client_name")

    prices = cur.fetchall()

    if result > 0:
        return render_template('prices.html', prices=prices)
    else:
        msg = 'No Prices Found'
        return render_template('prices.html', msg=msg)

    # Close connection
    cur.close()


# Create choices for product field
# (for add_price and edit_price views)
def get_product_names():
    # Create cursor
    cur = mysql.connection.cursor()
    # Get Products
    result = cur.execute("SELECT name FROM products ORDER BY name")
    products = cur.fetchall()
    # Close connection
    cur.close()
    # Create choices for the aggregate_to SelectField
    names = [(d["name"], d['name']) for d in products]
    return names


# Create choices for client_name field
# (for add_price and edit_price views)
def get_client_names():
    # Create cursor
    cur = mysql.connection.cursor()
    # Get Products
    result = cur.execute("SELECT name FROM clients WHERE type = %s ORDER BY name", ['Retail'])
    clients = cur.fetchall()
    # Close connection
    cur.close()
    # Create choices for the aggregate_to SelectField
    names = [(d["name"], d['name']) for d in clients]
    return names


# Add Price
@app.route('/add_price', methods=['GET', 'POST'])
@is_logged_in
def add_price():
    form = PriceForm(request.form)
    form.product.choices = get_product_names()
    form.client_name.choices = get_client_names()

    if request.method == 'POST' and form.validate():
        product = form.product.data
        client_type = form.client_type.data
        if client_type == 'Private':
            price_type = 'Standard'
            client_name = '-'
        else:
            price_type = form.price_type.data
            if price_type == 'Standard':
                client_name = '-'
            else:
                client_name = form.client_name.data

        # price_type = form.price_type.data
        # client_name = form.client_name.data
        unit_price = form.unit_price.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute(
            "INSERT INTO prices(product, client_type, price_type, client_name, unit_price) VALUES(%s, %s, %s, %s, %s)",
            (product, client_type, price_type, client_name, unit_price))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Price Created', 'success')

        return redirect(url_for('prices'))

    return render_template('add_price.html', form=form)


# Edit Price
@app.route('/edit_price/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_price(id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # Get price by id
    result = cur.execute("SELECT * FROM prices WHERE id = %s", [id])
    price = cur.fetchone()

    # Get form
    form = PriceForm(request.form)
    form.product.choices = get_product_names()
    form.client_name.choices = get_client_names()
    form.product.data = price['product']
    form.client_type.data = price['client_type']
    if form.client_type.data == "Retail":
        form.price_type.data = price['price_type']
        if form.price_type.data == "Special":
            form.client_name.data = price['client_name']
    form.unit_price.data = price['unit_price']

    if request.method == 'POST' and form.validate():
        product = request.form['product']
        client_type = request.form['client_type']
        # price_type = request.form['price_type']
        # client_name = request.form['client_name']
        if client_type == 'Private':
            price_type = 'Standard'
            client_name = '-'
        else:
            price_type = request.form['price_type']
            if price_type == 'Standard':
                client_name = '-'
            else:
                client_name = request.form['client_name']
        unit_price = request.form['unit_price']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute(
            "UPDATE prices SET product=%s, client_type=%s, price_type=%s, client_name=%s, unit_price=%s WHERE id=%s",
            (product, client_type, price_type, client_name, unit_price, id))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Price Updated', 'success')

        return redirect(url_for('prices'))
    # print old_name
    else:
        print(form.errors)
    return render_template('edit_price.html', form=form)


# Salespeople
@app.route('/salespeople')
@is_logged_in
def salespeople():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get Salespeople
    result = cur.execute("SELECT * FROM salespeople")

    salespeople = cur.fetchall()

    if result > 0:
        return render_template('salespeople.html', salespeople=salespeople)
    else:
        msg = 'No Salespeople Found'
        return render_template('salespeople.html', msg=msg)

    # Close connection
    cur.close()


# Add Salesperson
@app.route('/add_salesperson', methods=['GET', 'POST'])
@is_logged_in
def add_salesperson():
    form = SalespersonForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO salespeople(name) VALUES(%s)", [name])

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Salesperson Created', 'success')

        return redirect(url_for('salespeople'))

    return render_template('add_salesperson.html', form=form)


# Edit Salesperson
@app.route('/edit_salesperson/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_salesperson(id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # Get salesperson by id
    result = cur.execute("SELECT * FROM salespeople WHERE id = %s", [id])

    salesperson = cur.fetchone()

    # Get form
    form = SalespersonForm(request.form)

    # Populate salesperson form fields
    form.name.data = salesperson['name']

    if request.method == 'POST' and form.validate():
        name = request.form['name']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute and update retail clients table
        result = cur.execute("SELECT * FROM salespeople WHERE id = %s", [id])
        salesperson = cur.fetchone()
        cur.execute("UPDATE clients SET salesperson=%s WHERE salesperson=%s", (name, salesperson['name']))
        cur.execute("UPDATE salespeople SET name=%s WHERE id=%s", (name, id))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Salesperson Updated', 'success')

        return redirect(url_for('salespeople'))

    return render_template('edit_salesperson.html', form=form)


# Invoices
@app.route('/invoices')
@is_logged_in
def invoices():
    return render_template('invoices.html')


# Invoices Private Clients
@app.route('/invoices_private_clients')
@is_logged_in
def invoices_private_clients():
    return render_template('invoices_private_clients.html')


# Manage Invoices Private Clients
@app.route('/manage_invoices_private_clients')
@is_logged_in
def manage_invoices_private_clients():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get Invoices
    result = cur.execute(
        "SELECT * FROM invoices INNER JOIN clients ON invoices.client_id = clients.id WHERE clients.type = 'Private'")

    invoices = cur.fetchall()

    if result > 0:
        return render_template('manage_invoices_private_clients.html', invoices=invoices)
    else:
        msg = 'No Invoices Found'
        return render_template('manage_invoices_private_clients.html', msg=msg)

    # Close connection
    cur.close()


# Edit Private Client Invoice
@app.route('/edit_invoice_private_client/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_invoice_private_client(id):
    # Create Cursor
    cur = mysql.connection.cursor()

    # Get price by id
    result = cur.execute(
        "SELECT * FROM invoices INNER JOIN clients ON invoices.client_id = clients.id WHERE invoices.id = %s", [id])
    invoice = cur.fetchone()

    # Get form
    form = PrivateClientInvoiceForm(request.form)
    form.invoice_id.data = invoice['id']
    form.client_id.data = invoice['client_id']
    form.client_n.data = invoice['name']
    form.delivery_day.data = invoice['delivery_day']
    form.total_amount.data = invoice['total_amount']
    form.payment_status.data = invoice['payment_status']
    if form.payment_status.data == 'Paid':
        form.payment_date.data = invoice['payment_date']
        form.payment_method.data = invoice['payment_method']
        form.payment_details.data = invoice['payment_details']
    else:
        form.payment_date.data = invoice['payment_date']
        form.payment_method.data = 'Bank transfer'
        form.payment_details.data = ''
    form.other_info.data = invoice['other_info']

    if request.method == 'POST' and form.validate():
        delivery_day = request.form['delivery_day']
        payment_status = request.form['payment_status']
        if payment_status == 'Paid':
            payment_date = request.form['payment_date']
            payment_method = request.form['payment_method']
            payment_details = request.form['payment_details']
        else:
            # Ficticious payment_date to avoid eliminating the form.validate() function
            payment_date = '2000-01-01'
            payment_method = ''
            payment_details = ''

        other_info = request.form['other_info']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute(
            "UPDATE invoices SET delivery_day=%s, payment_status=%s, payment_date=%s, payment_method=%s, payment_details=%s, other_info=%s WHERE id=%s",
            (delivery_day, payment_status, payment_date, payment_method, payment_details, other_info, id))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Invoice Updated', 'success')

        return redirect(url_for('manage_invoices_private_clients'))

    else:
        print(form.errors)
    return render_template('edit_invoice_private_client.html', form=form)


# Create choices for client_id field
# (for add_invoice view)
def get_client_ids():
    # Create cursor
    cur = mysql.connection.cursor()
    # Get Products
    result = cur.execute("SELECT * FROM clients WHERE type = %s ORDER BY id", ['Private'])
    clients = cur.fetchall()
    # Close connection
    cur.close()
    # Create choices for the aggregate_to SelectField
    ids_names = [(d["id"], str(d['id']) + ' / ' + d['name']) for d in clients]
    # ids_names = [(d["id"], d['id']) for d in clients]

    return ids_names


# Add Invoices Private Clients
@app.route('/add_invoice_private_clients', methods=['GET', 'POST'])
@is_logged_in
def add_invoice_private_clients():
    form = PrivateClientAddInvoiceForm(request.form)
    form.client_id.choices = get_client_ids()
    form.product_one.choices = get_product_names()
    for sub_form in form.items:
        sub_form.product.choices = get_product_names()

    if request.method == 'POST':
        print request.form
        client_id = request.json.get('client_id')
        delivery_day = form.delivery_day.data
        total_amount = form.total_amount.data
        unit_price_one = request.json.get('price', 0)

        # unit_price_one = request.args.get('price')

        # Create Cursor
        cur = mysql.connection.cursor()

        # Get the invoice id of the new invoice
        result = cur.execute("SELECT * FROM invoices ORDER BY id DESC LIMIT 1;")
        current_invoice = cur.fetchone()

        # Insert data on the ordered_items table
        cur.execute(
            "INSERT INTO ordered_items(invoice_id, product_description, quantity_ordered, ordered_unit_price) values(%s, 'pao', 5, %s)",
            (current_invoice['id'], unit_price_one))

        # # Execute and insert into the database general invoice data
        # cur.execute("INSERT INTO invoices(client_id, delivery_day, total_amount, payment_status, payment_method, payment_details, other_info) VALUES(%s, %s, %s, 'Not paid', '', '', '')", (client_id, delivery_day, total_amount))

        # # Get the invoice id of the new invoice
        # result = cur.execute("SELECT * FROM invoices ORDER BY id DESC LIMIT 1;")
        # current_invoice = cur.fetchone()

        # # Insert into the database ordered items data
        # for sub_form in form.items:
        # 	product = sub_form.product.data
        # 	quantity = sub_form.quantity.data
        # 	unit_price = sub_form.unit_price.data

        # 	cur.execute("INSERT INTO ordered_items(invoice_id, product_description, quantity_ordered, ordered_unit_price) VALUES(%s, %s, %s, %s)", (current_invoice['id'], product, quantity, unit_price))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('Invoice Created', 'success')

        return jsonify({
            "message": "success"
        })

    return render_template('add_invoice_private_clients.html', form=form)


# Update Unite Price on Add Invoice View
@app.route('/get_unit_price', methods=['GET'])
@is_logged_in
def get_unit_price():
    prod = request.args.get('product')
    if prod is not None or prod is not '':
        # Create cursor
        cur = mysql.connection.cursor()
        # Get unit price
        result = cur.execute("SELECT * FROM prices WHERE product = %s AND client_type = 'Private'", [prod])
        selected_price = cur.fetchone()
        # Close connection
        if selected_price is not None:
            price = selected_price.get('unit_price', 0)
        else:
            price = 0
        # form = PrivateClientAddInvoiceForm(request.form)
        # form.unit_price_one.data = price
        # return render_template('add_invoice_private_client.html', form=form)
        cur.close()
        return str(price)
    else:
        return ''


# Convert Invoices to PDF Private Clients
@app.route('/convert_invoices_pdf_private_clients')
@is_logged_in
def convert_invoices_pdf_private_clients():
    return render_template('convert_invoices_pdf_private_clients.html')


# Invoices Retail Clients
@app.route('/invoices_retail_clients')
@is_logged_in
def invoices_retail_clients():
    return render_template('invoices_retail_clients.html')


# Manage Invoices Retail Clients
@app.route('/manage_invoices_retail_clients', methods=['GET', 'POST'])
@is_logged_in
def manage_invoices_retail_clients():
    return render_template('manage_invoices_retail_clients.html')


# Testing
@app.route('/testing', methods=['GET', 'POST'])
@is_logged_in
def testing():
    prod = request.args.get('product')
    # return render_template('invoices_Retail_clients.html')
    return str(prod)


# Generate Invoices of the Day Retail Clients
@app.route('/generate_invoices_day_retail_clients')
@is_logged_in
def generate_invoices_day_retail_clients():
    return render_template('generate_invoices_day_retail_clients.html')


# Convert Invoices to PDF Retail Clients
@app.route('/convert_invoices_pdf_retail_clients')
@is_logged_in
def convert_invoices_pdf_retail_clients():
    return render_template('convert_invoices_pdf_retail_clients.html')


# Statements & Receipts
@app.route('/statements_receipts')
@is_logged_in
def statements_receipts():
    return render_template('statements_receipts.html')


# Bakery & Pastry Reports
@app.route('/bakery_pastry_reports')
@is_logged_in
def bakery_pastry_reports():
    return render_template('bakery_pastry_reports.html')


# Divers Info
@app.route('/drivers_info')
@is_logged_in
def drivers_info():
    return render_template('drivers_info.html')


# Data Backup
@app.route('/data_backup')
@is_logged_in
def data_backup():
    return render_template('data_backup.html')
