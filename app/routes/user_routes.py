from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify, session
import razorpay
import os
from datetime import datetime
from app.auth import login_required_user as login_required, current_user
from app.models import db, User, Product, Transaction, Address, Payment
from sqlalchemy import or_
from app.services.recommendation_service import RecommendationService

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    products = Product.query.limit(12).all()
    return render_template('index.html', products=products)

@user_bp.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'POST':
        # Logic to calculate skin type and concerns from 6 questions
        answers = request.form
        
        # 1. Skin Feeling (Basic Type)
        q1 = answers.get('q1')
        skin_type = q1 if q1 else 'normal'
        
        # 2. Sensitivity check
        q3 = answers.get('q3')
        if q3 == 'sensitive':
            skin_type = 'sensitive'
            
        # 3. Build concerns list
        concerns = []
        if answers.get('q2') == 'frequent': concerns.append('Acne')
        if answers.get('q5') == 'yes': concerns.append('Dark Spots')
        if answers.get('q6') == 'yes': concerns.append('Dryness')
        
        if current_user.is_authenticated:
            current_user.skin_type = skin_type
            current_user.set_concerns(concerns)
            
            # Save raw quiz results for profile intelligence
            res_dict = answers.to_dict()
            from datetime import datetime
            res_dict['analyzed_at'] = datetime.now().strftime('%d %b %Y')
            current_user.set_quiz_results(res_dict)
            
            db.session.commit()
            flash('Your skin profile has been updated based on the analysis!', 'success')
            return redirect(url_for('user.profile'))
        else:
            # Store in session for guests to see results immediately
            from flask import session
            session['guest_skin_type'] = skin_type
            session['guest_concerns'] = concerns
            flash('Analysis complete! Log in to save these results to your profile.', 'info')
            return redirect(url_for('user.products', skin_type=skin_type))
            
    return render_template('analysis.html')

@user_bp.route('/about')
def about():
    return render_template('about.html')

@user_bp.route('/products')
def products():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.brand.ilike(f'%{search}%'))
    if category:
        query = query.filter(Product.category == category)
        
    products_list = query.limit(200).all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('products.html', products=products_list, categories=categories, search=search, current_category=category)

@user_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    from flask import session
    cart = session.get('cart', {})
    current_qty = cart.get(str(product_id), 0)
    
    if current_qty >= 6:
        flash('Maximum quantity (6) reached for this product.', 'warning')
        return redirect(url_for('user.view_cart'))
        
    cart[str(product_id)] = current_qty + 1
    session['cart'] = cart
    flash('Product added to your cart!', 'success')
    return redirect(url_for('user.view_cart'))

@user_bp.route('/cart')
@login_required
def view_cart():
    from flask import session
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            cart_items.append({'product': product, 'quantity': qty})
            total += product.price * qty
    return render_template('cart.html', cart_items=cart_items, total=total)

@user_bp.route('/cart/update/<int:product_id>/<action>')
@login_required
def update_cart(product_id, action):
    from flask import session
    cart = session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        if action == 'increase':
            if cart[pid] < 6:
                cart[pid] += 1
            else:
                flash('Maximum quantity limit (6) reached!', 'warning')
        elif action == 'decrease' and cart[pid] > 1:
            cart[pid] -= 1
    session['cart'] = cart
    return redirect(url_for('user.view_cart'))

@user_bp.route('/buy-now/<int:product_id>')
@login_required
def buy_now(product_id):
    from flask import session
    cart = session.get('cart', {})
    cart[str(product_id)] = 1
    session['cart'] = cart
    return redirect(url_for('user.checkout'))

@user_bp.route('/buy-again/<int:order_id>')
@login_required
def buy_again(order_id):
    from flask import session
    order = Transaction.query.filter_by(id=order_id, user_id=current_user.id).first()
    
    if not order:
        flash('Order not found or access denied.', 'danger')
        return redirect(url_for('user.profile'))
        
    # Ensure correct product mapping using product_id
    product = Product.query.get(order.product_id)
    if not product:
        # Fallback message
        flash('Sorry, this product is no longer available.', 'warning')
        return redirect(url_for('user.profile'))
        
    # Add that product to cart table
    cart = session.get('cart', {})
    current_qty = cart.get(str(product.id), 0)
    
    if current_qty >= 6:
        flash('Maximum quantity (6) reached for this product.', 'warning')
    else:
        cart[str(product.id)] = current_qty + 1
        session['cart'] = cart
        flash(f'{product.name} has been added to your cart!', 'success')
        
    return redirect(url_for('user.view_cart'))

