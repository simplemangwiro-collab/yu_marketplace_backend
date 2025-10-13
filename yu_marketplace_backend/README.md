# YU Marketplace

A simple Flask web app for managing student marketplace listings. Users can view, add, edit, and delete products. Built with Python, Flask, SQLite, and Bootstrap.

# Features

- View product listings
- Add new products
- Edit existing products
- Delete products
- Bootstrap-styled interface with navigation bar

# Tech Stack

- Python 3
- Flask
- SQLite
- Bootstrap 5
- HTML & CSS

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/yu-marketplace.git
   cd yu-marketplace
   ```

2. Create a virtual environment
   ```bash 
 python -m venv venv         
source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash 
    pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```python init_db.py
   ```

5. **Run the app**
   ```python app.py
   ```

6. **Visit in your browser**
   ```http://127.0.0.1:5000/items
   ```

## How It Works

1. Users visit the `/items` page to view all product listings.
2. They can click “Add Product” to submit a new item.
3. Each product has “Edit” and “Delete” buttons.
4. Data is stored in a local SQLite database.

## Screenshots

### 🏠 Homepage
![Homepage](screenshots/homepage.png)

### ➕ Add Product
![Add Product](screenshots/add_product.png)

### 📝 Edit Product
![Edit Product](screenshots/edit_product.png)

## Future Improvements

- Add user authentication and login system
- Enable image uploads for product listings
- Implement search and filter functionality
- Add pagination for large item lists
- Deploy the app to a cloud platform (e.g., Render or Heroku)

## License

This project is licensed under the MIT License.


