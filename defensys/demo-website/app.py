"""
Demo Vulnerable Web Application for DefenSys Testing
WARNING: This application contains intentional security vulnerabilities.
DO NOT deploy to production or expose to the internet!
"""

from flask import Flask, request, render_template_string, redirect, session, jsonify
import sqlite3
import os
import pickle
import subprocess

app = Flask(__name__)
app.secret_key = 'hardcoded-secret-key-12345'  # Vulnerability: Hardcoded secret

# Vulnerability: SQL Injection
DATABASE = 'demo.db'

def init_db():
    """Initialize database with sample data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            role TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            description TEXT
        )
    ''')
    
    # Insert sample data
    cursor.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'admin123', 'admin@demo.com', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (2, 'user', 'password', 'user@demo.com', 'user')")
    cursor.execute("INSERT OR IGNORE INTO products VALUES (1, 'Laptop', 999.99, 'High-performance laptop')")
    cursor.execute("INSERT OR IGNORE INTO products VALUES (2, 'Phone', 699.99, 'Latest smartphone')")
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Home page"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Demo Vulnerable Application</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: #f5f5f5;
            }
            .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 3px solid #ff6b6b; padding-bottom: 10px; }
            .warning { background: #fff3cd; border: 2px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .endpoint { background: #e9ecef; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .endpoint h3 { margin-top: 0; color: #007bff; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            ul { line-height: 1.8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔓 Demo Vulnerable Web Application</h1>
            
            <div class="warning">
                ⚠️ <strong>WARNING:</strong> This application contains intentional security vulnerabilities 
                for testing purposes. DO NOT use in production!
            </div>
            
            <h2>Available Endpoints:</h2>
            
            <div class="endpoint">
                <h3>🔐 Login (SQL Injection)</h3>
                <p><a href="/login">/login</a></p>
                <p>Try: username=' OR '1'='1' --</p>
            </div>
            
            <div class="endpoint">
                <h3>🔍 Search (XSS Vulnerability)</h3>
                <p><a href="/search">/search</a></p>
                <p>Try: &lt;script&gt;alert('XSS')&lt;/script&gt;</p>
            </div>
            
            <div class="endpoint">
                <h3>📊 Dashboard (IDOR)</h3>
                <p><a href="/dashboard?user_id=1">/dashboard?user_id=1</a></p>
                <p>Try changing user_id parameter</p>
            </div>
            
            <div class="endpoint">
                <h3>💾 Upload (Arbitrary File Upload)</h3>
                <p><a href="/upload">/upload</a></p>
                <p>No file type validation</p>
            </div>
            
            <div class="endpoint">
                <h3>⚙️ Admin Panel (Broken Access Control)</h3>
                <p><a href="/admin">/admin</a></p>
                <p>No authentication required</p>
            </div>
            
            <div class="endpoint">
                <h3>🖥️ Command Execution (RCE)</h3>
                <p><a href="/ping">/ping</a></p>
                <p>Try: 127.0.0.1; ls</p>
            </div>
            
            <div class="endpoint">
                <h3>📝 API (No Rate Limiting)</h3>
                <p><a href="/api/products">/api/products</a></p>
                <p>No rate limiting or authentication</p>
            </div>
            
            <h2>🎯 Testing Instructions:</h2>
            <ul>
                <li>Add this site as a target in DefenSys</li>
                <li>Run different scan types to detect vulnerabilities</li>
                <li>Check the scan results for findings</li>
                <li>Use <strong>http://localhost:5000</strong> as the target URL</li>
            </ul>
        </div>
    </body>
    </html>
    '''
    return html

# Vulnerability: SQL Injection
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Vulnerable SQL query - NO input validation
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # SQL Injection vulnerability
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/dashboard?user_id=' + str(user[0]))
        else:
            return render_template_string('''
                <h2>Login Failed</h2>
                <p>Invalid credentials</p>
                <a href="/login">Try again</a>
            ''')
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
        <style>
            body { font-family: Arial; max-width: 400px; margin: 100px auto; }
            input { width: 100%; padding: 10px; margin: 10px 0; }
            button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>Login</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p><small>Hint: Try SQL injection: ' OR '1'='1' --</small></p>
        <a href="/">← Back to Home</a>
    </body>
    </html>
    '''
    return html

# Vulnerability: XSS (Cross-Site Scripting)
@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    # Vulnerable: No output encoding
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Search</title>
        <style>
            body {{ font-family: Arial; max-width: 600px; margin: 50px auto; }}
            input {{ padding: 10px; width: 70%; }}
            button {{ padding: 10px 20px; background: #28a745; color: white; border: none; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h2>Search Products</h2>
        <form method="GET">
            <input type="text" name="q" placeholder="Search..." value="{query}">
            <button type="submit">Search</button>
        </form>
        <div style="margin-top: 20px;">
            <h3>Search Results for: {query}</h3>
            <p>No results found for "{query}"</p>
        </div>
        <p><small>Hint: Try XSS: &lt;script&gt;alert('XSS')&lt;/script&gt;</small></p>
        <a href="/">← Back to Home</a>
    </body>
    </html>
    '''
    return html

# Vulnerability: IDOR (Insecure Direct Object Reference)
@app.route('/dashboard')
def dashboard():
    user_id = request.args.get('user_id', '1')
    
    # Vulnerable: No authorization check
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id={user_id}")
    user = cursor.fetchone()
    conn.close()
    
    if user:
        html = f'''
        <!DOCTYPE html>
        <html>
        <head><title>Dashboard</title>
        <style>
            body {{ font-family: Arial; max-width: 600px; margin: 50px auto; }}
            .profile {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
        </style>
        </head>
        <body>
            <h2>User Dashboard</h2>
            <div class="profile">
                <p><strong>ID:</strong> {user[0]}</p>
                <p><strong>Username:</strong> {user[1]}</p>
                <p><strong>Email:</strong> {user[3]}</p>
                <p><strong>Role:</strong> {user[4]}</p>
            </div>
            <p><small>Hint: Try changing user_id in URL</small></p>
            <a href="/">← Back to Home</a>
        </body>
        </html>
        '''
        return html
    return "User not found"

# Vulnerability: Arbitrary File Upload
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            # Vulnerable: No file type validation
            filename = file.filename
            file.save(os.path.join('uploads', filename))
            return f"File {filename} uploaded successfully!"
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload File</title>
        <style>
            body { font-family: Arial; max-width: 500px; margin: 100px auto; }
            input { margin: 20px 0; }
            button { padding: 10px 20px; background: #17a2b8; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>Upload File</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Upload</button>
        </form>
        <p><small>Hint: No file type validation</small></p>
        <a href="/">← Back to Home</a>
    </body>
    </html>
    '''
    return html

# Vulnerability: Broken Access Control
@app.route('/admin')
def admin():
    # Vulnerable: No authentication check
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Panel</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; }
            .admin-panel { background: #dc3545; color: white; padding: 20px; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="admin-panel">
            <h2>🔐 Admin Panel</h2>
            <p>You shouldn't be able to access this without authentication!</p>
            <ul>
                <li>View all users</li>
                <li>Delete accounts</li>
                <li>Modify settings</li>
            </ul>
        </div>
        <p><small>Hint: This should require authentication</small></p>
        <a href="/">← Back to Home</a>
    </body>
    </html>
    '''
    return html

# Vulnerability: Command Injection
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    output = ''
    if request.method == 'POST':
        host = request.form.get('host', '')
        # Vulnerable: Command injection
        try:
            result = subprocess.check_output(f'ping -n 1 {host}', shell=True, stderr=subprocess.STDOUT)
            output = result.decode()
        except Exception as e:
            output = str(e)
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ping Utility</title>
        <style>
            body {{ font-family: Arial; max-width: 600px; margin: 50px auto; }}
            input {{ padding: 10px; width: 70%; }}
            button {{ padding: 10px 20px; background: #ffc107; border: none; cursor: pointer; }}
            pre {{ background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h2>Network Ping Tool</h2>
        <form method="POST">
            <input type="text" name="host" placeholder="Enter IP or hostname" required>
            <button type="submit">Ping</button>
        </form>
        <pre>{output}</pre>
        <p><small>Hint: Try command injection: 127.0.0.1 && dir</small></p>
        <a href="/">← Back to Home</a>
    </body>
    </html>
    '''
    return html

# Vulnerability: No Rate Limiting & Information Disclosure
@app.route('/api/products')
def api_products():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    
    # Vulnerable: Exposes sensitive information
    return jsonify({
        'products': products,
        'database_path': DATABASE,
        'secret_key': app.secret_key,
        'debug_mode': True
    })

# Vulnerability: Insecure Deserialization
@app.route('/deserialize', methods=['GET', 'POST'])
def deserialize():
    if request.method == 'POST':
        data = request.form.get('data', '')
        try:
            # Vulnerable: Unsafe deserialization
            obj = pickle.loads(bytes.fromhex(data))
            return f"Deserialized: {obj}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Deserialize Data</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; }
            textarea { width: 100%; height: 100px; padding: 10px; }
            button { padding: 10px 20px; background: #6c757d; color: white; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>Deserialize Object</h2>
        <form method="POST">
            <textarea name="data" placeholder="Enter hex-encoded pickle data"></textarea>
            <button type="submit">Deserialize</button>
        </form>
        <p><small>Hint: Insecure deserialization vulnerability</small></p>
        <a href="/">← Back to Home</a>
    </body>
    </html>
    '''
    return html

# Vulnerability: Sensitive Data Exposure
@app.route('/config')
def config():
    """Exposes configuration data"""
    return jsonify({
        'database': DATABASE,
        'secret_key': app.secret_key,
        'debug': True,
        'admin_password': 'admin123',
        'api_key': 'sk-1234567890abcdef',
        'aws_access_key': 'AKIAIOSFODNN7EXAMPLE'
    })

if __name__ == '__main__':
    # Create uploads directory
    os.makedirs('uploads', exist_ok=True)
    
    # Initialize database
    init_db()
    
    print("\n" + "="*60)
    print("🔓 DEMO VULNERABLE WEB APPLICATION")
    print("="*60)
    print("\n⚠️  WARNING: This application contains intentional vulnerabilities!")
    print("   DO NOT expose to the internet or use in production!\n")
    print("📍 Application running at: http://localhost:5000")
    print("🎯 Use this URL as a target in DefenSys\n")
    print("Vulnerabilities included:")
    print("  • SQL Injection")
    print("  • Cross-Site Scripting (XSS)")
    print("  • Insecure Direct Object Reference (IDOR)")
    print("  • Arbitrary File Upload")
    print("  • Broken Access Control")
    print("  • Command Injection")
    print("  • No Rate Limiting")
    print("  • Information Disclosure")
    print("  • Insecure Deserialization")
    print("  • Hardcoded Secrets")
    print("="*60 + "\n")
    
    # Run with debug mode (another vulnerability!)
    app.run(host='0.0.0.0', port=5000, debug=True)