@user_bp.route('/buy/<int:product_id>', methods=['POST', 'GET'])
@login_required
def buy_direct(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Create the transaction immediately (Direct Buy)
    transaction = Transaction(
        user_id=current_user.id,
        product_id=product.id,
        amount=product.price,
        quantity=1,
        status='pending'  # Initial status for direct buy
    )
    db.session.add(transaction)
    db.session.flush()

    # Create a payment record (Cash on Delivery default)
    from app.models import Payment
    payment = Payment(
        transaction_id=transaction.id,
        payment_method='Cash on Delivery',
        payment_status='pending',
        amount_paid=product.price
    )
    db.session.add(payment)
    db.session.commit()
    
    flash(f'Successfully placed order for {product.name}!', 'success')
    return redirect(url_for('user.profile'))

@user_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Retrieve user skin profile details
    if current_user.is_authenticated:
        user_skin_type = current_user.skin_type or 'normal'
        user_concerns = current_user.get_concerns()
        user_budget = current_user.budget
        user_sensitivity = current_user.sensitivity
    else:
        user_skin_type = session.get('guest_skin_type', 'normal')
        user_concerns = session.get('guest_concerns', [])
        user_budget = 2000.0
        user_sensitivity = 'mild'
        
    analysis = RecommendationService.get_dermiq_analysis(
        user_skin_type, user_concerns, user_sensitivity, user_budget, product
    )
    
    # Also fetch related products based on category for 'You may also like'
    related = Product.query.filter(Product.category == product.category, Product.id != product.id).limit(4).all()
    return render_template('product_detail.html', product=product, related=related, analysis=analysis)

@user_bp.route('/cart/remove/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    from flask import session
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    session['cart'] = cart
    return redirect(url_for('user.view_cart'))

@user_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    from flask import session
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('user.products'))
        
    if request.method == 'POST':
        # Retrieve form data
        phone = request.form.get('phone')
        street_address = request.form.get('street_address')
        city = request.form.get('city')
        state = request.form.get('state')
        pin_code = request.form.get('pin_code')
        
        # Verify inputs are not empty
        if not all([phone, street_address, city, state, pin_code]):
            flash('All shipping address fields are required.', 'danger')
            return redirect(url_for('user.checkout'))
            
        # Check if address already exists to prevent duplicate entries
        address = Address.query.filter_by(
            user_id=current_user.id,
            street_address=street_address,
            city=city,
            state=state,
            pin_code=pin_code
        ).first()
        
        if not address:
            # Check if this is the first address to make it default
            is_default = not Address.query.filter_by(user_id=current_user.id).first()
            if is_default:
                Address.query.filter_by(user_id=current_user.id).update({'is_default': False})
                
            address = Address(
                user_id=current_user.id,
                full_name=current_user.name,
                phone=phone,
                street_address=street_address,
                city=city,
                state=state,
                pin_code=pin_code,
                is_default=is_default
            )
            db.session.add(address)
            db.session.commit()
            
        # Save selected address ID in session
        session['checkout_address_id'] = address.id
        return redirect(url_for('user.payment'))
        
    # GET logic: find default or first address to autofill
    default_address = Address.query.filter_by(user_id=current_user.id, is_default=True).first()
    if not default_address:
        default_address = Address.query.filter_by(user_id=current_user.id).first()
    
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            cart_items.append({'product': product, 'quantity': qty})
            total += product.price * qty
            
    return render_template('checkout.html', cart_items=cart_items, total=total, default_address=default_address)

@user_bp.route('/payment')
@login_required
def payment():
    return render_template('payment.html')

@user_bp.route('/payment/process/<method>')
@login_required
def process_payment(method):
    from flask import session
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('user.index'))
    
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            total += product.price * qty
            
    return render_template('process_payment.html', method=method, total=total)

