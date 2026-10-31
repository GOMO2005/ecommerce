from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)
from flask_login import login_required, current_user
from models import Product, Order, OrderItem, db
from forms import CheckoutForm
from routes.cart import _get_cart, _save_cart

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page - place an order."""
    cart = _get_cart()
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('main.index'))

    # Build items and calculate total
    items = []
    total = 0.0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product and product.in_stock:
            subtotal = product.price * qty
            total += subtotal
            items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})

    if not items:
        flash('No valid items in cart.', 'warning')
        return redirect(url_for('cart.view'))

    form = CheckoutForm()
    if form.validate_on_submit():
        # Check stock again
        for item in items:
            p = Product.query.get(item['product'].id)
            if p.stock < item['quantity']:
                flash(f'Not enough stock for "{p.name}". Only {p.stock} left.', 'danger')
                return redirect(url_for('cart.view'))

        # Create order
        order = Order(
            user_id=current_user.id,
            total_amount=total,
            shipping_name=form.full_name.data,
            shipping_address=form.address.data,
            shipping_city=form.city.data,
            shipping_state=form.state.data,
            shipping_zip=form.zip_code.data,
            shipping_phone=form.phone.data,
            status='pending'
        )
        db.session.add(order)

        # Create order items and decrease stock
        for item in items:
            oi = OrderItem(
                order=order,
                product_id=item['product'].id,
                quantity=item['quantity'],
                price=item['product'].price
            )
            db.session.add(oi)
            product = Product.query.get(item['product'].id)
            product.stock -= item['quantity']

        db.session.commit()

        # Clear cart
        session.pop('cart', None)

        flash(f'Order #{order.id} placed successfully!', 'success')
        return redirect(url_for('orders.order_detail', order_id=order.id))

    return render_template('checkout.html', form=form, items=items, total=total)


@orders_bp.route('/')
@login_required
def list_orders():
    """List user's orders."""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc())\
        .paginate(page=page, per_page=10)
    return render_template('orders.html', orders=orders)


@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    """View a single order."""
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this order.', 'danger')
        return redirect(url_for('orders.list_orders'))
    return render_template('order_detail.html', order=order)