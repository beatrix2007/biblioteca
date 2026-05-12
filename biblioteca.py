from flask import Flask, request, redirect, render_template_string, session
import os
import requests

app = Flask(__name__)
app.secret_key = "super-segreta-123"

# =========================
# SUPABASE CONFIG
# =========================
SUPABASE_URL = "https://ugviadmtvtkynvgztfmj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVndmlhZG10dnRreW52Z3p0Zm1qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg1MzA2NzMsImV4cCI6MjA5NDEwNjY3M30.M3zG5wfdIlAvZhbvkAK1zarpezJf8d1HpgPhxQeV_cQ"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# =========================
# LOGIN ADMIN
# =========================
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

def is_admin():
    return session.get("admin", False)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/")
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
    session.clear()
    return redirect("/")


# =========================
# HOME + FILTRI
# =========================
@app.route("/")
def home():

    params = []

    query = SUPABASE_URL + "/rest/v1/libri?select=*"

    titolo = request.args.get("titolo", "")
    autore = request.args.get("autore", "")
    tipo = request.args.get("tipo", "")
    genere = request.args.get("genere", "")
    scaffale = request.args.get("scaffale", "")

    if titolo:
        query += f"&titolo=ilike.*{titolo}*"
    if autore:
        query += f"&autore=ilike.*{autore}*"
    if tipo:
        query += f"&tipo=eq.{tipo}"
    if genere:
        query += f"&genere=eq.{genere}"
    if scaffale:
        query += f"&scaffale=eq.{scaffale}"

    r = requests.get(query, headers=headers)
    libri = r.json()

    # generi/scaffali
    g = requests.get(SUPABASE_URL + "/rest/v1/generi?select=*", headers=headers).json()
    s = requests.get(SUPABASE_URL + "/rest/v1/scaffali?select=*", headers=headers).json()

    return render_template_string(HTML, libri=libri, generi=g, scaffali=s)


# =========================
# AGGIUNGI
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

    requests.post(
        SUPABASE_URL + "/rest/v1/libri",
        headers=headers,
        json=data
    )

    return redirect("/")


# =========================
# ELIMINA
# =========================
@app.route("/elimina/<int:id>")
def elimina(id):

    if not is_admin():
        return "Non autorizzato", 403

    requests.delete(
        SUPABASE_URL + f"/rest/v1/libri?id=eq.{id}",
        headers=headers
    )

    return redirect("/")

@app.route("/admin/generi", methods=["POST"])
def add_genere():

    if not is_admin():
        return "Non autorizzato", 403

    nome = request.form["nome"].strip().lower()

    requests.post(
        SUPABASE_URL + "/rest/v1/generi",
        headers=headers,
        json={"nome": nome}
    )

    return redirect("/")


@app.route("/admin/scaffali", methods=["POST"])
def add_scaffale():

    if not is_admin():
        return "Non autorizzato", 403

    nome = request.form["nome"].strip().upper()

    requests.post(
        SUPABASE_URL + "/rest/v1/scaffali",
        headers=headers,
        json={"nome": nome}
    )

    return redirect("/")

@app.route("/admin/generi/elimina/<int:id>")
def elimina_genere(id):

    if not is_admin():
        return "Non autorizzato", 403

    requests.delete(
        SUPABASE_URL + f"/rest/v1/generi?id=eq.{id}",
        headers=headers
    )

    return redirect("/")


@app.route("/admin/scaffali/elimina/<int:id>")
def elimina_scaffale(id):

    if not is_admin():
        return "Non autorizzato", 403

    requests.delete(
        SUPABASE_URL + f"/rest/v1/scaffali?id=eq.{id}",
        headers=headers
    )

    return redirect("/")

# =========================
# MODIFICA
# =========================
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

    r = requests.get(
        SUPABASE_URL + f"/rest/v1/libri?id=eq.{id}&select=*",
        headers=headers
    )

    libro = r.json()[0]

    return render_template_string(FORM_MODIFICA, libro=libro)


