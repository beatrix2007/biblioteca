from flask import Flask, request, redirect, render_template_string, session
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# =========================
# SUPABASE
# =========================
SUPABASE_URL = "https://ugviadmtvtkynvgztfmj.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# =========================
# AUTH
# =========================
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

def is_admin():
    return session.get("admin") is True


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session.clear()
            session["admin"] = True
            return redirect("/login")
        return "❌ Password errata"

    return render_template_string(LOGIN_HTML)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# HOME + FILTRI
# =========================
@app.route("/")
def home():

    url = SUPABASE_URL + "/rest/v1/libri?select=*"

    titolo = request.args.get("titolo", "")
    autore = request.args.get("autore", "")
    tipo = request.args.get("tipo", "")
    genere = request.args.get("genere", "")
    scaffale = request.args.get("scaffale", "")

    if titolo:
        url += f"&titolo=ilike.*{titolo}*"
    if autore:
        url += f"&autore=ilike.*{autore}*"
    if tipo:
        url += f"&tipo=eq.{tipo}"
    if genere:
        url += f"&genere=eq.{genere}"
    if scaffale:
        url += f"&scaffale=eq.{scaffale}"

    libri = requests.get(url, headers=headers).json()

    generi = requests.get(SUPABASE_URL + "/rest/v1/generi?select=*", headers=headers).json()
    scaffali = requests.get(SUPABASE_URL + "/rest/v1/scaffali?select=*", headers=headers).json()

    return render_template_string(HTML, libri=libri, generi=generi, scaffali=scaffali)


# =========================
# LIBRI
# =========================
@app.route("/aggiungi", methods=["POST"])
def aggiungi():

    if not is_admin():
        return "Non autorizzato", 403

    data = {
        "titolo": request.form["titolo"].upper(),
        "autore": request.form["autore"].upper(),
        "tipo": request.form["tipo"],
        "genere": request.form["genere"],
        "scaffale": request.form["scaffale"]
    }

    requests.post(SUPABASE_URL + "/rest/v1/libri", headers=headers, json=data)

    return redirect("/")


@app.route("/elimina/<int:id>")
def elimina(id):

    if not is_admin():
        return "Non autorizzato", 403

    requests.delete(
        SUPABASE_URL + f"/rest/v1/libri?id=eq.{id}",
        headers=headers
    )

    return redirect("/")


@app.route("/modifica/<int:id>", methods=["GET", "POST"])
def modifica(id):

    if not is_admin():
        return "Non autorizzato", 403

    if request.method == "POST":

        data = {
            "titolo": request.form["titolo"].upper(),
            "autore": request.form["autore"].upper(),
            "tipo": request.form["tipo"],
            "genere": request.form["genere"],
            "scaffale": request.form["scaffale"]
        }

        requests.patch(
            SUPABASE_URL + f"/rest/v1/libri?id=eq.{id}",
            headers=headers,
            json=data
        )

        return redirect("/")

    libro = requests.get(
        SUPABASE_URL + f"/rest/v1/libri?id=eq.{id}&select=*",
        headers=headers
    ).json()[0]

    return render_template_string(FORM_MODIFICA, libro=libro)


# =========================
# ADMIN GENERI
# =========================
@app.route("/admin/generi")
def admin_generi():

    if not is_admin():
        return "Non autorizzato", 403

    generi = requests.get(
        SUPABASE_URL + "/rest/v1/generi?select=*",
        headers=headers
    ).json()

    return render_template_string(GENERI_HTML, generi=generi)


@app.route("/admin/generi/aggiungi", methods=["POST"])
def add_genere():

    if not is_admin():
        return "Non autorizzato", 403

    requests.post(
        SUPABASE_URL + "/rest/v1/generi",
        headers=headers,
        json={"nome": request.form["nome"].lower()}
    )

    return redirect("/admin/generi")


@app.route("/admin/generi/modifica/<int:id>", methods=["POST"])
def edit_genere(id):

    if not is_admin():
        return "Non autorizzato", 403

    requests.patch(
        SUPABASE_URL + f"/rest/v1/generi?id=eq.{id}",
        headers=headers,
        json={"nome": request.form["nome"].lower()}
    )

    return redirect("/admin/generi")


@app.route("/admin/generi/elimina/<int:id>")
def delete_genere(id):

    if not is_admin():
        return "Non autorizzato", 403

    requests.delete(
        SUPABASE_URL + f"/rest/v1/generi?id=eq.{id}",
        headers=headers
    )

    return redirect("/admin/generi")


# =========================
# ADMIN SCAFFALI
# =========================
@app.route("/admin/scaffali")
def admin_scaffali():

    if not is_admin():
        return "Non autorizzato", 403

    scaffali = requests.get(
        SUPABASE_URL + "/rest/v1/scaffali?select=*",
        headers=headers
    ).json()

    return render_template_string(SCAFFALI_HTML, scaffali=scaffali)


@app.route("/admin/scaffali/aggiungi", methods=["POST"])
def add_scaffale():

    if not is_admin():
        return "Non autorizzato", 403

    requests.post(
        SUPABASE_URL + "/rest/v1/scaffali",
        headers=headers,
        json={"nome": request.form["nome"].upper()}
    )

    return redirect("/admin/scaffali")


@app.route("/admin/scaffali/modifica/<int:id>", methods=["POST"])
def edit_scaffale(id):

    if not is_admin():
        return "Non autorizzato", 403

    requests.patch(
        SUPABASE_URL + f"/rest/v1/scaffali?id=eq.{id}",
        headers=headers,
        json={"nome": request.form["nome"].upper()}
    )

    return redirect("/admin/scaffali")


