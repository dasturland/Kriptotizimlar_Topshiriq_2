from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
import ssl
from utils.crypto import generate_rsa_keys, sign_message, verify_signature, hmac_sha256, split_secret_shares, recover_secret_from_shares
from utils.audit import log_event
from utils.db import init_db, get_db_connection
from functools import wraps
from datetime import timedelta
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=2)

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

init_db(DB_PATH)

HARDCODED_ADMIN = {
    'username': 'Admin',
    'password': 'Parol2005'
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Iltimos, tizimga kiring.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') not in roles:
                flash('Sizda bu amaliyotni bajarish huquqi yo\'q.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'xodim')

        errors = []
        if len(password) < 8:
            errors.append('Kamida 8 ta belgi kerak')
        if not any(c.islower() for c in password):
            errors.append('Kichik harf bo\'lishi kerak')
        if not any(c.isupper() for c in password):
            errors.append('Katta harf bo\'lishi kerak')
        if not any(c.isdigit() for c in password):
            errors.append('Raqam bo\'lishi kerak')
        if not any(c in '!@#$%^&*()_+-=[]{};:\\|,.<>/?' for c in password):
            errors.append('Maxsus belgi bo\'lishi kerak')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)

        conn = get_db_connection(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', (username, password_hash, role))
            conn.commit()
            flash('Ro\'yxatdan muvaffaqiyatli o\'tdingiz', 'success')
            log_event(DB_PATH, username, 'register')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Bunday foydalanuvchi mavjud', 'danger')
            return redirect(url_for('register'))
        finally:
            conn.close()

    conn = get_db_connection(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT username FROM users WHERE role = ?', ('boshliq',))
    boshliq_exists = cur.fetchone()
    conn.close()
    
    return render_template('register.html', boshliq_exists=boshliq_exists)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == HARDCODED_ADMIN['username'] and password == HARDCODED_ADMIN['password']:
            session.permanent = True
            session['user_id'] = 0
            session['username'] = HARDCODED_ADMIN['username']
            session['role'] = 'admin'
            flash('Tizimga muvaffaqiyatli kirdingiz', 'success')
            log_event(DB_PATH, username, 'login')
            return redirect(url_for('admin_panel'))

        conn = get_db_connection(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT id, password_hash, role FROM users WHERE username = ?', (username,))
        row = cur.fetchone()
        conn.close()
        
        if row and check_password_hash(row[1], password):
            session.permanent = True
            session['user_id'] = row[0]
            session['username'] = username
            session['role'] = row[2]
            flash('Tizimga muvaffaqiyatli kirdingiz', 'success')
            log_event(DB_PATH, username, 'login')
            return redirect(url_for('index'))
        else:
            flash('Login yoki parol xato', 'danger')
            log_event(DB_PATH, username, 'failed_login')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    username = session.get('username')
    session.clear()
    flash('Tizimdan chiqdingiz', 'info')
    log_event(DB_PATH, username, 'logout')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
@role_required('admin')
def admin_panel():
    conn = get_db_connection(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, username, role FROM users')
    users = cur.fetchall()
    conn.close()
    return render_template('admin.html', users=users)

@app.route('/delete_user/<int:user_id>')
@login_required
@role_required('admin')
def delete_user(user_id):
    conn = get_db_connection(DB_PATH)
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash('Foydalanuvchi o\'chirildi', 'info')
    log_event(DB_PATH, session.get('username'), f'delete_user:{user_id}')
    return redirect(url_for('admin_panel'))

@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    conn = get_db_connection(DB_PATH)
    cur = conn.cursor()
    
    if request.method == 'POST':
        recipient = request.form['recipient']
        body = request.form['body']
        key = os.environ.get('HMAC_KEY', 'secret_hmac_key').encode()
        mac = hmac_sha256(key, body.encode())
        cur.execute('INSERT INTO messages (sender, recipient, body, hmac) VALUES (?, ?, ?, ?)', 
                   (session.get('username'), recipient, body, mac))
        conn.commit()
        flash('Xabar yuborildi', 'success')
        log_event(DB_PATH, session.get('username'), f'send_message to {recipient}')
    
    user_role = session.get('role')
    if user_role == 'admin':
        cur.execute('SELECT id, sender, recipient, body, hmac, signature, timestamp FROM messages ORDER BY timestamp DESC')
    else:
        cur.execute('SELECT id, sender, recipient, body, hmac, signature, timestamp FROM messages WHERE recipient = ? OR sender = ? ORDER BY timestamp DESC', 
                   (session.get('username'), session.get('username')))
    
    msgs = cur.fetchall()
    conn.close()
    return render_template('messages.html', messages=msgs)

@app.route('/check_hmac/<int:msg_id>')
@login_required
def check_hmac(msg_id):
    conn = get_db_connection(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT body, hmac, sender FROM messages WHERE id = ?', (msg_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        flash('Xabar topilmadi', 'danger')
        return redirect(url_for('messages'))
    
    body, stored_hmac, sender = row
    key = os.environ.get('HMAC_KEY', 'secret_hmac_key').encode()
    mac = hmac_sha256(key, body.encode())
    
    if mac == stored_hmac:
        flash('Xabar yaxlitligi buzilmagan', 'success')
        log_event(DB_PATH, session.get('username'), f'hmac_ok message:{msg_id}')
    else:
        flash('Xabar yaxlitligi buzilgan', 'danger')
        log_event(DB_PATH, session.get('username'), f'hmac_fail message:{msg_id}')
    return redirect(url_for('messages'))

@app.route('/generate_keys')
@login_required
@role_required('admin', 'boshliq')
def generate_keys_route():
    private, public = generate_rsa_keys()
    with open('private.pem', 'wb') as f:
        f.write(private)
    with open('public.pem', 'wb') as f:
        f.write(public)
    flash('Kalitlar yaratildi', 'success')
    log_event(DB_PATH, session.get('username'), 'generate_keys')
    return redirect(url_for('messages'))

@app.route('/sign_message/<int:msg_id>')
@login_required
@role_required('admin', 'boshliq')
def sign_message_route(msg_id):
    if not os.path.exists('private.pem'):
        flash('Iltimos avval kalitlar yaratilsin', 'warning')
        return redirect(url_for('messages'))
    
    conn = get_db_connection(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT body FROM messages WHERE id = ?', (msg_id,))
    row = cur.fetchone()
    
    if not row:
        flash('Xabar topilmadi', 'danger')
        return redirect(url_for('messages'))
    
    body = row[0]
    with open('private.pem', 'rb') as f:
        private = f.read()
    
    signature = sign_message(private, body.encode())
    cur.execute('UPDATE messages SET signature = ? WHERE id = ?', (signature, msg_id))
    conn.commit()
    conn.close()
    
    flash('Xabar imzolandi', 'success')
    log_event(DB_PATH, session.get('username'), f'sign_message:{msg_id}')
    return redirect(url_for('messages'))

@app.route('/verify_signature/<int:msg_id>')
@login_required
def verify_signature_route(msg_id):
    conn = get_db_connection(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT body, signature FROM messages WHERE id = ?', (msg_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        flash('Xabar topilmadi', 'danger')
        return redirect(url_for('messages'))
    
    body, signature = row
    if not signature:
        flash('Xabar imzolanmagan', 'warning')
        return redirect(url_for('messages'))
    
    if not os.path.exists('public.pem'):
        flash('Jamoa public kaliti mavjud emas', 'danger')
        return redirect(url_for('messages'))
    
    with open('public.pem', 'rb') as f:
        public = f.read()
    
    ok = verify_signature(public, body.encode(), signature)
    if ok:
        flash('Imzo tekshirildi', 'success')
        log_event(DB_PATH, session.get('username'), f'verify_sig_ok message:{msg_id}')
    else:
        flash('Imzo noto\'g\'ri', 'danger')
        log_event(DB_PATH, session.get('username'), f'verify_sig_fail message:{msg_id}')
    return redirect(url_for('messages'))

@app.route('/secret_sharing', methods=['GET', 'POST'])
@login_required
def secret_sharing_view():
    recovered = None
    shares_list = []
    secrets_list = []
    
    conn = get_db_connection(DB_PATH)
    cur = conn.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'split' and session.get('role') in ['admin', 'boshliq']:
            secret_text = request.form.get('secret', '').strip()
            description = request.form.get('description', 'Sir').strip()
            
            if not secret_text:
                flash('Sir kiritilmadi', 'danger')
                return redirect(url_for('secret_sharing_view'))
            
            secret = secret_text.encode()
            shares = split_secret_shares(secret)
            secret_id = str(uuid.uuid4())
            
            cur.execute('INSERT INTO secrets (secret_id, owner, description) VALUES (?, ?, ?)',
                       (secret_id, session.get('username'), description))
            
            cur.execute('SELECT username FROM users WHERE role = ?', ('xodim',))
            xodimlar = [row[0] for row in cur.fetchall()]
            
            if len(xodimlar) < 3:
                flash('Kamida 3 ta xodim kerak. Hozir faqat {} ta'.format(len(xodimlar)), 'warning')
            
            for i, share in enumerate(shares):
                if i < len(xodimlar):
                    recipient = xodimlar[i]
                else:
                    recipient = 'xodim_{}'.format(i+1)
                share_hex = share.hex()
                cur.execute('INSERT INTO secret_shares (secret_id, recipient, share_data) VALUES (?, ?, ?)',
                           (secret_id, recipient, share_hex))
            
            conn.commit()
            flash('Sir 3 ta ulushga bo\'lindi va xodimlarga yuborildi', 'success')
            log_event(DB_PATH, session.get('username'), 'secret_split:{}'.format(secret_id))
        
        elif action == 'recover' and session.get('role') == 'xaker':
            shares_hex = request.form.getlist('share')
            shares = []
            for s in shares_hex:
                if s and s.strip():
                    try:
                        shares.append(bytes.fromhex(s.strip()))
                    except:
                        pass
            
            if len(shares) < 2:
                recovered = 'Kamida 2 ta ulush tanlang. Hozir {} ta tanlangan.'.format(len(shares))
                log_event(DB_PATH, session.get('username'), 'secret_recover_fail_not_enough_shares')
            else:
                try:
                    recovered_bytes = recover_secret_from_shares(shares)
                    recovered = recovered_bytes.decode('utf-8', errors='ignore')
                    flash('Sir muvaffaqiyatli tiklandi!', 'success')
                    log_event(DB_PATH, session.get('username'), 'secret_recover_success')
                except Exception as e:
                    recovered = 'Qayta tiklashda xatolik: {}'.format(str(e))
                    flash(recovered, 'danger')
                    log_event(DB_PATH, session.get('username'), 'secret_recover_fail')
    
    user_role = session.get('role')
    
    if user_role in ['admin', 'boshliq']:
        cur.execute('SELECT secret_id, description, created_at FROM secrets WHERE owner = ? ORDER BY created_at DESC',
                   (session.get('username'),))
        secrets_list = cur.fetchall()
        
        cur.execute('SELECT ss.id, ss.recipient, ss.share_data, ss.timestamp FROM secret_shares ss INNER JOIN secrets s ON ss.secret_id = s.secret_id WHERE s.owner = ? ORDER BY ss.timestamp DESC',
                   (session.get('username'),))
        shares_list = cur.fetchall()
    
    elif user_role == 'xodim':
        cur.execute('SELECT id, share_data, timestamp FROM secret_shares WHERE recipient = ? ORDER BY timestamp DESC',
                   (session.get('username'),))
        shares_list = cur.fetchall()
    
    elif user_role == 'xaker':
        cur.execute('SELECT id, recipient, share_data FROM secret_shares ORDER BY timestamp DESC')
        shares_list = cur.fetchall()
    
    conn.close()
    
    return render_template('secret_sharing.html', recovered=recovered, shares_list=shares_list, secrets_list=secrets_list)

@app.route('/audit')
@login_required
@role_required('admin')
def audit_view():
    conn = get_db_connection(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, username, event, timestamp FROM audit ORDER BY timestamp DESC')
    rows = cur.fetchall()
    conn.close()
    return render_template('audit.html', logs=rows)

if __name__ == '__main__':
    ssl_context = None
    project_root = os.path.abspath(os.path.dirname(__file__))
    server_cert = os.path.join(project_root, 'server.crt')
    server_key = os.path.join(project_root, 'server.key')
    ca_cert = os.path.join(project_root, 'MyRootCA.crt')

    if os.path.exists(server_cert) and os.path.exists(server_key):
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:!aNULL:!MD5:!DSS')
            context.load_cert_chain(certfile=server_cert, keyfile=server_key)

            if os.path.exists(ca_cert):
                context.load_verify_locations(cafile=ca_cert)
                context.verify_mode = ssl.CERT_REQUIRED
                print('Mutual TLS enabled: client certificates required (using MyRootCA.crt)')
            else:
                print('Server certificate found but CA (MyRootCA.crt) not found — client certs will not be required')

            ssl_context = context
        except Exception as e:
            print(f"Failed to configure SSL context: {e}")
            ssl_context = None

    try:
        port = int(os.environ.get('PORT', '5000'))
    except Exception:
        port = 5000

    if ssl_context:
        app.run(host='0.0.0.0', port=port, ssl_context=ssl_context, debug=False)
    else:
        print('Running without TLS (no server cert/key configured).')
        app.run(host='0.0.0.0', port=port, debug=False)
