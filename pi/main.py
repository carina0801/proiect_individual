from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from connect1 import get_sql_conn
from products_dao import get_all_products, insert_products, insert_image, delete_products, insert_user, username_exists, compare, get_product_by_id, get_user_id, get_product_by_name
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'aloe'


@app.route("/manage-products", methods=['GET', 'POST', 'DELETE'])
def manage_products():
    connection = get_sql_conn()
    if request.method == "POST":
        print("da")
        product_name = request.form.get('productName')
        price = request.form.get('price')
        unit = request.form.get('unit')

        product_image = request.files['productImage']
        image_path = f'static/{product_name}.jpg'
        product_image.save(image_path)
        insert_products(connection, product_name, price, unit)
        insert_image(connection, image_path, product_name)

    elif request.method == "DELETE":
        product_id = request.args.get('productId')  # Assuming you're passing productId as a query parameter
        delete_products(connection, product_id)
        return jsonify({"message": "Product deleted successfully"})

    connection = get_sql_conn()
    products = get_all_products(connection)
    return render_template("manage_products.html", products=products)

@app.route("/products", methods = ["GET"])
def products():
    connection = get_sql_conn()
    
    products = get_all_products(connection)
    return render_template("products.html", products=products)

@app.route("/products/search", methods=["GET"])
def search_products():
    connection = get_sql_conn()
    name = request.args.get('term')
    products = get_product_by_name(connection, name)
    return jsonify(products)





@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    connection = get_sql_conn()
    if request.method == 'POST':
        name = request.form.get('name')
        last_name = request.form.get('last_name')
        username = request.form.get('user')
        email = request.form.get('email')
        raw_password = request.form.get('password')
        hashed_password = generate_password_hash(raw_password, method='pbkdf2:sha256')
        if username_exists(connection, username):
            return jsonify({"error": "Username already exists"}), 400
        insert_user(connection, name, last_name, username, email, hashed_password)
    

#hashimg here
    #cod dao
    return render_template('singup.html')



@app.route("/logout")
def logout():
    # Clear the session data
    session.clear()

    # Redirect to the login page
    return redirect(url_for('login'))


@app.route("/login", methods = ['GET', 'POST'])
def login():
    connection = get_sql_conn()
    if request.method == 'POST':
        username = request.form.get('user')
        password= request.form.get('password')
        
        if compare(connection, username, password):
            session['authenticated'] = True
            user_id = get_user_id(connection, username)
            session['user_id'] = user_id
            print("da")
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "password or username incorrect"}), 400

    return render_template("login.html")


@app.route("/view_product/<int:product_id>")
def view_product(product_id):

    connection = get_sql_conn()
    product = get_product_by_id(connection, product_id)
    return render_template("view_product.html", product = product)



@app.route("/check_auth")
def check_auth():
    if session.get('authenticated'):
        return jsonify({'authenticated': True}), 200
    else:
        return jsonify({'authenticated': False}), 401
    


@app.route("/cart/<int:product_id>", methods=['POST', 'GET', 'DELETE'])
def add_cart(product_id):
    if not session.get('authenticated'):
        return jsonify({'error': 'User not authenticated'}), 401

    # Retrieve the user's cart from the session, or create an empty cart
    cart = session.get('cart', [])
    quantity = request.json.get('quantity', 1)

    # Add the product_id to the cart along with the quantity
    cart.append({'product_id': product_id, 'quantity': quantity})
    print(cart)
    print("nu")
    # Update the session with the modified cart

    session['cart'] = cart

    return jsonify({'message': 'Product added to cart successfully'}), 200



@app.route("/view_cart", methods = ['GET', 'POST', 'DELETE'])
def view_cart():
    if request.method == "DELETE":
        product_id = int(request.args.get('productId'))  # Assuming you're passing productId as a query parameter
        cart = session.get('cart', [])
        
        # Filter out the item with the specified product_id
        updated_cart = [item for item in cart if item['product_id'] != product_id]

        # Update the session with the modified cart
        session['cart'] = updated_cart

        return jsonify({"message": "Item deleted successfully"})

    cart = session.get('cart', [])
    print(cart, "nu")
   
    connection = get_sql_conn()
    # Fetch additional product information from the database
    cart_items = []
    for item in cart:
        product_id = item['product_id']
        quantity = item['quantity']
        product_info = get_product_by_id(connection, product_id)
        if product_info:
            item_info = {
                'product_info': product_info,
                'quantity': quantity
            }
            product_info['price'] = round(product_info["price"]* float(item_info['quantity']), 2)

            cart_items.append(item_info)

    return render_template("cart.html", cart_items=cart_items)





if __name__ == "__main__":
    app.run(debug=True)