@app.route("/admin/scaffali/elimina/<int:id>")
def delete_scaffale(id):

    if not is_admin():
        return "Non autorizzato", 403

    requests.delete(
        SUPABASE_URL + f"/rest/v1/scaffali?id=eq.{id}",
        headers=headers
    )

    return redirect("/admin/scaffali")

BASE_STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {
    font-family: Arial;
    background:#f4f6f8;
    margin:0;
}

.container {
    max-width:900px;
    margin:auto;
    padding:20px;
}

.card {
    background:white;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
    box-shadow:0 2px 6px rgba(0,0,0,0.05);
}

input, select {
    width:100%;
    padding:10px;
    margin:5px 0;
    border:1px solid #ddd;
    border-radius:8px;
}

button {
    padding:10px 14px;
    border:none;
    border-radius:8px;
    background:#2c3e50;
    color:white;
    cursor:pointer;
}

button:hover { opacity:0.9; }

a.btn {
    display:inline-block;
    padding:8px 12px;
    border-radius:8px;
    text-decoration:none;
    color:white;
}

.btn-blue { background:#3498db; }
.btn-red { background:#e74c3c; }
.btn-dark { background:#2c3e50; }

table {
    width:100%;
    border-collapse:collapse;
}

td, th {
    padding:10px;
    border-bottom:1px solid #ddd;
}

</style>

<div class="container">
"""
# =========================
# HTML
# =========================
HTML = BASE_STYLE + """
<meta name="viewport" content="width=device-width, initial-scale=1">

<div class="container">

<div class="header">
    <h2>📚 Biblioteca</h2>

    <div>
    {% if session.get("admin") %}
        🔐 Admin
        <a class="btn btn-red" href="/logout">Logout</a>
    {% else %}
        <a class="btn btn-dark" href="/login">Login</a>
    {% endif %}
    </div>
</div>

{% if session.get("admin") %}

<div class="card">
<h3>⚙️ Admin Panel</h3>
<a class="btn btn-dark" href="/admin/generi">📚 Generi</a>
<a class="btn btn-dark" href="/admin/scaffali">📦 Scaffali</a>
</div>

<div class="card">
<h3>➕ Aggiungi libro</h3>

<form method="POST" action="/aggiungi">

    <input name="titolo" placeholder="Titolo">
    <input name="autore" placeholder="Autore">

    <select name="tipo">
        <option value="libro">Libro</option>
        <option value="rivista">Rivista</option>
    </select>

    <select name="genere">
        {% for g in generi %}
        <option value="{{ g['nome'] }}">{{ g['nome'] }}</option>
        {% endfor %}
    </select>

    <select name="scaffale">
        {% for s in scaffali %}
        <option value="{{ s['nome'] }}">{{ s['nome'] }}</option>
        {% endfor %}
    </select>

    <button>➕ Aggiungi</button>
</form>
</div>

{% endif %}

<div class="card">
<h3>🔍 Libri</h3>

<div class="grid">

{% if libri|length == 0 %}

<div class="card">
    <h3>📭 Nessun libro</h3>
    <p>Inserisci il primo libro dalla sezione admin.</p>
</div>

{% else %}

{% for l in libri %}
<div class="card">

    <h3>{{ l['titolo'] }}</h3>
    <p>✍️ {{ l['autore'] }}</p>
    <p>📚 {{ l['tipo'] }} | {{ l['genere'] }} | {{ l['scaffale'] }}</p>

    {% if session.get("admin") %}
        <a class="btn btn-blue" href="/modifica/{{ l['id'] }}">✏️</a>
        <a class="btn btn-red" href="/elimina/{{ l['id'] }}">🗑</a>
    {% endif %}

</div>
{% endfor %}

{% endif %}

</div>
</div>

</div>
"""


FORM_MODIFICA = BASE_STYLE + """
<div class="card">
<h2>✏️ Modifica libro</h2>

<form method="POST">

<input name="titolo" value="{{ libro['titolo'] }}">
<input name="autore" value="{{ libro['autore'] }}">

<select name="tipo">
    <option value="libro">Libro</option>
    <option value="rivista">Rivista</option>
</select>

<input name="genere" value="{{ libro['genere'] }}">
<input name="scaffale" value="{{ libro['scaffale'] }}">

<button>Salva</button>

</form>

</div>
</div>
"""


GENERI_HTML = BASE_STYLE + """
<h2>Generi</h2>
<a href="/">Home</a>

<form method="POST" action="/admin/generi/aggiungi">
    <input name="nome">
    <button>Aggiungi</button>
</form>

<ul>
{% for g in generi %}
<li>
{{ g['nome'] }}
<form method="POST" action="/admin/generi/modifica/{{ g['id'] }}">
<input name="nome" value="{{ g['nome'] }}">
<button>✔</button>
</form>
<a href="/admin/generi/elimina/{{ g['id'] }}">🗑</a>
</li>
{% endfor %}
</ul>
"""


SCAFFALI_HTML = BASE_STYLE + """
<h2>Scaffali</h2>
<a href="/">Home</a>

<form method="POST" action="/admin/scaffali/aggiungi">
    <input name="nome">
    <button>Aggiungi</button>
</form>

<ul>
{% for s in scaffali %}
<li>
{{ s['nome'] }}
<form method="POST" action="/admin/scaffali/modifica/{{ s['id'] }}">
<input name="nome" value="{{ s['nome'] }}">
<button>✔</button>
</form>
<a href="/admin/scaffali/elimina/{{ s['id'] }}">🗑</a>
</li>
{% endfor %}
</ul>
"""

LOGIN_HTML = BASE_STYLE + """
    <h2>Login Admin</h2>
    <form method="POST">
        <input type="password" name="password">
        <button>Entra</button>
    </form>
    """


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)