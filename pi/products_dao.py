from connect1 import get_sql_conn
from werkzeug.security import generate_password_hash, check_password_hash


def get_all_products(connection):
   

    cursor = connection.cursor()

    query = ('select products.primary_id, products.product_name, products.uom_id, products.price, uom.uom_name '
             'from products join uom on products.uom_id=uom.uom_id')
    cursor.execute(query)
    
    response = []

    for (primary_id, product_name, uom_id, price, uom_name) in cursor:
        response.append({
            'primary_id': primary_id,
            'product_name':product_name,
            'uom_id':uom_id,
            'price':price,
            'uom_name': uom_name,
            'images': get_product_images(connection, primary_id)
        })
    
    return response


def get_product_by_name(connection, name):

    cursor = connection.cursor()
    query = ('select products.primary_id, products.product_name, products.uom_id, products.price, uom.uom_name '
             'from products join uom on products.uom_id=uom.uom_id '
             'where products.product_name = %s')
    
    cursor.execute(query, (name,))
    

    response = []

    for (primary_id, product_name, uom_id, price, uom_name) in cursor:
        response.append({
            'primary_id': primary_id,
            'product_name':product_name,
            'uom_id':uom_id,
            'price':price,
            'uom_name': uom_name,
            'images': get_product_images(connection, primary_id)
        })
    
    return response



def get_product_by_id(connection, primary_id):
    cursor = connection.cursor()

    query = ('select products.primary_id, products.product_name, products.uom_id, products.price, uom.uom_name '
             'from products join uom on products.uom_id=uom.uom_id '
             'where products.primary_id = %s')
    cursor.execute(query, (primary_id,))

    product = cursor.fetchone()

    if product:
        return {
            'primary_id': product[0],
            'product_name': product[1],
            'uom_id': product[2],
            'price': product[3],
            'uom_name': product[4],
            'image': get_product_image(connection, primary_id)
        }
    else:
        return None
    



def get_product_images(connection, product_id):
    cursor = connection.cursor()

    query = ('SELECT image_url FROM product_images '
             'WHERE product_id = %s')
    cursor.execute(query, (product_id,))

    images = [row[0] for row in cursor.fetchall()]

    return images

def get_product_image(connection, product_id):
    cursor = connection.cursor()

    query = ('SELECT image_url FROM product_images '
             'WHERE product_id = %s')
    cursor.execute(query, (product_id,))

    image = cursor.fetchone()

    return image[0] if image else None


def username_exists(connection, username):
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    return cursor.fetchone() is not None


def get_user_id(connection, username):
    cursor = connection.cursor()
    query = "SELECT user_id FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    return cursor.fetchone() is not None


def insert_products(connection, product_name, price, unit):
    query = ("INSERT INTO products "
        "(product_name, uom_id, price)" 
        "VALUES (%s, %s, %s)")
    
    cursor = connection.cursor()

    data = (product_name, unit, price)
    cursor.execute(query, data)
    connection.commit()
    return cursor.lastrowid

def insert_user(connection, name, last_name, username, email, hashed_password):
    query = ("INSERT INTO users "
        "(username, email, password, first_name, last_name)" 
        "VALUES (%s, %s, %s, %s, %s)")
    
    cursor = connection.cursor()

    data = (username, email, hashed_password, name, last_name)
    cursor.execute(query, data)
    connection.commit()
    return cursor.lastrowid

def get_product_id(connection, name):
    query = ("select primary_id from products "
        "where product_name = %s")
    cursor = connection.cursor()
    cursor.execute(query, (name,))

    id = [row[0] for row in cursor.fetchall()]

    return id
    

def compare(connection, username, password):
    cursor = connection.cursor()
    cursor.execute("SELECT username, password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user:
        # Assuming the stored password is hashed
        if check_password_hash(user[1], password):
            return True
        else:
            return False
    else:
        return False



def insert_image(connection, image_path, name):
    query = ("Insert into product_images "
             "(product_id, image_url)"
             "VALUES (%s, %s)")
    cursor = connection.cursor()
    id = get_product_id(connection, name)
    
    # Check if the product_id is not empty before proceeding
    if id:
        data = (id[0], image_path)
        cursor.execute(query, data)
        connection.commit()
    else:
        print(f"Product not found with name: {name}")

def delete_products(connection, primary_id):
    cursor = connection.cursor()
    query_image = ("delete from product_images where product_id=" + str(primary_id))
    query = ("delete from products where primary_id=" + str(primary_id))
    cursor.execute(query_image)
    cursor.execute(query)
    connection.commit()