@user_bp.route('/create-order', methods=['POST'])
@login_required
def create_order():
    data = request.get_json(silent=True) or {}
    amount_in_rupees = data.get('amount')
    
    if not amount_in_rupees:
        return jsonify({'error': 'Amount is required'}), 400
        
    try:
        amount_in_paise = int(round(float(amount_in_rupees) * 100))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount format'}), 400
    
    KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
    
    if not KEY_ID or not KEY_SECRET:
        return jsonify({'error': 'Razorpay keys not configured on server'}), 500
        
    client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))
    
    order_data = {
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": f"receipt_{current_user.id}_{int(datetime.utcnow().timestamp())}",
        "payment_capture": 1
    }
    
    try:
        order = client.order.create(data=order_data)
        return jsonify({
            'order_id': order['id'],
            'amount': amount_in_rupees,
            'currency': 'INR'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/payment/razorpay/checkout', methods=['POST'])
@login_required
def razorpay_checkout():
    from flask import session
    cart = session.get('cart', {})
    if not cart:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Get address_id from request
    data_req = request.get_json(silent=True) or {}
    address_id = data_req.get('address_id')
    
    if not address_id:
        return jsonify({'error': 'Please select a shipping address'}), 400
        
    # Validate address
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first()
    if not address:
        return jsonify({'error': 'Invalid address selected'}), 400
    
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            total = round(total + (product.price * qty), 2)
            
    # Use environment variables for production/test
    KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
    
    if not KEY_ID or not KEY_SECRET:
        return jsonify({'error': 'Razorpay keys not configured on server'}), 500
        
    client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))
    
    # Create Razorpay Order
    order_data = {
        "amount": int(round(total * 100)), # Amount in paise
        "currency": "INR",
        "receipt": f"receipt_{current_user.id}_{int(datetime.utcnow().timestamp())}",
        "payment_capture": 1,
        "notes": {
            "customer_id": current_user.id,
            "customer_email": current_user.email,
            "order_type": "Skincare Professional Routine"
        }
    }
    
    try:
        order = client.order.create(data=order_data)
        return jsonify({
            'order_id': order['id'],
            'amount_paise': order_data['amount'],
            'amount': total,
            'currency': 'INR',
            'key': KEY_ID,
            'user_name': current_user.name,
            'user_email': current_user.email,
            'user_phone': address.phone
        })
    except Exception as e:
        return jsonify({'error': f"Razorpay Error: {str(e)}"}), 500

@user_bp.route('/payment/razorpay/verify', methods=['POST'])
@login_required
def razorpay_verify():
    from flask import session
    data = request.get_json(silent=True) or {}
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')
    address_id = data.get('address_id')
    
    # Initialize Razorpay Client
    KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
    
    if not KEY_ID or not KEY_SECRET:
        return jsonify({'status': 'failure', 'error': 'Keys not configured'}), 400
        
    client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))
    
    # Verify Signature
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }
    
    try:
        client.utility.verify_payment_signature(params_dict)
        
        # Create records
        cart = session.get('cart', {})
        for pid, qty in cart.items():
            product = Product.query.get(int(pid))
            if product:
                transaction = Transaction(
                    user_id=current_user.id,
                    product_id=product.id,
                    amount=product.price * qty,
                    quantity=qty,
                    address_id=address_id,
                    status='completed'
                )
                db.session.add(transaction)
                db.session.flush()
                
                payment_record = Payment(
                    transaction_id=transaction.id,
                    payment_method='ONLINE',
                    payment_status='paid',
                    amount_paid=transaction.amount,
                    transaction_ref=razorpay_payment_id
                )
                db.session.add(payment_record)
                
        db.session.commit()
        session['cart'] = {}
        return jsonify({'status': 'success'})
        
    except Exception as e:
        return jsonify({'status': 'failure', 'error': str(e)}), 400

@user_bp.route('/order/confirm', methods=['POST'])
@login_required
def confirm_order():
    from flask import session
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('user.index'))
    
    method = request.form.get('method', 'COD')
    address_id = request.form.get('address_id')
    
    if not address_id:
        flash('Please select a shipping address.', 'warning')
        return redirect(request.referrer)
        
    # Validate ownership
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first()
    if not address:
        flash('Invalid address selected.', 'danger')
        return redirect(request.referrer)
    
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            transaction = Transaction(
                user_id=current_user.id,
                product_id=product.id,
                amount=product.price * qty,
                quantity=qty,
                address_id=address_id,
                status='completed'
            )
            db.session.add(transaction)
            db.session.flush()
            
            payment_record = Payment(
                transaction_id=transaction.id,
                payment_method=method,
                payment_status='paid' if method != 'COD' else 'pending',
                amount_paid=transaction.amount
            )
            db.session.add(payment_record)

    db.session.commit()
    session['cart'] = {}
    flash('Order confirmed successfully!', 'success')
    return redirect(url_for('user.profile'))

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Update user profile information from form inputs
        current_user.name = request.form.get('name', current_user.name)
        current_user.skin_type = request.form.get('skin_type', current_user.skin_type)
        current_user.set_concerns(request.form.getlist('concerns'))
        
        budget = request.form.get('budget')
        if budget:
            current_user.budget = float(budget)
            
        current_user.sensitivity = request.form.get('sensitivity', 'mild')
        db.session.commit()
        
        if request.args.get('autosubmit') != 'true':
            flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))
        
    # Get user recommendations and routine
    advice = RecommendationService.get_expert_advice(current_user.skin_type, current_user.get_concerns())
    routine = RecommendationService.generate_routine(current_user)
    
    # Retrieve user transactions and group duplicate products
    purchases = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    grouped = {}
    for t in purchases:
        if t.product_id not in grouped:
            grouped[t.product_id] = {
                'id': t.id,
                'product': t.product,
                'product_id': t.product_id,
                'amount': t.amount,
                'date': t.date,
                'status': t.status,
                'order_count': 1
            }
        else:
            grouped[t.product_id]['order_count'] += 1
            
    return render_template('profile.html', user=current_user, transactions=list(grouped.values()), routine=routine, advice=advice)

