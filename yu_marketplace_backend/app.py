from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to YU Marketplace!"

@app.route('/about')
def about():
    return "This is a student-built backend for YU Marketplace."

@app.route('/items')
def get_items():
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, product_name, price FROM products")
    items = cursor.fetchall()
    conn.close()

    return render_template("items.html", items=items)

from flask import request, redirect, render_template

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = sqlite3.connect("marketplace.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect('/items')


@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['product_name']
        price = request.form['price']

        conn = sqlite3.connect("marketplace.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (product_name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        conn.close()

        return redirect('/items')

    return render_template("add.html")

    # If GET request, show the form
    return '''
        <h2>Add a New Product</h2>
        <form method="post">
            Product Name: <input type="text" name="product_name"><br>
            Price: <input type="text" name="price"><br>
            <input type="submit" value="Add Product">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
