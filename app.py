from flask import Flask, render_template_string, request, redirect
import psycopg2
import os

app = Flask(__name__)

# Connect to PostgreSQL using environment variables
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

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
    cur.execute("SELECT name, review, rating FROM reviews ORDER BY id DESC")
    reviews = cur.fetchall()

    cur.execute("SELECT AVG(rating) FROM reviews")
    avg_rating = cur.fetchone()[0]
    avg_rating = round(avg_rating, 1) if avg_rating else 0

    conn.close()

    return render_template_string(TEMPLATE, reviews=reviews, avg_rating=avg_rating)


TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Customer Reviews</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', sans-serif;
            background: url('/static/The-Great-Wildebeest-Migration-750x450.jpg') no-repeat center center fixed;
            background-size: cover;
        }
        .container {
            max-width: 850px;
            margin: 60px auto;
            padding: 40px;
            border-radius: 14px;
            border: 2px solid #ffffffcc; /* semi-white outline */
            background: transparent; /* completely see-through */
            color: #ffffff;
        }
        h2, h3 {
            text-align: center;
            color: #ffffff;
        }
        .avg-rating {
            text-align: center;
            font-size: 1.5em;
            color: #00ff99; /* green */
            margin-bottom: 30px;
        }
        .review {
            border-bottom: 1px solid #ffffff33;
            padding: 20px 0;
            color: #fff;
        }
        .review strong {
            font-size: 1.2em;
            color: #ffffff;
        }
        .stars {
            color: gold;
            font-size: 1.3em;
            margin-top: 8px;
        }
        form {
            margin-top: 50px;
        }
        input[type="text"], textarea, select {
            width: 100%;
            padding: 15px 18px;
            margin-top: 12px;
            font-size: 1.1em;
            border-radius: 10px;
            border: 1px solid #ffffff99;
            background: transparent;
            color: white;
        }
        input::placeholder, textarea::placeholder {
            color: #dddddd;
        }
        label {
            display: block;
            margin-top: 20px;
            font-weight: bold;
            color: #ffffff;
        }
        button {
            background: #000000cc;
            color: white;
            border: 1px solid #ffffff99;
            padding: 16px 30px;
            margin-top: 25px;
            font-size: 1.2em;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            transition: 0.3s;
        }
        button:hover {
            background: #28a745; /* green */
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Customer Reviews</h2>
        <div class="avg-rating">★ {{ avg_rating }} / 5 overall</div>

        {% for name, review, rating in reviews %}
            <div class="review">
                <strong>{{ name }}</strong>
                <p>{{ review }}</p>
                <div class="stars">
                    {% for i in range(rating) %}★{% endfor %}
                    {% for i in range(5 - rating) %}☆{% endfor %}
                </div>
            </div>
        {% endfor %}

        <h3>Leave a Review</h3>
        <form method="POST">
            <label for="name">Your Name</label>
            <input type="text" name="name" placeholder="e.g. Jane Doe" required>

            <label for="review">Your Review</label>
            <textarea name="review" placeholder="Write your feedback here..." required></textarea>

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
        
