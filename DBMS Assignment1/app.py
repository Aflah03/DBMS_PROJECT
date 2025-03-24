import mysql.connector
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="8547",
    database="bike_rental"
)
cursor = db.cursor()

# Home Route (Show Bikes)
@app.route('/')
def home():
    cursor.execute("SELECT * FROM bikes")
    bikes = cursor.fetchall()
    return render_template('index.html', bikes=bikes)

# NEWLY ADDED













@app.route('/remove_booking/<int:booking_id>')
def remove_booking(booking_id):
    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
    db.commit()
    return redirect('/admin')


@app.route('/cancel_booking/<int:booking_id>')
def cancel_booking(booking_id):
    if 'user_id' in session:
        cursor.execute("DELETE FROM bookings WHERE id = %s AND user_id = %s", (booking_id, session['user_id']))
        db.commit()
    return redirect('/bookings')













# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        db.commit()
        return redirect('/login')
    
    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            return redirect('/')
        return 'Invalid credentials'
    
    return render_template('login.html')


# Book a Bike
@app.route('/book/<int:bike_id>')
def book_bike(bike_id):
    if 'user_id' in session:
        cursor.execute("INSERT INTO bookings (user_id, bike_id, status) VALUES (%s, %s, 'pending')", (session['user_id'], bike_id))
        db.commit()
        return redirect('/bookings')
    
    return redirect('/login')


# User Booking Page
@app.route('/bookings')
def user_bookings():
    if 'user_id' in session:
        cursor.execute("SELECT b.model, bk.status FROM bookings bk JOIN bikes b ON bk.bike_id = b.id WHERE bk.user_id = %s", (session['user_id'],))
        bookings = cursor.fetchall()
        return render_template('bookings.html', bookings=bookings)
    
    return redirect('/login')

# Admin Page (Manage Pending Bookings)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        model = request.form['model']
        price = request.form['price']
        description = request.form['description']
        
        cursor.execute("INSERT INTO bikes (model, price, description) VALUES (%s, %s, %s)", (model, price, description))
        db.commit()
    
    # Fetch only pending bookings
    cursor.execute("""
    SELECT bk.id, u.name, b.model, bk.status 
    FROM bookings bk 
    JOIN users u ON bk.user_id = u.id 
    JOIN bikes b ON bk.bike_id = b.id 
    WHERE bk.status = 'pending'
""")

    bookings = cursor.fetchall()

    return render_template('admin.html', bookings=bookings)



# Approve a Booking
@app.route('/approve/<int:booking_id>')
def approve(booking_id):
    cursor.execute("UPDATE bookings SET status = %s WHERE id = %s", ("approved", booking_id))
    db.commit()
    return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=True)
