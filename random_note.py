from flask import Flask, redirect, render_template, request
import psycopg2
from psycopg2 import sql
import threading

app = Flask(__name__)

# Replace these with your database connection details
DB_NAME = "changesets"
DB_USER = "www-data"
DB_PASSWORD = "secretpassword"
DB_HOST = "localhost"
DB_PORT = "5432"

# Connect to the database
connection = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

lock = threading.Lock()
@app.route('/<country_code>')
@app.route('/')
def random_note(country_code=None):
    with lock, connection, connection.cursor() as cursor:
        if country_code:
            # Use the note_country_queue table if country_code is provided
            select_query = """
                UPDATE note_country_queue
                SET seq_number = seq_number + 1, rand = random()
                WHERE (id, country_code) IN (
                    SELECT id, country_code
                    FROM note_country_queue
                    WHERE country_code = %s
                    ORDER BY seq_number, rand
                    FOR UPDATE
                    LIMIT 1
                )
                RETURNING id, lat, lon;
                """
            cursor.execute(select_query, (country_code,))
        else:
            select_query = """
                UPDATE note_queue
                SET seq_number = seq_number + 1, rand = random()
                WHERE id IN (
                    SELECT id
                    FROM note_queue
                    ORDER BY seq_number, rand
                    FOR UPDATE
                    LIMIT 1
                )
                RETURNING id, lat, lon;
                """
            cursor.execute(select_query)
        selected_id, lat, lon = cursor.fetchone() if cursor.rowcount else None
        connection.commit()

        if selected_id:
            
            zoom = request.args.get('z', type = int)
            if zoom and 1 <= zoom <= 20:
                hashUrl = f"#map={zoom}/{lat:.6f}/{lon:.6f}"
            else:
                hashUrl = ""

            return redirect(f"https://openstreetmap.org/note/{selected_id}{hashUrl}", code=302)
        
        else:
            return "No notes available"


@app.route('/list')    
@app.route('/list-new')
def country_list():
    with connection, connection.cursor() as cursor:
        cursor.execute("SELECT iso_code, name FROM countries ORDER BY name")
        countries = cursor.fetchall()
        return render_template('country_list.html', countries=countries)

if __name__ == '__main__':
    app.run(debug=True)