# =========================
# HTML PRINCIPALE
# =========================
HTML = """
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body { font-family: Arial; margin: 20px; }
input, select, button { padding: 8px; margin: 5px; font-size: 14px; }

li {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-bottom: 10px;
}

a {
    display:inline-block;
    padding:6px 10px;
    border-radius:6px;
    text-decoration:none;
    color:white;
}
@media (max-width: 768px) {
    div[style*="display:flex"] {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
}
</style>
<div style="
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:12px;
    border-bottom:1px solid #ddd;
    margin-bottom:20px;
">

    <h2 style="margin:0;">📚 Biblioteca</h2>

    <div>

        {% if session.get("admin") %}
            <span style="margin-right:10px;">🔐 Admin attivo</span>
            <a href="/logout"
               style="padding:6px 12px; background:#e74c3c; color:white; border-radius:6px; text-decoration:none;">
                Logout
            </a>
        {% else %}
            <a href="/login"
               style="padding:6px 12px; background:#2c3e50; color:white; border-radius:6px; text-decoration:none;">
                Login Admin
            </a>
        {% endif %}

    </div>

</div>

{% if session.get("admin") %}

<hr>

<h2>⚙️ Gestione categorie</h2>

<div style="display:flex; gap:20px; flex-wrap:wrap;">

    <form method="POST" action="/admin/generi">
        <h4>📚 Aggiungi genere</h4>
        <input name="nome" placeholder="es. fantasy" required>
        <button>Aggiungi</button>
    </form>

    <ul>
    {% for g in generi %}
        <li>
            {{ g['nome'] }}
            <a href="/admin/generi/elimina/{{ g['id'] }}"
            onclick="return confirm('Eliminare genere?');"
            style="color:red; margin-left:10px;">
                🗑
            </a>
        </li>
    {% endfor %}
    </ul>

    <form method="POST" action="/admin/scaffali">
        <h4>📦 Aggiungi scaffale</h4>
        <input name="nome" placeholder="es. A1" required>
        <button>Aggiungi</button>
    </form>

    <ul>
    {% for s in scaffali %}
        <li>
            {{ s['nome'] }}
            <a href="/admin/scaffali/elimina/{{ s['id'] }}"
            onclick="return confirm('Eliminare scaffale?');"
            style="color:red; margin-left:10px;">
                🗑
            </a>
        </li>
    {% endfor %}
    </ul>

</div>

{% endif %}

{% if session.get("admin") is true %}
<h2>➕ Aggiungi libro</h2>
<form method="POST" action="/aggiungi">

    <input name="titolo" placeholder="Titolo" required>
    <input name="autore" placeholder="Autore" required>

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

    <button>Aggiungi</button>
</form>
{% endif %}

<hr>

<h3>🔍 Filtri</h3>

<form method="GET">

    <input name="titolo" placeholder="Titolo">
    <input name="autore" placeholder="Autore">

    <select name="tipo">
        <option value="">Tutti i tipi</option>
        <option value="libro">Libro</option>
        <option value="rivista">Rivista</option>
    </select>

    <select name="genere">
        <option value="">Tutti i generi</option>
        {% for g in generi %}
            <option value="{{ g['nome'] }}">{{ g['nome'] }}</option>
        {% endfor %}
    </select>

    <select name="scaffale">
        <option value="">Tutti gli scaffali</option>
        {% for s in scaffali %}
            <option value="{{ s['nome'] }}">{{ s['nome'] }}</option>
        {% endfor %}
    </select>

    <button>Cerca</button>
</form>

<hr>

<h3>📖 Libri</h3>

{% if libri|length == 0 %}
    <p>📭 Nessun libro presente</p>
{% else %}

<ul style="list-style:none; padding:0;">
{% for libro in libri %}
    <li>

        <b>{{ libro['titolo'] }}</b><br>
        ✍️ {{ libro['autore'] }}<br>
        📚 {{ libro['tipo'] }} | {{ libro['genere'] }} | {{ libro['scaffale'] }}

        {% if session.get("admin") %}
        <div style="margin-top:10px;">
            <a href="/modifica/{{ libro['id'] }}" style="background:#3498db;">✏️ Modifica</a>
            <a href="/elimina/{{ libro['id'] }}" style="background:#e74c3c;"
               onclick="return confirm('Eliminare?');">🗑️ Elimina</a>
        </div>
        {% endif %}

    </li>
{% endfor %}
</ul>

{% endif %}
"""


# =========================
# FORM MODIFICA
# =========================
FORM_MODIFICA = """
<h2>✏️ Modifica libro</h2>

<form method="POST">

    <input name="titolo" value="{{ libro['titolo'] }}">
    <input name="autore" value="{{ libro['autore'] }}">

    <select name="tipo">
        <option value="libro" {% if libro['tipo']=='libro' %}selected{% endif %}>Libro</option>
        <option value="rivista" {% if libro['tipo']=='rivista' %}selected{% endif %}>Rivista</option>
    </select>

    <input name="genere" value="{{ libro['genere'] }}">
    <input name="scaffale" value="{{ libro['scaffale'] }}">

    <button>💾 Salva</button>

</form>
"""


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)