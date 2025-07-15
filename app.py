from flask import Flask, render_template_string, request, redirect
import psycopg2
import os

app = Flask(__name__)

# Connect to the database using environment variables (must be set in Render)
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# Create reviews table once
@app.before_request
def create_table_once():
    if not hasattr(app, 'db_initialized'):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                review TEXT NOT NULL,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()
        app.db_initialized = True

# Homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        review = request.form['review']
        rating = int(request.form['rating'])

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO reviews (name, review, rating) VALUES (%s, %s, %s)",
                    (name, review, rating))
        conn.commit()
        conn.close()
        return redirect('/')

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, review, rating, created_at FROM reviews ORDER BY id DESC")
    reviews = cur.fetchall()
    conn.close()

    return render_template_string(TEMPLATE, reviews=reviews)

# Improved HTML template
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Customer Reviews</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: #f4f4f4;
        }
        .container {
            max-width: 800px;
            margin: 50px auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        h2 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .review {
            border-bottom: 1px solid #ddd;
            padding: 15px 0;
        }
        .review strong {
            color: #222;
            font-size: 1.1em;
        }
        .review small {
            color: #666;
        }
        .stars {
            color: #f4b400;
            font-size: 1.2em;
            margin-top: 5px;
        }
        form {
            margin-top: 40px;
        }
        input[type="text"], textarea, select {
            width: 100%;
            padding: 12px 15px;
            margin-top: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 1em;
            box-sizing: border-box;
        }
        textarea {
            height: 120px;
            resize: vertical;
        }
        button {
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 20px;
            margin-top: 15px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        button:hover {
            background: #218838;
        }
        label {
            font-weight: bold;
            display: block;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Customer Reviews</h2>
        {% for name, review, rating, created_at in reviews %}
            <div class="review">
                <strong>{{ name }}</strong> - <small>{{ created_at }}</small>
                <p>{{ review }}</p>
                <div class="stars">
                    {% for i in range(rating) %}★{% endfor %}
                    {% for i in range(5 - rating) %}☆{% endfor %}
                </div>
            </div>
        {% endfor %}

        <h2>Leave a Review</h2>
        <form method="POST">
            <label for="name">Your Name</label>
            <input type="text" name="name" placeholder="e.g. John Doe" required>

            <label for="review">Your Review</label>
            <textarea name="review" placeholder="Share your thoughts..." required></textarea>

            <label for="rating">Rating</label>
            <select name="rating" required>
                <option value="5">★★★★★ - Excellent</option>
                <option value="4">★★★★☆ - Very Good</option>
                <option value="3">★★★☆☆ - Average</option>
                <option value="2">★★☆☆☆ - Poor</option>
                <option value="1">★☆☆☆☆ - Terrible</option>
            </select>

            <button type="submit">Submit Review</button>
        </form>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
