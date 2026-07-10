from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
import os
from werkzeug.utils import secure_filename
from app.auth import login_required_admin
from app.models import db, User, Product, Transaction
from functools import wraps

# Create admin blueprint
admin_bp = Blueprint('admin', __name__)



# Helper function to save uploaded image file
def save_image(file):
    if not file:
        return None
    
    filename = secure_filename(file.filename)
    upload_folder = os.path.join('app', 'static', 'uploads', 'products')
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # Return file path for URL
    return url_for('static', filename='uploads/products/' + filename)

# Calculate analytics for admin dashboard using basic python loops
def get_dashboard_analytics():
    import json
    
    # Get all tables from database
    users = User.query.all()
    products = Product.query.all()
    transactions = Transaction.query.all()
    
    # Simple counts
    total_users = len(users)
    total_products = len(products)
    total_transactions = len(transactions)
    
    # Calculate total revenue
    total_revenue = 0.0
    for t in transactions:
        total_revenue += t.amount
        
    # Group transactions monthly using a python dictionary
    monthly_map = {}
    for t in transactions:
        month = t.date.strftime('%b %Y')
        if month not in monthly_map:
            monthly_map[month] = {
                'month': month,
                'revenue': 0.0,
                'orders': 0,
                'raw_date': t.date
            }
        monthly_map[month]['revenue'] += t.amount
        monthly_map[month]['orders'] += 1
        
    # Sort months by date
    sorted_months = sorted(monthly_map.values(), key=lambda x: x['raw_date'])
    monthly_data = sorted_months[-6:]
    
    # Calculate skin type distribution
    skin_types = {}
    for u in users:
        if u.skin_type:
            st = u.skin_type.strip()
            skin_types[st] = skin_types.get(st, 0) + 1
            
    # Calculate product sales quantities
    product_sales = {}
    for t in transactions:
        if t.product:
            p_name = t.product.name
            product_sales[p_name] = product_sales.get(p_name, 0) + t.quantity
            
    # Sort product sales descending and get top 5
    sorted_sales = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)
    top_products = dict(sorted_sales[:5])
    
    # Parse concerns from json user profiles
    concern_counts = {}
    for u in users:
        if u.concerns:
            try:
                concerns_list = json.loads(u.concerns)
                for c in concerns_list:
                    c_clean = c.strip()
                    concern_counts[c_clean] = concern_counts.get(c_clean, 0) + 1
            except:
                pass
                
    # Sort concerns descending and take top 6
    sorted_concerns = sorted(concern_counts.items(), key=lambda x: x[1], reverse=True)
    top_concerns = dict(sorted_concerns[:6])
    
    # Count age groups
    age_groups = {
        '18-24': 0,
        '25-34': 0,
        '35-44': 0,
        '45+': 0
    }
    for u in users:
        if u.age:
            if 18 <= u.age <= 24:
                age_groups['18-24'] += 1
            elif 25 <= u.age <= 34:
                age_groups['25-34'] += 1
            elif 35 <= u.age <= 44:
                age_groups['35-44'] += 1
            elif u.age >= 45:
                age_groups['45+'] += 1
                
    return {
        'total_users': total_users,
        'total_products': total_products,
        'total_transactions': total_transactions,
        'total_revenue': total_revenue,
        'monthly_data': monthly_data,
        'skin_types': skin_types,
        'top_products': top_products,
        'concern_counts': top_concerns,
        'age_groups': age_groups
    }

# Redirect admin root to dashboard
@admin_bp.route('/')
@login_required_admin
def index():
    return redirect(url_for('admin.dashboard'))

# Dashboard view route
@admin_bp.route('/dashboard')
@login_required_admin
def dashboard():
    analytics = get_dashboard_analytics()
    return render_template('admin/admin_dashboard.html', **analytics)

# Products list view route
@admin_bp.route('/products', methods=['GET'])
@login_required_admin
def products():
    search = request.args.get('search', '')
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.brand.ilike(f'%{search}%'))
    
    products_list = query.all()
    return render_template('admin/admin_products.html', products=products_list, search=search)

