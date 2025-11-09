from flask import Flask, render_template_string, request, redirect, session
import json, os, hashlib

app = Flask(__name__)
app.secret_key = "gizli_anahtar"
USER_FILE = "users.json"

# HTML ŞABLONLARI
login_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Cleaner Giriş</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; text-align: center; margin-top: 50px; padding: 20px; }
        input, button { padding: 10px; width: 80%; max-width: 300px; margin: 10px auto; display: block; }
        button { background-color: orange; border: none; color: white; font-weight: bold; }
    </style>
</head>
<body>
    <h2>Cleaner sistemine hoş geldiniz</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Kullanıcı adı" required>
        <input type="password" name="password" maxlength="5" placeholder="En fazla 5 haneli şifre" required>
        <button type="submit">Kaydol / Giriş Yap</button>
    </form>
    {% if message %}<p style="color:green;">{{ message }}</p>{% endif %}
</body>
</html>
"""

welcome_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Cleaner Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; text-align: center; margin-top: 50px; padding: 20px; }
        button, a { padding: 10px 20px; margin: 10px; text-decoration: none; font-weight: bold; }
        button { background-color: red; color: white; border: none; }
        a { background-color: green; color: white; display: inline-block; }
    </style>
</head>
<body>
    <h2>{{ message }}</h2>
    {% if admin %}
        <a href="/admin">Yönetici Paneline Git</a>
    {% endif %}
    <form method="POST" action="/logout">
        <button type="submit">Çıkış Yap</button>
    </form>
</body>
</html>
"""

admin_html = """
<!DOCTYPE html>
<html>
<head><title>Yönetici Paneli</title></head>
<body style="text-align:center;">
    <h2>Yönetici Paneli</h2>
    <table border="1" style="margin:auto;">
        <tr><th>Kullanıcı</th><th>CL</th><th>İşlem</th></tr>
        {% for user, data in users.items() %}
        <tr>
            <td>{{ user }}</td>
            <td>{{ data.cl }}</td>
            <td>
                <form method="POST" action="/delete/{{ user }}" style="display:inline;">
                    <button type="submit">Sil</button>
                </form>
                <form method="POST" action="/update_cl/{{ user }}" style="display:inline;">
                    <input type="number" name="amount" placeholder="+/- CL" style="width:60px;">
                    <button type="submit">Güncelle</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
    <br><a href="/welcome">Geri Dön</a>
</body>
</html>
"""

# YARDIMCI FONKSİYONLAR
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# GİRİŞ / KAYIT
@app.route("/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect("/welcome")

    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if len(password) > 5:
            message = "Şifre en fazla 5 haneli olmalı."
        else:
            password_hash = hash_password(password)
            users = load_users()

            # Yönetici özel kontrol
            if username == "Cleaner Personeli" and password == "571de":
                users[username] = {"password": password_hash, "cl": 999}
                save_users(users)
                session["username"] = username
                session["admin"] = True
                return redirect("/welcome")

            if username in users:
                if users[username]["password"] == password_hash:
                    session["username"] = username
                    session["admin"] = False
                    return redirect("/welcome")
                else:
                    message = "Şifre yanlış!"
            else:
                users[username] = {"password": password_hash, "cl": 50}
                save_users(users)
                session["username"] = username
                session["admin"] = False
                message = "Kayıt başarılı! Giriş yapıldı."

    return render_template_string(login_html, message=message)

# HOŞ GELDİN SAYFASI
@app.route("/welcome")
def welcome():
    if "username" not in session:
        return redirect("/")
    msg = "Hoş geldin yönetici!" if session.get("admin") else f"Hoş geldin {session['username']}!"
    return render_template_string(welcome_html, message=msg, admin=session.get("admin"))

# ÇIKIŞ
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")

# YÖNETİCİ PANELİ
@app.route("/admin")
def admin_panel():
    if not session.get("admin"):
        return redirect("/")
    users = load_users()
    return render_template_string(admin_html, users=users)

# KULLANICI SİLME
@app.route("/delete/<username>", methods=["POST"])
def delete_user(username):
    if not session.get("admin"):
        return redirect("/")
    users = load_users()
    if username in users:
        users.pop(username)
        save_users(users)
    return redirect("/admin")

# CL GÜNCELLEME
@app.route("/update_cl/<username>", methods=["POST"])
def update_cl(username):
    if not session.get("admin"):
        return redirect("/")
    amount = int(request.form.get("amount", 0))
    users = load_users()
    if username in users:
        users[username]["cl"] += amount
        save_users(users)
    return redirect("/admin")

# UYGULAMA BAŞLAT
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
