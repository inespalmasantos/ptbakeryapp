from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from app import app, mysql, login_manager
from models import Users, DeliveryTimes, Products, Prices, Clients
from forms import *


@login_manager.user_loader
def load_user(user_id):
    return Users.get_by_id(user_id)


# Dashboard
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# Delivery Times
@app.route('/delivery_times')
@login_required
def delivery_times():
    result = DeliveryTimes.get_all()
    if len(result) > 0:
        return render_template('delivery_times.html', delivery_times=result)
    else:
        msg = 'No Delivery Times Found'
        return render_template('delivery_times.html', msg=msg)


# Add Delivery Time
@app.route('/add_delivery_time', methods=['GET', 'POST'])
@login_required
def add_delivery_time():
    form = DeliveryTimeForm(request.form)
    if request.method == 'POST' and form.validate():
        obj = DeliveryTimes(time=form.time.data)
        obj.save()
        flash('Delivery time created', 'success')
        return redirect(url_for('delivery_times'))
    return render_template('add_delivery_time.html', form=form)


# Edit Delivery Time
@app.route('/edit_delivery_time/<string:id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def get_products():
    result = Products.get_all()
    if len(result) > 0:
        return render_template('products.html', products=result)
    else:
        msg = 'No Products Found'
        return render_template('products.html', msg=msg)


# Create choices for aggregate_to field when nr_pieces_per_bag is equal to 1
# (for add_product and edit_product views)
def get_names():
    products = Products.get_all()
    # Create choices for the aggregate_to SelectField
    names = [(d["name"], d['name']) for d in products]
    return names


# Add Product
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def get_prices():
    prices = Prices.get_all()

    if len(prices) > 0:
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def invoices():
    return render_template('invoices.html')


# Invoices Private Clients
@app.route('/invoices_private_clients')
@login_required
def invoices_private_clients():
    return render_template('invoices_private_clients.html')


# Manage Invoices Private Clients
@app.route('/manage_invoices_private_clients')
@login_required
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
@login_required
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
    clients = Clients.get_private_clients()
    ids_names = [(d["id"], str(d['id']) + ' / ' + d['name']) for d in clients]
    return ids_names


# Add Invoices Private Clients
@app.route('/add_invoice_private_clients', methods=['GET', 'POST'])
@login_required
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
@login_required
def get_unit_price():
    prod = request.args.get('product')
    if prod is not None or prod is not '':
        selected_price = Prices.query.filter_by(product=prod, client_type='Private')
        if selected_price is not None:
            price = selected_price.get('unit_price', 0)
        else:
            price = 0
        return str(price)
    else:
        return ''


# Convert Invoices to PDF Private Clients
@app.route('/convert_invoices_pdf_private_clients')
@login_required
def convert_invoices_pdf_private_clients():
    return render_template('convert_invoices_pdf_private_clients.html')


# Invoices Retail Clients
@app.route('/invoices_retail_clients')
@login_required
def invoices_retail_clients():
    return render_template('invoices_retail_clients.html')


# Manage Invoices Retail Clients
@app.route('/manage_invoices_retail_clients', methods=['GET', 'POST'])
@login_required
def manage_invoices_retail_clients():
    return render_template('manage_invoices_retail_clients.html')


# Generate Invoices of the Day Retail Clients
@app.route('/generate_invoices_day_retail_clients')
@login_required
def generate_invoices_day_retail_clients():
    return render_template('generate_invoices_day_retail_clients.html')


# Convert Invoices to PDF Retail Clients
@app.route('/convert_invoices_pdf_retail_clients')
@login_required
def convert_invoices_pdf_retail_clients():
    return render_template('convert_invoices_pdf_retail_clients.html')


# Statements & Receipts
@app.route('/statements_receipts')
@login_required
def statements_receipts():
    return render_template('statements_receipts.html')


# Bakery & Pastry Reports
@app.route('/bakery_pastry_reports')
@login_required
def bakery_pastry_reports():
    return render_template('bakery_pastry_reports.html')


# Divers Info
@app.route('/drivers_info')
@login_required
def drivers_info():
    return render_template('drivers_info.html')


# Data Backup
@app.route('/data_backup')
@login_required
def data_backup():
    return render_template('data_backup.html')
