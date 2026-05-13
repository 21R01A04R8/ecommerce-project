from flask import Flask, render_template, redirect
from flask import url_for, request, session

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SECRET KEY

app.secret_key = "ecommerce_secret"

# DATABASE SETUP

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# PRODUCT TABLE

class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    price = db.Column(db.Integer)

    image = db.Column(db.String(100))

# USER TABLE

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(100))

    password = db.Column(db.String(100))

# ORDER TABLE

class Order(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    product_name = db.Column(db.String(100))

    quantity = db.Column(db.Integer)

    payment = db.Column(db.String(100))

# CREATE DATABASE

with app.app_context():

    db.create_all()

    if Product.query.count() == 0:

        products = [

            Product(
                name='Laptop',
                price=50000,
                image='laptop.jpg'
            ),

            Product(
                name='Mobile',
                price=20000,
                image='phone.jpg'
            ),

            Product(
                name='Headphones',
                price=3000,
                image='headphones.jpg'
            )

        ]

        db.session.add_all(products)

        db.session.commit()

# CART

cart = {}

# HOME PAGE

@app.route('/')
def home():

    username = session.get('username')

    search = request.args.get('search')

    if search:

        products = Product.query.filter(
            Product.name.contains(search),
            Product.name != 'Watch'
        ).all()

    else:

        products = Product.query.filter(
            Product.name != 'Watch'
        ).all()

    return render_template(

        'index.html',

        products=products,

        username=username

    )

# ADD TO CART

@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):

    if 'username' not in session:
        return redirect(url_for('login'))

    if id in cart:

        cart[id]['quantity'] += 1

    else:

        product = Product.query.get(id)

        if product:

            cart[id] = {

                'product': product,

                'quantity': 1

            }

    return redirect(url_for('cart_page'))

# CART PAGE

@app.route('/cart')
def cart_page():

    if 'username' not in session:
        return redirect(url_for('login'))

    total = 0

    for item in cart.values():

        total += (

            item['product'].price *

            item['quantity']

        )

    return render_template(

        'cart.html',

        cart=cart,

        total=total

    )

# INCREASE QUANTITY

@app.route('/increase/<int:id>')
def increase(id):

    if id in cart:

        cart[id]['quantity'] += 1

    return redirect(url_for('cart_page'))

# DECREASE QUANTITY

@app.route('/decrease/<int:id>')
def decrease(id):

    if id in cart:

        cart[id]['quantity'] -= 1

        if cart[id]['quantity'] <= 0:

            del cart[id]

    return redirect(url_for('cart_page'))

# REMOVE ITEM

@app.route('/remove/<int:id>')
def remove(id):

    if id in cart:

        del cart[id]

    return redirect(url_for('cart_page'))

# CHECKOUT PAGE

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():

    if 'username' not in session:
        return redirect(url_for('login'))

    total = 0

    for item in cart.values():

        total += (

            item['product'].price *

            item['quantity']

        )

    if request.method == 'POST':

        name = request.form['name']

        address = request.form['address']

        phone = request.form['phone']

        payment = request.form['payment']

        for item in cart.values():

            new_order = Order(

                username=session['username'],

                product_name=item['product'].name,

                quantity=item['quantity'],

                payment=payment

            )

            db.session.add(new_order)

        db.session.commit()

        cart.clear()

        return render_template(

            'success.html',

            name=name,

            payment=payment

        )

    return render_template(

        'checkout.html',

        total=total

    )

# ORDERS PAGE

@app.route('/orders')
def orders():

    if 'username' not in session:
        return redirect(url_for('login'))

    user_orders = Order.query.filter_by(

        username=session['username']

    ).all()

    return render_template(

        'orders.html',

        orders=user_orders

    )

# LOGIN PAGE

@app.route('/login', methods=['GET', 'POST'])
def login():

    message = ""

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        user = User.query.filter_by(

            email=email,

            password=password

        ).first()

        if user:

            session['username'] = user.name

            return redirect(url_for('home'))

        else:

            message = "Invalid Email or Password"

    return render_template(

        'login.html',

        message=message

    )

# LOGOUT

@app.route('/logout')
def logout():

    session.pop('username', None)

    return redirect(url_for('login'))

# REGISTER PAGE

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']

        email = request.form['email']

        password = request.form['password']

        new_user = User(

            name=name,

            email=email,

            password=password

        )

        db.session.add(new_user)

        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# RUN APP

if __name__ == '__main__':

    app.run(debug=True)