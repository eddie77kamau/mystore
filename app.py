from flask import Flask, render_template, url_for, request, redirect, flash, session
import pymysql
from mpesa import *


app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route("/index")
def index():
    # Establish a connection to DB 
    connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
    
    # Define SQL queries
    categories = ['snacks', 'vegetables', 'maizeflour', 'dairy', 'coookingoil', 'sugar', 'sweets', 'stationery', 'personalcare', 'ceraels', 'laundry']
    
    products = {}
    cursor = connection.cursor()

    for category in categories:
        sql = f"SELECT * FROM products WHERE category = %s"
        cursor.execute(sql, (category,))
        products[category] = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("index.html", **products)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Establishing a database connection
        connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
        cursor = connection.cursor()

        # Retrieve user from database
        sql = "SELECT * FROM users WHERE email = %s AND password = %s"
        data = (email, password)
        cursor.execute(sql, data)
        user = cursor.fetchone()

        # Check if user exists and role matches
        if user and user[5] == role:  # Assuming role is at index 5 in the result
            session['key'] = email  # Set session

            if role == 'admin':
                flash('Welcome Admin!', 'success')
                return redirect("/admin")
            else:
                flash('Welcome Customer!', 'success')
                return redirect("/index")  # Redirect to index for customers
        else:
            flash('Invalid login credentials or role!', 'danger')
            return render_template("login.html")  # Render login if unsuccessful

    return render_template("login.html")  # Render login if GET request

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        # Validate form data
        if not all([name, phone, email, password, confirm_password, role]):
            flash('All fields are required!', 'danger')
            return redirect("/signup")

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect("/signup")

        # Establish a database connection
        try:
            connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
            cursor = connection.cursor()

            # Check if the email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Email already registered! Please log in.', 'danger')
                return redirect("/signup")

            # Insert the new user into the database
            cursor.execute("""
                INSERT INTO users (username, phone, email, password, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, phone, email, password, role))

            connection.commit()
            flash(f'Successfully registered as {role.capitalize()}!', 'success')
            return redirect("/index")  # Redirect to index after successful signup
        
        except Exception as e:
            connection.rollback()
            flash(f"An error occurred: {e}", 'danger')
            return redirect("/signup")
        finally:
            cursor.close()
            connection.close()
    
    return render_template('signup.html')

@app.route('/admin')
def admin_dashboard():
    if 'key' in session:  # Ensure session key is set
        return render_template('admin.html')  # Your admin dashboard template
    else:
        flash('Please log in first!', 'warning')
        return redirect('/login')  # Redirect if not logged in


@app.route('/category/<category_name>')
def category_page(category_name):
    # Establish database connection
    connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
    cursor = connection.cursor()

    # Fetch products based on the category passed in the URL
    cursor.execute("SELECT * FROM products WHERE category = %s", (category_name,))
    products = cursor.fetchall()

    # Fetch a limited set of products for the "Similar Products" carousel (from all categories)
    cursor.execute("SELECT * FROM products LIMIT 10")  # Change this to fetch the number of products you want
    similar_products = cursor.fetchall()

    # Close connection
    connection.close()

    # Render the appropriate template, passing the products
    return render_template('category.html', products=products, category=category_name.capitalize(), similar_products=similar_products)


@app.route('/single/<int:product_id>')
def single(product_id):
    # Establish a new connection to the database
    connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
    cursor = connection.cursor()

    # Query the product from the database by ID
    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()

    # Close the connection
    cursor.close()
    connection.close()

    if product:
        return render_template('single.html', product=product)
    else:
        return "Product not found", 404

    # route for search 
@app.route('/search', methods=['GET'])
def search():
    # Get the search query from the form
    query = request.args.get('query')

    # Establish a database connection
    connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
    cursor = connection.cursor()

    # Search the database for products that match the query
    sql = "SELECT * FROM products WHERE name LIKE %s OR category LIKE %s"
    search_term = f"%{query}%"
    cursor.execute(sql, (search_term, search_term))

    # Fetch all matching products
    products = cursor.fetchall()

    # Close the connection
    cursor.close()
    connection.close()

    # Pass the search results to the search results template
    return render_template('search_results.html', products=products, query=query)


# mpesa
    # implement STK push 
    # Mpesa route with cart clearing
@app.route('/mpesa', methods=['POST'])
def mpesa():
    phone = request.form["phone"]
    amount = request.form["amount"]

    # Call the mpesa_payment function (assumes successful STK push request)
    mpesa_payment("1000", phone)

    # Clear the cart and reset item count after initiating payment
    session['cart'] = []
    session['cart_count'] = 0

    # Return a confirmation message or redirect to a new page
    return '''
        <h1>Please complete payment on your phone</h1>
        <a href="/index" class="btn btn-dark btn-sm">
            <button class="bg-info">Go back to Products</button>
        </a>
        <body style="background-image: url('/static/images/banana.webp'); 
                     background-size: contain; 
                     background-repeat: no-repeat; 
                     background-position: center;">
        </body>
    '''

   


# admin upload route 
@app.route("/upload", methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        # Get form data
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_category = request.form['product_category']
        product_image = request.files['product_image']

        # Save image to the static folder
        product_image.save('static/images/' + product_image.filename)

        # Connect to the database
        connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
        cursor = connection.cursor()

        # SQL query for inserting product data
        sql = """
        INSERT INTO products (name, price, category, image)
        VALUES (%s, %s, %s, %s)
        """
        data = (product_name, product_price, product_category, product_image.filename)

        # Execute the query
        cursor.execute(sql, data)
        connection.commit()

        # Close the connection
        cursor.close()
        connection.close()

        return render_template('upload.html', message="Product added successfully!")
    else:
        return render_template('upload.html')


@app.route("/manageproducts")
def manage_products():
    connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    connection.close()

    return render_template('manage_products.html', products=products)

# Route to edit a product (GET and POST)
@app.route("/edit_product/<int:product_id>", methods=['GET', 'POST'])
def edit_product(product_id):
    connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
    cursor = connection.cursor()

    if request.method == 'POST':
        # Update product in the database
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_cost = request.form['product_cost']
        product_category = request.form['product_category']

        sql = """UPDATE products SET product_name=%s, product_desc=%s, product_cost=%s, product_category=%s 
                 WHERE id=%s"""
        cursor.execute(sql, (product_name, product_desc, product_cost, product_category, product_id))
        connection.commit()

        return redirect('/manageproducts')

    else:
        cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        product = cursor.fetchone()
        connection.close()
        return render_template('edit_product.html', product=product)

# Route to delete a product
@app.route("/delete_product/<int:product_id>")
def delete_product(product_id):
    connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
    cursor = connection.cursor()

    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    connection.commit()
    connection.close()

    return redirect('/manageproducts')

# Route for managing users in admin dashboard
@app.route("/manageusers", methods=['GET', 'POST'])
def manage_users():
    
        connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
        cursor = connection.cursor()

        # If the request method is POST, that means the form was submitted to add a user
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            role = request.form['role']
            phone = request.form['phone']
            
            # Insert the new user into the database
            sql = "INSERT INTO users (username, email, password, role, phone) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (name, email, password, role, phone))
            connection.commit()
        
        # Fetch the users to display
        cursor.execute("SELECT id, username, email, role, phone FROM users")
        users = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('manage_users.html', users=users)
   


@app.route("/edituser/<int:user_id>", methods=['GET', 'POST'])
def edit_user(user_id):
    connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
    cursor = connection.cursor()

    cursor.execute("UPDATE FROM users WHERE id=%s", (user_id,))
    connection.commit()
    connection.close()

    return redirect('/manageusers')

@app.route("/deleteuser/<int:user_id>", methods=['POST'])
def delete_user(user_id):
    connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
    cursor = connection.cursor()

    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    connection.commit()
    connection.close()

    return redirect('/manageusers')


# cart  icon count 
@app.context_processor
def inject_cart_count():
    return {'cart_count': session.get('cart_count', 0)}

# add to cart route 
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Fetch product details (e.g., from the database) based on product_id
    connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    connection.close()

    if product:
        # Convert the price to a float (Decimal is not JSON serializable)
        price = float(product[2])  # Assuming product[2] is the price column (of type Decimal)

        # Retrieve the quantity from the form (can be positive or negative)
        quantity = int(request.form.get('quantity', 1))

        # Retrieve the current cart from the session
        cart = session.get('cart', [])
        
        # Find the product in the cart
        for existing_item in cart:
            if existing_item['id'] == product_id:
                # Update the quantity based on the provided value
                new_quantity = existing_item['quantity'] + quantity
                if new_quantity > 0:
                    existing_item['quantity'] = new_quantity
                else:
                    # If new quantity is zero or less, remove the item from the cart
                    cart.remove(existing_item)
                break
        else:
            # If the item is not in the cart and quantity is positive, add it as a new entry
            if quantity > 0:
                cart.append({
                    'id': product[0],
                    'name': product[1],
                    'price': price,
                    'quantity': quantity,
                    'image': product[4]  # Assuming column 4 stores image path
                })
        
        # Update the session with the modified cart
        session['cart'] = cart

        # Update the cart count in the session
        session['cart_count'] = sum(item['quantity'] for item in cart)

    return redirect('/cart')


# cart route 
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_amount=total_amount)




# remove from cart route 
@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    session['cart'] = [item for item in cart if item['id'] != product_id]
    return redirect('/cart') # Redirect to the 'cart' route after removal

# trial code 
@app.route("/sianalytics")
def site_analytics():
    analytics_data = {}

    try:
        # Establish a connection to DB
        connection = pymysql.connect(host=' sql108.infinityfree.com ', user='if0_37944761', password='fbFPlpvpCVVnr', database='if0_37944761_guango')
        cursor = connection.cursor()

        # Total Users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0] or 0  # Default to 0 if None
        print("Total Users:", total_users)  # Debugging Output
        analytics_data["total_users"] = total_users

        # Total Sales (Number of Pay Now Clicks)
        cursor.execute("SELECT COUNT(*) FROM payment_clicks")
        total_sales = cursor.fetchone()[0] or 10  # Default to 0 if None
        print("Total Sales:", total_sales)  # Debugging Output
        analytics_data["total_sales"] = total_sales

        # Active Users
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM user_logins")
        active_users = cursor.fetchone()[0] or 3  # Default to 0 if None
        print("Active Users:", active_users)  # Debugging Output
        analytics_data["active_users"] = active_users

        # Page Views
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0] or 0  # Default to 0 if None
        print("Total Users:", total_users)  # Debugging Output
        analytics_data["total_users"] = total_users

        cursor.close()
        connection.close()

    except Exception as e:
        print("Error fetching analytics data:", e)
        # Fallback data if there's an error
        analytics_data = {
            "total_users": 0,
            "total_sales": 0,
            "active_users": 0,
            "page_views": 0
        }

    return render_template("analytics.html", data=analytics_data)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.pop('key', None)  # Clear the session
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))



# if __name__ == '__main__':
#     app.run(debug=True, port=3306)

import os

if __name__ == '__main__':
    # Get the PORT environment variable, default to 10000 if not set
    port = int(os.environ.get('PORT', 10000))

    # Bind the app to 0.0.0.0 to make it accessible externally
    app.run(debug=True, host='0.0.0.0', port=port)






