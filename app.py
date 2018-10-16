from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, DateField, DecimalField, StringField, SelectField, IntegerField, TextAreaField, PasswordField, validators, ValidationError
from passlib.hash import sha256_crypt
from functools import wraps
#from datetime import datetime
import json

app = Flask(__name__)
app.config.from_object('config')

# Config MySQL
app.config['MYSQL_HOST']
app.config['MYSQL_USER']
app.config['MYSQL_PASSWORD']
app.config['MYSQL_DB']
app.config['MYSQL_CURSORCLASS']
# init MYSQL
mysql = MySQL(app)

# Secret key
app.config['SECRET_KEY']

# User login
@app.route('/', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		# Get Form Fields
		username = request.form['username']
		password_candidate = request.form['password']

		# Create cursor
		cur = mysql.connection.cursor()

		# Get user by username
		result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

		if result > 0:
			# Get stored hash
			data = cur.fetchone()
			password = data['password']

			# Compare passwords
			if sha256_crypt.verify(password_candidate, password):
			    # Passed
			    session['logged_in'] = True
			    session['username'] = username

			    # flash('You are now logged in', 'success')
			    return redirect(url_for('dashboard'))
			else:
				error = 'Invalid login'
				return render_template('login.html', error=error)
			# Close connection
			cur.close()
		else:
			error = 'Username not found'
			return render_template('login.html', error=error)

	return render_template('login.html')

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

# Logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	# flash('You are now logged out', 'success')
	return redirect(url_for('login'))

# Register form class
class RegisterForm(Form):
	username = StringField('Username', [validators.Length(min=4, max=25)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm password')

# User register
@app.route('/register', methods=['GET', 'POST'])
@is_logged_in
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		
		# Create cursor
		cur = mysql.connection.cursor()

		# Execute query
		cur.execute("INSERT INTO users(username, password) VALUES(%s, %s)", (username, password))

		# Commit to DB
		mysql.connection.commit()

		# Close connection
		cur.close()

		flash('New user registered', 'success' )

		return redirect(url_for('dashboard'))
	return render_template('register.html', form=form)

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	return render_template('dashboard.html')

# Clients
@app.route('/clients')
@is_logged_in
def clients():
	return render_template('clients.html')

# Private Clients
@app.route('/private_clients')
@is_logged_in
def private_clients():
	# Create cursor
	cur = mysql.connection.cursor()

	# Get Private Clients
	result = cur.execute("SELECT * FROM clients WHERE type = 'private'")

	clients = cur.fetchall()

	if result > 0:
		return render_template('private_clients.html', clients=clients)
	else:
		msg = 'No Clients Found'
		return render_template('private_clients.html', msg=msg)

	# Close connection
	cur.close()

# Private Client Form Class
class PrivateClientForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=100)])
	payment_scheme = SelectField('Payment scheme', choices=[('Post delivery', 'Post delivery'), ('Prepayment', 'Prepayment')])
	phone = StringField('Phone', [validators.Length(max=30)])
	email = StringField('Email', [validators.Length(max=100)])
	address = StringField('Address', [validators.Length(min=1, max=255)])
	door_code = StringField('Door code', [validators.Length(max=100)])
	zone = SelectField('Zone', choices=[('Macau', 'Macau'), ('Taipa', 'Taipa'), ('Coloane', 'Coloane'), ('Cotai', 'Cotai')])
	
# Add Private Client
@app.route('/add_private_client', methods=['GET', 'POST'])
@is_logged_in
def add_private_client():
	form = PrivateClientForm(request.form)
	
	if request.method == 'POST' and form.validate():
		name = form.name.data
		payment_scheme = form.payment_scheme.data
		phone = form.phone.data
		email = form.email.data
		address = form.address.data
		door_code = form.door_code.data
		zone = form.zone.data
						
		# Create Cursor
		cur = mysql.connection.cursor()

		# Execute
		cur.execute("INSERT INTO clients(name, type, payment_scheme, phone_one, email_one, address, door_code, zone) VALUES(%s, 'private', %s, %s, %s, %s, %s, %s)", (name, payment_scheme, phone, email, address, door_code, zone))

		# Commit to DB
		mysql.connection.commit()

		# Close connection
		cur.close()

		flash('Client Created', 'success')

		return redirect(url_for('private_clients'))

	return render_template('add_private_client.html', form=form)

