"""Database seeder - run with: python seed.py"""
from app import create_app
from extensions import db
from models import User, Category, Product, Order, OrderItem
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, timezone  # ← Add timezone
import random

app = create_app()

SEED_DATA = {
    'categories': [
        ('Electronics', 'Gadgets, devices, and electronic accessories.'),
        ('Clothing', 'Fashion apparel for men, women, and children.'),
        ('Books', 'Fiction, non-fiction, and academic books.'),
        ('Home & Kitchen', 'Household items and kitchen essentials.'),
        ('Sports', 'Equipment and gear for various sports.'),
        ('Beauty', 'Skincare, makeup, and personal care products.'),
    ],
    'products': [
        # Electronics
        ('Wireless Bluetooth Headphones', 'Premium noise-cancelling headphones with 30-hour battery life.', 79.99, 25, 1),
        ('Smartphone Case - Clear', 'Durable clear case with shock absorption.', 19.99, 100, 1),
        ('USB-C Fast Charger 65W', 'Compact fast charger compatible with most devices.', 29.99, 50, 1),
        ('Mechanical Keyboard RGB', 'Full-size mechanical keyboard with customizable RGB lighting.', 89.99, 15, 1),
        ('Portable Bluetooth Speaker', 'Waterproof speaker with 12-hour playback time.', 49.99, 35, 1),
        ('Webcam 1080p HD', 'High-definition webcam with built-in microphone.', 39.99, 20, 1),

        # Clothing
        ('Classic Cotton T-Shirt', 'Comfortable 100% cotton t-shirt available in multiple colors.', 24.99, 200, 2),
        ('Slim Fit Denim Jeans', 'Modern slim-fit jeans with stretch comfort.', 54.99, 80, 2),
        ('Warm Winter Jacket', 'Insulated jacket with water-resistant outer shell.', 129.99, 30, 2),
        ('Running Sneakers', 'Lightweight running shoes with cushioned soles.', 74.99, 60, 2),
        ('Casual Button-Down Shirt', 'Relaxed-fit button-down perfect for any occasion.', 44.99, 45, 2),

        # Books
        ('The Art of Programming', 'A comprehensive guide to software development.', 39.99, 40, 3),
        ('Science Fiction Anthology', 'Collection of the best sci-fi short stories.', 14.99, 75, 3),
        ('World History Encyclopedia', 'Detailed encyclopedia covering world history.', 49.99, 20, 3),
        ('Cooking Masterclass', '200 recipes from beginner to advanced level.', 29.99, 55, 3),

        # Home & Kitchen
        ('Stainless Steel Knife Set', '8-piece knife set with wooden block.', 69.99, 25, 4),
        ('Non-Stick Frying Pan Set', 'Set of 3 non-stick pans in different sizes.', 44.99, 40, 4),
        ('Ceramic Coffee Mug Set', 'Set of 6 handmade ceramic mugs.', 34.99, 50, 4),
        ('Bamboo Cutting Board', 'Large eco-friendly bamboo cutting board.', 22.99, 70, 4),

        # Sports
        ('Yoga Mat Premium', 'Extra thick non-slip yoga mat with carrying strap.', 34.99, 60, 5),
        ('Resistance Bands Set', 'Set of 5 resistance bands with different strengths.', 19.99, 100, 5),
        ('Adjustable Dumbbells', 'Pair of adjustable dumbbells (5-50 lbs each).', 199.99, 10, 5),
        ('Jump Rope Speed', 'Professional speed jump rope with ball bearings.', 12.99, 80, 5),

        # Beauty
        ('Vitamin C Serum', 'Brightening serum with hyaluronic acid.', 24.99, 90, 6),
        ('Moisturizing Cream', 'Deep hydration cream for all skin types.', 19.99, 120, 6),
        ('Lip Balm Set', 'Set of 4 organic lip balms in assorted flavors.', 9.99, 150, 6),
        ('Hair Repair Shampoo', 'Sulfate-free shampoo for damaged hair.', 15.99, 85, 6),
    ]
}


def seed():
    with app.app_context():
        db.create_all()

        # Check if data already exists
        if User.query.first():
            print('Database already has data. Skipping seed.')
            return

        print('Seeding database...')

        # Create admin user
        admin = User(
            username='admin',
            email='admin@ecommerce.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)

        # Create regular user
        user = User(
            username='john',
            email='john@example.com',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(user)

        # Create categories
        categories = {}
        for name, desc in SEED_DATA['categories']:
            cat = Category(name=name, description=desc)
            db.session.add(cat)
            categories[name] = cat

        db.session.flush()

        # Create products
        products = []
        for name, desc, price, stock, cat_idx in SEED_DATA['products']:
            cat_name = SEED_DATA['categories'][cat_idx - 1][0]
            product = Product(
                name=name,
                description=desc,
                price=price,
                stock=stock,
                category_id=categories[cat_name].id,
                image_url=f'https://picsum.photos/seed/{name.lower().replace(" ", "-")}/400/400'
            )
            db.session.add(product)
            products.append(product)

        db.session.flush()

        # Create some sample orders
        statuses = ['pending', 'processing', 'shipped', 'delivered']
        for i in range(5):
            order = Order(
                user_id=user.id,
                total_amount=0,
                status=random.choice(statuses),
                shipping_name='John Doe',
                shipping_address='123 Main Street',
                shipping_city='New York',
                shipping_state='NY',
                shipping_zip='10001',
                shipping_phone='555-1234-5678',
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))  # ← Fixed
            )
            db.session.add(order)
            db.session.flush()

            # Add 1-3 items to each order
            num_items = random.randint(1, 3)
            selected = random.sample(products, min(num_items, len(products)))
            total = 0
            for prod in selected:
                qty = random.randint(1, 2)
                oi = OrderItem(
                    order_id=order.id,
                    product_id=prod.id,
                    quantity=qty,
                    price=prod.price
                )
                db.session.add(oi)
                total += prod.price * qty

            order.total_amount = total

        db.session.commit()
        print('Database seeded successfully!')
        print('\nLogin credentials:')
        print('  Admin: admin / admin123')
        print('  User:  john / password123')


if __name__ == '__main__':
    seed()