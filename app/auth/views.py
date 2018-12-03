from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user

from ..models import Users
from . import auth
from .forms import *


# User register
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            Users.create_new(form.username.data, form.password.data)
            flash('New user registered', 'success')
            return redirect(url_for('login'))
        except Exception as error:
            flash(error, 'danger')
    return render_template('auth/register.html', form=form)


# User login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get('next') or url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.get_by_username(form.username.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('Logged in successfully as {}'.format(user.username), 'success')
            return redirect(request.args.get('next') or url_for('dashboard'))
        flash('Incorrect username or password', 'danger')
    return render_template('auth/login.html', form=form)


# Logout
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are now logged out', 'success')
    return redirect(url_for('auth.login'))