# Edit Private Client
@app.route('/edit_private_client/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_private_client(id):
	# Create Cursor
	cur = mysql.connection.cursor()

	# Get private client by id
	result = cur.execute("SELECT * FROM clients WHERE id = %s", [id])

	client = cur.fetchone()

	# Get form 
	form = PrivateClientForm(request.form)
	form.name.data = client['name']
	form.payment_scheme.data = client['payment_scheme']
	form.phone.data = client['phone_one']
	form.email.data = client['email_one']
	form.address.data = client['address']
	form.door_code.data = client['door_code']
	form.zone.data = client['zone']
	


	if request.method == 'POST' and form.validate():
		name = request.form['name']
		payment_scheme = request.form['payment_scheme']
		phone = request.form['phone']
		email = request.form['email']
		address = request.form['address']
		door_code = request.form['door_code']
		zone = request.form['zone']
		
		# Create Cursor
		cur = mysql.connection.cursor()

		# Execute
		cur.execute("UPDATE clients SET name=%s, payment_scheme=%s, phone_one=%s, email_one=%s, address=%s, door_code=%s, zone=%s WHERE id=%s", (name, payment_scheme, phone, email, address, door_code, zone, id))

		# Commit to DB
		mysql.connection.commit()

		# Close connection
		cur.close()

		flash('Client Updated', 'success')

		return redirect(url_for('private_clients'))
	else:
		print(form.errors)
	return render_template('edit_private_client.html', form=form)



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

# Retail Client Form Class
class RetailClientForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=100)])
	retail_type = SelectField('Retail type', choices=[('Restaurant', 'Restaurant'), ('Supermarket', 'Supermarket')])
	delivery_time = SelectField('Delivery time', choices=[])
	payment_scheme = SelectField('Payment scheme', choices=[('CoD', 'CoD'), ('WB', 'WB'), ('MB', 'MB'), ('TBC', 'TBC')])
	statement_delivery_method = SelectField('Statement delivery method', choices=[('By email', 'By email'), ('By wechat', 'By wechat'), ('By hand', 'By hand'), ('Not applicable', 'Not applicable')])
	contact_person = StringField('Contact person', [validators.Length(max=100)])
	phone_one = StringField('Phone', [validators.Length(max=30)])
	email_one = StringField('Email', [validators.Length(max=100)])
	wechat_id = StringField('Wechat id', [validators.Length(max=100)])
	salesperson = SelectField('Salesperson', choices=[])
	other_info = StringField('Other info', [validators.Length(max=255)])
	
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
		cur.execute("INSERT INTO clients(name, type, retail_type, delivery_time, payment_scheme, statement_delivery_method, contact_person, phone_one, email_one, wechat_id, salesperson, other_info) VALUES(%s, 'retail', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (name, retail_type, delivery_time, payment_scheme, statement_delivery_method, contact_person, phone_one, email_one, wechat_id, salesperson, other_info))

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
		cur.execute("UPDATE clients SET name=%s, retail_type=%s, delivery_time=%s, payment_scheme=%s, statement_delivery_method=%s, contact_person=%s, phone_one=%s, email_one=%s, wechat_id=%s, salesperson=%s, other_info=%s WHERE id=%s", (name, retail_type, delivery_time, payment_scheme, statement_delivery_method, contact_person, phone_one, email_one, wechat_id, salesperson, other_info, id))

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

# Delivery Time Form Class
class Delivery_timeForm(Form):
	time = StringField('Time', [validators.Length(min=1, max=20)])

# Add Delivery Time
@app.route('/add_delivery_time', methods=['GET', 'POST'])
@is_logged_in
def add_delivery_time():
	form = Delivery_timeForm(request.form)
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
	form = Delivery_timeForm(request.form)

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

# Product Form Class
class ProductForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	product_type = SelectField('Type', choices=[('Bakery', 'Bakery'), ('Pastry', 'Pastry')])
	nr_pieces_per_bag = SelectField('Number of pieces per bag', choices=[(x, x) for x in range(1, 41)], coerce=int)
	aggregate_to = SelectField('Aggregate to', choices = [])

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
		cur.execute("INSERT INTO products(name, product_type, nr_pieces_per_bag, aggregate_to) VALUES(%s, %s, %s, %s)", (name, product_type, nr_pieces_per_bag, aggregate_to))

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
		cur.execute("UPDATE products SET name=%s, product_type=%s, nr_pieces_per_bag=%s, aggregate_to=%s WHERE id=%s", (name, product_type, nr_pieces_per_bag, aggregate_to, id))
        		
		# Commit to DB
		mysql.connection.commit()

		# Close connection
		cur.close()

		flash('Product Updated', 'success')

		return redirect(url_for('products'))
		#print old_name
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

# Price Form Class
class PriceForm(Form):
	#product = StringField('Product', [validators.Length(min=1, max=100)])
	product = SelectField('Product', choices = [])
	client_type = SelectField('Client type', choices=[('Private', 'Private'), ('Retail', 'Retail')])
	price_type = SelectField('Price type', choices=[('Standard', 'Standard'), ('Special', 'Special')])
	#client_name = StringField('Client name', [validators.Length(min=1, max=100)])
	client_name = SelectField('Client name', choices = [])
	unit_price = DecimalField('Unit price', places=2, rounding=None)

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
 		
		#price_type = form.price_type.data
		#client_name = form.client_name.data
		unit_price = form.unit_price.data

		# Create Cursor
		cur = mysql.connection.cursor()

		# Execute
		cur.execute("INSERT INTO prices(product, client_type, price_type, client_name, unit_price) VALUES(%s, %s, %s, %s, %s)", (product, client_type, price_type, client_name, unit_price))

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
		#price_type = request.form['price_type']
		#client_name = request.form['client_name']
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
		cur.execute("UPDATE prices SET product=%s, client_type=%s, price_type=%s, client_name=%s, unit_price=%s WHERE id=%s", (product, client_type, price_type, client_name, unit_price, id))
        		
		# Commit to DB
		mysql.connection.commit()

		# Close connection
		cur.close()

		flash('Price Updated', 'success')

		return redirect(url_for('prices'))
		#print old_name
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


# Salesperson Form Class
class SalespersonForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=30)])

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
	result = cur.execute("SELECT * FROM invoices INNER JOIN clients ON invoices.client_id = clients.id WHERE clients.type = 'Private'")

	invoices = cur.fetchall()

	if result > 0:
		return render_template('manage_invoices_private_clients.html', invoices=invoices)
	else:
		msg = 'No Invoices Found'
		return render_template('manage_invoices_private_clients.html', msg=msg)

	# Close connection
	cur.close()

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
	
