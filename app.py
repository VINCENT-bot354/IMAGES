# A simple Flask app that shows reviews (with rating) and allows users to add new ones
# Database: PostgreSQL
# Structure: Display reviews first, then the form at the bottom

from flask import Flask, render_template_string, request, redirect
import psycopg2
import os
import flask
print("🔥 Running Flask version:", flask.__version__)

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

# Create reviews table if it doesn't exist (run this once)
@app.before_first_request
def create_table():
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

# Home page: show all reviews and form at the bottom
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

# HTML template (inline)
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Customer Reviews</title>
    <style>
        body { font-family: Arial; padding: 20px; max-width: 600px; margin: auto; }
        .review { border-bottom: 1px solid #ccc; padding: 10px 0; }
        .stars { color: gold; }
        textarea, input, select { width: 100%; padding: 8px; margin: 5px 0; }
    </style>
</head>
<body>
    <h2>Customer Reviews</h2>
    {% for name, review, rating, created_at in reviews %}
        <div class="review">
            <strong>{{ name }}</strong> - <small>{{ created_at }}</small>
            <p>{{ review }}</p>
            <div class="stars">
                {% for i in range(rating) %}â˜…{% endfor %}
                {% for i in range(5 - rating) %}â˜†{% endfor %}
            </div>
        </div>
    {% endfor %}

    <h2>Leave a Review</h2>
    <form method="POST">
        <input type="text" name="name" placeholder="Your Name" required>
        <textarea name="review" placeholder="Write your review here..." required></textarea>
        <label for="rating">Rating:</label>
        <select name="rating" required>
            <option value="5">â˜…â˜…â˜…â˜…â˜…</option>
            <option value="4">â˜…â˜…â˜…â˜…â˜†</option>
            <option value="3">â˜…â˜…â˜…â˜†â˜†</option>
            <option value="2">â˜…â˜…â˜†â˜†â˜†</option>
            <option value="1">â˜…â˜†â˜†â˜†â˜†</option>
        </select>
        <button type="submit">Submit Review</button>
    </form>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
