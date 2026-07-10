# -*- coding: utf-8 -*-
"""
DermIQ - Auth Routes
Handles user and admin login, registration, and logout with complete session isolation.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app.models import db, User
from app.auth import current_user, login_required_user

auth_bp = Blueprint('auth', __name__)

# Route for user login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user in database by email
        user = User.query.filter_by(email=email).first()
        
        # Check if password is correct
        if user and user.check_password(password):
            # ONLY create user_id session
            session['user_id'] = user.id
            session.permanent = True
            flash(f'Logged in as {user.name}.', 'success')
            
            # Check if there is a next page parameter
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
                
            return redirect(url_for('user.profile'))
            
        flash('Invalid email or password', 'error')
        
    return render_template('login.html')

# Route for admin login
@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user and check if role is admin
        user = User.query.filter_by(email=email).first()
        if user and user.role == 'admin' and user.check_password(password):
            # ONLY create admin_id session
            session['admin_id'] = user.id
            session.permanent = True
            flash('Admin session successfully established.', 'success')
            return redirect(url_for('admin.dashboard'))
            
        flash('Verification failed: User is not an admin or credentials invalid.', 'error')
    
    return render_template('admin/admin_login.html')

# Route for signup
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))
        
    if request.method == 'POST':
        # Get user details from signup form
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')
        name = f"{first_name} {last_name}".strip()
        email = request.form.get('email')
        password = request.form.get('password')
        skin_type = request.form.get('skin_type')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
            
        # Create user record
        user = User(
            name=name,
            email=email,
            skin_type=skin_type,
            role='user'
        )
        
        # Get concerns list
        concerns = request.form.getlist('concerns')
        if concerns:
            user.set_concerns(concerns)
            
        # Encrypt/hash password and save user
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

# Route for user logout
@auth_bp.route('/logout')
@login_required_user
def logout():
    # Only remove user_id
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('user.index'))
