import os
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Take DB config ONLY from environment variables (no localhost fallback)
app.config['MYSQL_HOST'] = os.environ['MYSQL_HOST']
app.config['MYSQL_USER'] = os.environ['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = os.environ['MYSQL_DB']

mysql = MySQL(app)

def init_db():
    cur = mysql.connection.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        message TEXT
    );
    ''')
    mysql.connection.commit()
    cur.close()

# Run DB init only before first request (NOT at container startup)
@app.before_first_request
def initialize():
    init_db()

@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute('SELECT message FROM messages')
    messages = cur.fetchall()
    cur.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': new_message})

# optional health route for Kubernetes probes
@app.route('/healthz')
def health():
    return "ok", 200

if __name__ == '__main__':
    # DO NOT CALL init_db() HERE — it breaks Kubernetes
    app.run(host='0.0.0.0', port=5000, debug=True)


