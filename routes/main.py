from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, session)
from models import Product, Category, db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page - featured products and categories."""
    categories = Category.query.order_by(Category.name).all()
    featured = Product.query.filter(Product.stock > 0)\
        .order_by(Product.created_at.desc()).limit(8).all()
    return render_template('index.html', categories=categories,
                           featured=featured)


@main_bp.route('/category/<int:category_id>')
def category(category_id):
    """Products by category."""
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(category_id=category_id)\
        .filter(Product.stock > 0)\
        .order_by(Product.name)\
        .paginate(page=page, per_page=12)
    return render_template('index.html', category=category,
                           products=products, categories=Category.query.all())


@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Single product detail page."""
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.stock > 0
    ).limit(4).all()
    return render_template('product_detail.html', product=product,
                           related=related)


@main_bp.route('/search')
def search():
    """Search products by name or description."""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    products = Product.query.filter(
        (Product.name.ilike(f'%{query}%')) |
        (Product.description.ilike(f'%{query}%'))
    ).filter(Product.stock > 0)\
     .order_by(Product.name)\
     .paginate(page=page, per_page=12)

    return render_template('index.html', products=products,
                           search_query=query,
                           categories=Category.query.all())