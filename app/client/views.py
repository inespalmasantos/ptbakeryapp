from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user

from .. import mysql
from ..models import Clients
from . import client
from .forms import *


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


# Clients
@client.route('/')
@login_required
def index():
    return render_template('client/clients.html')


# Private Clients
@client.route('/private-list')
@login_required
def private_clients():
    clients = Clients.query.all()
    if len(clients) > 0:
        return render_template('client/private_clients.html', clients=clients)
    else:
        msg = 'No Clients Found'
        return render_template('client/private_clients.html', msg=msg)


# Edit Private Client
@client.route('/private', methods=['GET', 'POST'])
@client.route('/private/<string:client_id>', methods=['GET', 'POST'])
@login_required
def private_client(client_id=None):
    client_obj = Clients.query.get(client_id) if client_id is not None else Clients()
    form = PrivateClientForm(obj=client_obj)
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(client_obj)
        client_obj.save()
        flash('Client Updated', 'success')
        return redirect(url_for('client.private_clients'))
    else:
        pass
    return render_template('client/private_client.html',
                           title='Add private client' if client_id is None else 'Edit private client', form=form)


# Retail Clients
@client.route('/retail-list')
@login_required
def retail_clients():
    clients = Clients.query.filter_by(type='retail').all()
    if len(clients) > 0:
        return render_template('retail_clients.html', clients=clients)
    else:
        msg = 'No Clients Found'
        return render_template('retail_clients.html', msg=msg)


# Add Retail Client
@client.route('/add_retail', methods=['GET', 'POST'])
@login_required
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
@client.route('/edit_retail/<string:id>', methods=['GET', 'POST'])
@login_required
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
        print ""
    return render_template('edit_retail_client.html', form=form)