# Add product route
@admin_bp.route('/product/add', methods=['GET', 'POST'])
@login_required_admin
def add_product():
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Save image file if uploaded
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename != '':
                image_url = save_image(file)
                if image_url:
                    data['image_url'] = image_url

        # Create new product record in db
        product = Product(
            name=data.get('name', ''),
            brand=data.get('brand', ''),
            category=data.get('category', ''),
            price=float(data.get('price', 0) or 0),
            rating=float(data.get('rating', 0) or 0),
            ingredients=data.get('ingredients', ''),
            description=data.get('description', ''),
            image_url=data.get('image_url', ''),
            suitable_for=data.get('suitable_for', ''),
            concerns=data.get('concerns', ''),
            stock=int(data.get('stock', 100) or 100),
            is_active=bool(int(data.get('is_active', 1) or 1))
        )
        db.session.add(product)
        db.session.commit()

        flash('Product added successfully.', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/admin_product_form.html', action='Add', product=None)

# Edit product route
@admin_bp.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required_admin
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Save image file if uploaded
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename != '':
                image_url = save_image(file)
                if image_url:
                    data['image_url'] = image_url

        # Update product fields directly
        product.name = data.get('name', product.name)
        product.brand = data.get('brand', product.brand)
        product.category = data.get('category', product.category)
        product.price = float(data.get('price', product.price) or 0)
        product.rating = float(data.get('rating', product.rating) or 0)
        product.ingredients = data.get('ingredients', product.ingredients)
        product.description = data.get('description', product.description)
        product.image_url = data.get('image_url', product.image_url)
        product.suitable_for = data.get('suitable_for', product.suitable_for)
        product.concerns = data.get('concerns', product.concerns)
        product.stock = int(data.get('stock', product.stock or 100) or 100)
        product.is_active = bool(int(data.get('is_active', 1) or 1))
        db.session.commit()

        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/admin_product_form.html', action='Edit', product=product)

# Delete product route
@admin_bp.route('/product/delete/<int:id>', methods=['POST'])
@login_required_admin
def delete_product(id):
    from app.models import Transaction, Payment
    product = Product.query.get_or_404(id)
    
    # Get associated transactions
    transactions = Transaction.query.filter_by(product_id=product.id).all()
    transaction_ids = [t.id for t in transactions]
    
    # Delete child payments and transactions
    if transaction_ids:
        Payment.query.filter(Payment.transaction_id.in_(transaction_ids)).delete(synchronize_session=False)
        Transaction.query.filter(Transaction.id.in_(transaction_ids)).delete(synchronize_session=False)
        
    # Delete product
    db.session.delete(product)
    db.session.commit()

    flash('Product deleted successfully.', 'success')
    return redirect(url_for('admin.products'))

# Users list view route
@admin_bp.route('/users')
@login_required_admin
def users():
    users_list = User.query.all()
    return render_template('admin/admin_users.html', users=users_list)

# Transactions list view route
@admin_bp.route('/transactions')
@login_required_admin
def transactions():
    transactions_list = Transaction.query.order_by(Transaction.date.desc()).all()
    
    total_transactions = len(transactions_list)
    total_revenue = sum(t.amount for t in transactions_list)
    
    return render_template('admin/admin_transactions.html', 
        transactions=transactions_list,
        total_transactions=total_transactions,
        total_revenue=total_revenue
    )

# Delete transaction route
@admin_bp.route('/transaction/delete/<int:id>', methods=['POST'])
@login_required_admin
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    
    # Delete child payment
    from app.models import Payment
    Payment.query.filter_by(transaction_id=id).delete()
    
    # Delete transaction
    db.session.delete(transaction)
    db.session.commit()
    
    flash('Transaction deleted successfully.', 'success')
    return redirect(url_for('admin.transactions'))

# Delete user route
@admin_bp.route('/user/delete/<int:id>', methods=['POST'])
@login_required_admin
def delete_user(id):
    if id == int(session.get('admin_id')):
        flash('You cannot delete yourself.', 'error')
        return redirect(url_for('admin.users'))
        
    from app.models import Payment, Address
    user = User.query.get_or_404(id)
    
    # Delete user payments and transactions first (to free foreign key references on addresses)
    transactions = Transaction.query.filter_by(user_id=user.id).all()
    transaction_ids = [t.id for t in transactions]
    if transaction_ids:
        Payment.query.filter(Payment.transaction_id.in_(transaction_ids)).delete(synchronize_session=False)
        Transaction.query.filter(Transaction.id.in_(transaction_ids)).delete(synchronize_session=False)
        
    # Delete user addresses after transactions are deleted
    Address.query.filter_by(user_id=user.id).delete()
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.users'))


# Toggle user role (user <-> admin) route
@admin_bp.route('/user/update_role/<int:id>', methods=['POST'])
@login_required_admin
def update_role(id):
    if id == int(session.get('admin_id')):
        flash('You cannot change your own role.', 'error')
        return redirect(url_for('admin.users'))
    
    user = User.query.get_or_404(id)
    user.role = 'admin' if user.role == 'user' else 'user'
    db.session.commit()
    
    flash(f"User {user.name} is now {user.role}.", 'success')
    return redirect(url_for('admin.users'))

# Logout route
@admin_bp.route('/logout')
@login_required_admin
def logout():
    session.pop('admin_id', None)
    flash('Admin logged out successfully.', 'success')
    return redirect(url_for('auth.admin_login'))