# Edit Private Client Invoice
@app.route('/edit_invoice_private_client/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_invoice_private_client(id):
	# Create Cursor
	cur = mysql.connection.cursor()

	# Get price by id
	result = cur.execute("SELECT * FROM invoices INNER JOIN clients ON invoices.client_id = clients.id WHERE invoices.id = %s", [id])
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
			#Ficticious payment_date to avoid eliminating the form.validate() function
			payment_date = '2000-01-01'
			payment_method = ''
			payment_details = ''
		
		other_info = request.form['other_info']

		
		# Create Cursor
		cur = mysql.connection.cursor()

		# Execute
		cur.execute("UPDATE invoices SET delivery_day=%s, payment_status=%s, payment_date=%s, payment_method=%s, payment_details=%s, other_info=%s WHERE id=%s", (delivery_day, payment_status, payment_date, payment_method, payment_details, other_info, id))
        		
		# Commit to DB
		mysql.connection.commit()

		# Close connection
		cur.close()

		flash('Invoice Updated', 'success')

		return redirect(url_for('manage_invoices_private_clients'))
		
	else:
		print(form.errors)
	return render_template('edit_invoice_private_client.html', form=form)


# Convert Invoices to PDF Private Clients
@app.route('/convert_invoices_pdf_private_clients')
@is_logged_in
def convert_invoices_pdf_private_clients():
	return render_template('convert_invoices_pdf_private_clients.html')

# Invoices Retail Clients
@app.route('/invoices_retail_clients')
@is_logged_in
def invoices_retail_clients():
	return render_template('invoices_Retail_clients.html')

# Manage Invoices Retail Clients
@app.route('/manage_invoices_retail_clients')
@is_logged_in
def manage_invoices_retail_clients():
	return render_template('manage_invoices_retail_clients.html')

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

if __name__ == '__main__':
	app.run(debug = True)