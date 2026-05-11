from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = "super-segreta-123"

def get_db():
    return sqlite3.connect("biblioteca.db")

# crea tabella se non esiste
with get_db() as db:
    db.execute("""
    CREATE TABLE IF NOT EXISTS libri (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titolo TEXT,
        autore TEXT,
        isbn TEXT
    )
    """)
import sqlite3

import os

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

from flask import session

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form["password"]

        if ADMIN_PASSWORD and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/")
        else:
            return "❌ Password errata"

    return """
    <h2>🔐 Login Admin</h2>
    <form method="POST">
        <input type="password" name="password">
        <button>Entra</button>
    </form>
    """
@app.route("/logout")
def logout():
    session["admin"] = False
    return redirect("/")

def is_admin():
    return session.get("admin", False)

HTML = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {
    font-family: Arial;
    margin: 20px;
}

/* layout base (PC) */
input, select, button {
    padding: 8px;
    margin: 5px;
    font-size: 14px;
}

li {
    font-size: 15px;
    line-height: 1.4;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-bottom: 10px;
}

/* pulsanti */
a {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 6px;
    text-decoration: none;
    color: white;
}

/* mobile */
@media (max-width: 768px) {

    body {
        margin: 10px;
    }

    input, select, button {
        width: 100%;
        font-size: 16px;
        margin: 5px 0;
    }

    li {
        font-size: 16px;
    }

    a {
        width: 100%;
        text-align: center;
        margin-top: 5px;
    }
}
</style>
<div style="margin-bottom:15px;">

{% if session.get("admin") %}

    <span>🔐 Admin attivo</span>
    <a href="/logout"
       style="margin-left:10px; padding:5px 10px; background:#e74c3c; color:white; text-decoration:none; border-radius:5px;">
        Logout
    </a>

{% else %}

    <a href="/login"
       style="padding:5px 10px; background:#2c3e50; color:white; text-decoration:none; border-radius:5px;">
        Login Admin
    </a>

{% endif %}

</div>
<h1>📚 Biblioteca</h1>

{% if session.get("admin") %}


<h2>➕ Aggiungi nuovo libro</h2>
<form method="POST" action="/aggiungi">
    <input name="titolo" placeholder="Titolo" required>
    <input name="autore" placeholder="Autore" required>
    <select name="tipo">
        <option value="-">Seleziona tipo</option>
        <option value="libro">Libro</option>
        <option value="rivista">Rivista</option>
    </select>
    <select name="genere" required>
        <option value="-">Tutti i generi</option>
        <option value="fantasy">Fantasy</option>
        <option value="fantascienza">Fantascienza</option>
        <option value="giallo">Giallo</option>
        <option value="thriller">Thriller</option>
        <option value="storico">Storico</option>
        <option value="biografia">Biografia</option>
        <option value="saggio">Saggio</option>
        <option value="altro">Altro</option>
    </select>
    <select name="scaffale" required>
        <option value="-">Tutti gli scaffali</option>

        <option value="A1">A1</option>
        <option value="A2">A2</option>
        <option value="A3">A3</option>

        <option value="B1">B1</option>
        <option value="B2">B2</option>
        <option value="B3">B3</option>

        <option value="C1">C1</option>
        <option value="C2">C2</option>

        <option value="altro">Altro</option>
    </select>
    <button type="submit">Aggiungi</button>
</form>
{% endif %}

<br>

<h3>🔍 Cerca e filtra</h3>

<form method="GET" action="/">

    <input name="titolo" placeholder="Titolo">

    <input name="autore" placeholder="Autore">

    <select name="tipo">
        <option value="">Tutti i tipi</option>
        <option value="libro">Libro</option>
        <option value="rivista">Rivista</option>
    </select>

    <select name="genere">
        <option value="">Tutti i generi</option>

        <option value="fantasy">Fantasy</option>
        <option value="fantascienza">Fantascienza</option>
        <option value="giallo">Giallo</option>
        <option value="thriller">Thriller</option>
        <option value="storico">Storico</option>
        <option value="biografia">Biografia</option>
        <option value="saggio">Saggio</option>
        <option value="altro">Altro</option>
    </select>
    <select name="scaffale">
        <option value="">Tutti gli scaffali</option>

        <option value="A1">A1</option>
        <option value="A2">A2</option>
        <option value="A3">A3</option>

        <option value="B1">B1</option>
        <option value="B2">B2</option>
        <option value="B3">B3</option>

        <option value="C1">C1</option>
        <option value="C2">C2</option>

        <option value="altro">Altro</option>
    </select>

    <button type="submit">Cerca</button>
</form>

<ul style="list-style:none; padding:0;">
{% for libro in libri %}
    <li style="padding:10px; margin-bottom:10px; border:1px solid #ddd; border-radius:8px;">

        <div style="font-size:18px; font-weight:bold;">
            📖 {{ libro[1] }}
        </div>

        <div style="font-size:14px; color:#555; margin-bottom:5px;">
            ✍️ {{ libro[2] }}
        </div>

        <div style="font-size:13px; color:#333;">
            📚 Tipo: {{ libro[3] }} |
            🏷️ Genere: {{ libro[4] }} |
            📦 Scaffale: {{ libro[5] }}
        </div>
{% if session.get("admin") %}

    <div style="margin-top:10px; display:flex; gap:8px;">
        <a href="/modifica/{{ libro[0] }}"
        style="padding:5px 10px; background:#3498db; color:white; text-decoration:none; border-radius:5px;">
            ✏️ Modifica
        </a>

        <a href="/elimina/{{ libro[0] }}"
        onclick="return confirm('Eliminare questo libro?');"
        style="padding:5px 10px; background:#e74c3c; color:white; text-decoration:none; border-radius:5px;">
            🗑️ Elimina
        </a>
    </div>

