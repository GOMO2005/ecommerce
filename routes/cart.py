from flask import (Blueprint, request, redirect, url_for,
                   flash, session, render_template)
from models import Product, db

cart_bp = Blueprint('cart', __name__)


def _get_cart():
    """Return cart dict from session."""
    return session.get('cart', {})


def _save_cart(cart):
    """Save cart dict to session."""
    session['cart'] = cart
    session.modified = True


@cart_bp.route('/')
def view():
    """Display shopping cart."""
    cart = _get_cart()
    items = []
    total = 0.0

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

    return render_template('cart.html', items=items, total=total)


@cart_bp.route('/add/<int:product_id>', methods=['POST'])
def add(product_id):
    """Add a product to the cart."""
    product = Product.query.get_or_404(product_id)

    if not product.in_stock:
        flash('This product is out of stock.', 'danger')
        return redirect(url_for('main.product_detail', product_id=product_id))

    quantity = request.form.get('quantity', 1, type=int)
    quantity = max(1, min(quantity, product.stock))

    cart = _get_cart()
    pid = str(product_id)

    if pid in cart:
        new_qty = cart[pid] + quantity
        if new_qty > product.stock:
            flash(f'Only {product.stock} items available in stock.', 'warning')
            new_qty = product.stock
        cart[pid] = new_qty
    else:
        cart[pid] = quantity

    _save_cart(cart)
    flash(f'"{product.name}" added to cart!', 'success')
    return redirect(url_for('cart.view'))


@cart_bp.route('/update', methods=['POST'])
def update():
    """Update cart item quantities."""
    cart = _get_cart()
    updated = False

    for pid, qty in request.form.items():
        if pid.startswith('qty_'):
            product_id = pid[4:]
            product = Product.query.get(int(product_id))
            if product:
                new_qty = max(0, min(int(qty), product.stock))
                if new_qty == 0:
                    cart.pop(str(product_id), None)
                else:
                    cart[str(product_id)] = new_qty
                updated = True

    if updated:
        _save_cart(cart)
        flash('Cart updated.', 'success')

    return redirect(url_for('cart.view'))


@cart_bp.route('/remove/<int:product_id>')
def remove(product_id):
    """Remove an item from the cart."""
    cart = _get_cart()
    pid = str(product_id)

    if pid in cart:
        product = Product.query.get(product_id)
        del cart[pid]
        _save_cart(cart)
        flash(f'"{product.name}" removed from cart.', 'info')

    return redirect(url_for('cart.view'))


@cart_bp.route('/clear')
def clear():
    """Clear the entire cart."""
    session.pop('cart', None)
    flash('Cart cleared.', 'info')
    return redirect(url_for('cart.view'))