@user_bp.route('/address/add', methods=['POST'])
@login_required
def add_address():
    full_name = request.form.get('full_name')
    phone = request.form.get('phone')
    street_address = request.form.get('street_address')
    city = request.form.get('city')
    state = request.form.get('state')
    pin_code = request.form.get('pin_code')
    is_default = 'is_default' in request.form
    
    if not all([full_name, phone, street_address, city, state, pin_code]):
        flash('All address details are compulsory.', 'danger')
        return redirect(request.referrer or url_for('user.profile'))
        
    # If is_default, clear other defaults
    if is_default:
        Address.query.filter_by(user_id=current_user.id).update({'is_default': False})
        
    # If this is the only address, make it default regardless
    if not Address.query.filter_by(user_id=current_user.id).first():
        is_default = True
        
    new_address = Address(
        user_id=current_user.id,
        full_name=full_name,
        phone=phone,
        street_address=street_address,
        city=city,
        state=state,
        pin_code=pin_code,
        is_default=is_default
    )
    db.session.add(new_address)
    db.session.commit()
    
    flash('Address added successfully!', 'success')
    return redirect(request.referrer or url_for('user.profile'))

@user_bp.route('/address/delete/<int:address_id>', methods=['POST'])
@login_required
def delete_address(address_id):
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    
    was_default = address.is_default
    
    # Nullify address references in transactions to avoid IntegrityError (foreign key constraint)
    Transaction.query.filter_by(address_id=address_id).update({'address_id': None})
    
    db.session.delete(address)
    db.session.commit()

    
    # If the default was deleted, set the most recent address as default if any exist
    if was_default:
        new_default = Address.query.filter_by(user_id=current_user.id).order_by(Address.created_at.desc()).first()
        if new_default:
            new_default.is_default = True
            db.session.commit()
            
    flash('Address removed.', 'info')
    return redirect(request.referrer or url_for('user.profile'))

@user_bp.route('/address/default/<int:address_id>', methods=['POST'])
@login_required
def set_default_address(address_id):
    Address.query.filter_by(user_id=current_user.id).update({'is_default': False})
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    address.is_default = True
    db.session.commit()
    flash('Default address updated.', 'success')
    return redirect(request.referrer or url_for('user.profile'))

@user_bp.route('/api/recommend', methods=['GET'])
def api_recommend():
    skin_type = request.args.get('skin_type', 'normal')
    budget_raw = request.args.get('budget', '2000')
    concerns_raw = request.args.get('concerns', '')
    
    try:
        budget = float(budget_raw)
    except ValueError:
        budget = 2000.0

    concerns = [c.strip() for c in concerns_raw.split(',') if c.strip()] if concerns_raw else []

    # Get all products
    products = Product.query.all()
    scored_products = []
    
    for p in products:
        score = RecommendationService.calculate_compatibility_score(skin_type, concerns, 'mild', p)
        if p.price <= budget:
            scored_products.append({
                'product': p.name,
                'brand': p.brand,
                'category': p.category,
                'price': p.price,
                'score': score,
                'reason': f"Matches {skin_type} skin & concerns | rating: {p.rating} | fits budget"
            })
            
    # Sort by score descending
    scored_products.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({
        'skin_type': skin_type,
        'budget': budget,
        'concerns': concerns,
        'recommendations': scored_products[:10]
    })

@user_bp.route('/api/analyze', methods=['GET'])
def api_analyze():
    from sqlalchemy import func
    total_products = Product.query.count()
    avg_rating = db.session.query(func.avg(Product.rating)).scalar() or 0.0
    avg_rating = round(float(avg_rating), 2)
    
    best_brand_query = db.session.query(
        Product.brand, func.avg(Product.rating)
    ).group_by(Product.brand).having(func.count(Product.id) >= 3).order_by(func.avg(Product.rating).desc()).first()
    best_brand = best_brand_query[0] if best_brand_query else "Cerave"
    
    return jsonify({
        'kpis': {
            'total_products': total_products,
            'average_rating': avg_rating
        },
        'best_brand': best_brand
    })