{% endif %}

    </li>
{% endfor %}
</ul>
"""

FORM_MODIFICA = """
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {
    font-family: Arial;
    background: #f4f4f4;
    padding: 20px;
}

.box {
    background: white;
    padding: 20px;
    max-width: 500px;
    margin: auto;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

input, select, button {
    width: 100%;
    padding: 10px;
    margin-top: 10px;
    font-size: 16px;
}

button {
    background: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
}

/* 📱 MOBILE */
@media (max-width: 600px) {
    body {
        padding: 10px;
    }

    .box {
        width: 100%;
    }
}
</style>

<div class="box">
<h2>✏️ Modifica libro</h2>

<form method="POST">

    <input name="titolo" value="{{ libro[1] }}" required>
    <input name="autore" value="{{ libro[2] }}">

    <select name="tipo">
        <option value="libro" {% if libro[3]=='libro' %}selected{% endif %}>Libro</option>
        <option value="rivista" {% if libro[3]=='rivista' %}selected{% endif %}>Rivista</option>
    </select>

    <select name="genere">
        <option value="fantasy" {% if libro[4]=='fantasy' %}selected{% endif %}>Fantasy</option>
        <option value="thriller" {% if libro[4]=='thriller' %}selected{% endif %}>Thriller</option>
        <option value="altro" {% if libro[4]=='altro' %}selected{% endif %}>Altro</option>
    </select>

    <select name="scaffale">
        <option value="A1" {% if libro[5]=='A1' %}selected{% endif %}>A1</option>
        <option value="A2" {% if libro[5]=='A2' %}selected{% endif %}>A2</option>
        <option value="altro" {% if libro[5]=='altro' %}selected{% endif %}>Altro</option>
    </select>

    <button>💾 Salva</button>

</form>
</div>
"""


@app.route("/")
def home():
    db = get_db()

    titolo = request.args.get("titolo", "").strip()
    autore = request.args.get("autore", "").strip()
    tipo = request.args.get("tipo", "").strip()
    genere = request.args.get("genere", "").strip()
    scaffale = request.args.get("scaffale", "").strip()

    query = "SELECT * FROM libri WHERE 1=1"
    params = []

    if titolo:
        query += " AND titolo LIKE ?"
        params.append(f"%{titolo}%")

    if autore:
        query += " AND autore LIKE ?"
        params.append(f"%{autore}%")

    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)

    if genere:
        query += " AND genere = ?"
        params.append(genere)

    if scaffale:
        query += " AND scaffale = ?"
        params.append(scaffale)

    libri = db.execute(query, params).fetchall()

    return render_template_string(HTML, libri=libri)

@app.route("/aggiungi", methods=["POST"])
def aggiungi():
    db = get_db()

    titolo = request.form["titolo"].strip()
    autore = request.form["autore"].strip()
    tipo = request.form["tipo"]
    genere = request.form["genere"]
    scaffale = request.form["scaffale"]

    # 🔍 controllo duplicato
    titolo = request.form["titolo"].strip().lower()
    autore = request.form["autore"].strip().lower()

    esiste = db.execute("""
        SELECT id FROM libri
        WHERE LOWER(TRIM(titolo)) = ? AND LOWER(TRIM(autore)) = ?
    """, (titolo, autore)).fetchone()

    if esiste:
        return "⚠️ Libro già presente nel catalogo!"

    # ➕ inserimento normale
    db.execute("""
        INSERT INTO libri (titolo, autore, tipo, genere, scaffale)
        VALUES (?, ?, ?, ?, ?)
    """, (titolo, autore, tipo, genere, scaffale))

    db.commit()
    return redirect("/")

    

@app.route("/elimina/<int:id>")
def elimina(id):
    if not is_admin():
        return "Non autorizzato", 403
    db = get_db()
    db.execute("DELETE FROM libri WHERE id = ?", (id,))
    db.commit()
    return redirect("/")

@app.route("/modifica/<int:id>", methods=["GET", "POST"])
def modifica(id):
    if not is_admin():
        return "Non autorizzato", 403
    db = get_db()

    if request.method == "POST":
        db.execute("""
            UPDATE libri
            SET titolo = ?, autore = ?, tipo = ?, genere = ?, scaffale = ?
            WHERE id = ?
        """, (
            request.form["titolo"],
            request.form["autore"],
            request.form["tipo"],
            request.form["genere"],
            request.form["scaffale"],
            id
        ))
        db.commit()
        return redirect("/")

    libro = db.execute("SELECT * FROM libri WHERE id = ?", (id,)).fetchone()

    return render_template_string(FORM_MODIFICA, libro=libro)


# 👇 QUESTA È LA PARTE IMPORTANTE
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)