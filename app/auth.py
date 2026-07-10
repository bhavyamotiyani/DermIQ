# -*- coding: utf-8 -*-
"""
DermIQ - Custom Independent Authentication System
Defines isolated sessions for users (session['user_id']) and admins (session['admin_id']),
and custom middleware decorators (login_required_user, login_required_admin).
"""

from functools import wraps
from flask import session, redirect, url_for, flash, has_request_context, g
from werkzeug.local import LocalProxy
from app.models import db, User

# Custom LocalProxy for current_user (exclusively for storefront users)
def _get_current_user():
    if not has_request_context():
        return None
        
    if not hasattr(g, 'current_user'):
        user_id = session.get('user_id')
        if user_id:
            try:
                g.current_user = db.session.get(User, int(user_id))
            except Exception:
                g.current_user = None
        else:
            g.current_user = None
            
    if g.current_user is None:
        # Mimic AnonymousUser for storefront guest visitors
        class AnonymousUser:
            id = None
            name = "Guest"
            email = ""
            role = "guest"
            skin_type = None
            budget = 0.0
            sensitivity = "mild"
            concerns = None
            addresses = []
            is_authenticated = False
            
            def get_concerns(self):
                return []
                
            def get_quiz_results(self):
                return None
                
        return AnonymousUser()
        
    return g.current_user

current_user = LocalProxy(_get_current_user)

# Decorator to protect User pages
def login_required_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator to protect Admin pages
def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = session.get('admin_id')
        if not admin_id:
            # Redirect ONLY to admin login
            flash('Admin session required.', 'error')
            return redirect(url_for('auth.admin_login'))
            
        admin_user = db.session.get(User, int(admin_id))
        if not admin_user or admin_user.role != 'admin':
            session.pop('admin_id', None)
            flash('Unauthorized access.', 'error')
            return redirect(url_for('auth.admin_login'))
            
        return f(*args, **kwargs)
    return decorated_function
