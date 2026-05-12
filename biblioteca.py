from flask import Flask, request, redirect, render_template_string, session
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

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
print("KEY:", SUPABASE_KEY)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# =========================
# AUTH
# =========================
def is_admin():
    return session.get("admin") is True


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/")
        return "❌ Password errata"

    return """
    <h2>Login Admin</h2>
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
# BASE UI
# =========================
BASE = """
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body { font-family: Arial; background:#f4f6f8; margin:0; }
.container { max-width:900px; margin:auto; padding:20px; }

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
    padding:10px;
    border:none;
    border-radius:8px;
    background:#2c3e50;
    color:white;
    cursor:pointer;
}

a { text-decoration:none; }

.btn { padding:6px 10px; border-radius:8px; color:white; display:inline-block; }
.red { background:#e74c3c; }
.blue { background:#3498db; }
.dark { background:#2c3e50; }
</style>

<div class="container">
"""

@app.route("/modifica/<int:id>", methods=["GET", "POST"])
def modifica(id):
    if not is_admin():
        return "Non autorizzato", 403

    # GET → mostra form
    if request.method == "GET":
        libro = requests.get(
            SUPABASE_URL + f"/rest/v1/libri?id=eq.{id}&select=*",
            headers=headers
        ).json()

        if not libro:
            return "Libro non trovato"

        libro = libro[0]

        generi = requests.get(SUPABASE_URL + "/rest/v1/generi?select=*", headers=headers).json()
        scaffali = requests.get(SUPABASE_URL + "/rest/v1/scaffali?select=*", headers=headers).json()

        html = BASE + """
        <h2>✏️ Modifica libro</h2>

        <form method="POST">

            <input name="titolo" value="{{ libro['titolo'] }}" required>
            <input name="autore" value="{{ libro['autore'] }}">

            <select name="tipo">
                <option value="libro" {% if libro['tipo']=='libro' %}selected{% endif %}>Libro</option>
                <option value="rivista" {% if libro['tipo']=='rivista' %}selected{% endif %}>Rivista</option>
                <option value="fumetto" {% if libro['tipo']=='fumetto' %}selected{% endif %}>Fumetto</option>
            </select>

            <select name="genere">
                {% for g in generi %}
                    <option value="{{ g['nome'] }}" {% if g['nome']==libro['genere'] %}selected{% endif %}>
                        {{ g['nome'] }}
                    </option>
                {% endfor %}
            </select>

            <select name="scaffale">
                {% for s in scaffali %}
                    <option value="{{ s['nome'] }}" {% if s['nome']==libro['scaffale'] %}selected{% endif %}>
                        {{ s['nome'] }}
                    </option>
                {% endfor %}
            </select>

            <button>Salva modifiche</button>
        </form>
        """

        return render_template_string(html, libro=libro, generi=generi, scaffali=scaffali)

    # POST → salva modifiche
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
# =========================
# HOME
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
    

    html = BASE + """
    <h2>📚 Biblioteca</h2>

    {% if session.get("admin") %}
        <a class="btn blue" href="/admin">Admin</a>
        <a class="btn dark" href="/logout">Logout</a>
    {% else %}
        <a class="btn dark" href="/login">Login</a>
    {% endif %}

    {% if session.get("admin") %}
    <div class="card">
        <h3>➕ Aggiungi libro</h3>
        <form method="POST" action="/aggiungi">

            <input name="titolo" placeholder="Titolo">
            <input name="autore" placeholder="Autore">

            <select name="tipo">
                <option value="libro">Libro</option>
                <option value="rivista">Rivista</option>
                <option value="fumetto">Fumetto</option>
            </select>

            <select name="genere">
                <option value="-" selected>-</option>
                {% for g in generi %}
                    <option value="{{ g['nome'] }}">{{ g['nome'] }}</option>
                {% endfor %}
            </select>

            <select name="scaffale">
                <option value="-" selected>-</option>
                {% for g in scaffali %}
                    <option value="{{ g['nome'] }}">{{ g['nome'] }}</option>
                {% endfor %}
            </select>

            <button>Aggiungi</button>
            </form>
        </div>
    {% endif %}

    <div class="card">
    <h3>🔍 Filtri</h3>
    <form method="GET">

        <input name="titolo" placeholder="Titolo">
        <input name="autore" placeholder="Autore">

        <select name="tipo">
            <option value="">Tipo</option>
            <option value="libro">Libro</option>
            <option value="rivista">Rivista</option>
            <option value="fumetto">Fumetto</option>
        </select>

        <select name="genere">
            <option value="">Genere</option>
            {% for g in generi %}
                <option value="{{ g['nome'] }}">{{ g['nome'] }}</option>
            {% endfor %}
        </select>

        <select name="scaffale">
            <option value="">Scaffale</option>
            {% for s in scaffali %}
                <option value="{{ s['nome'] }}">{{ s['nome'] }}</option>
            {% endfor %}
        </select>

        <button>Cerca</button>
    </form>
    </div>

    <h3>📖 Libri</h3>

    {% if libri|length == 0 %}
        <div class="card">📭 Nessun libro</div>
    {% else %}
        {% for l in libri %}
        <div class="card">
            <b>{{ l['titolo'] }}</b><br>
            ✍️ {{ l['autore'] }}<br>
            📚 {{ l['tipo'] }} | {{ l['genere'] }} | {{ l['scaffale'] }}

            {% if session.get("admin") %}
            <div style="margin-top:10px;">
                <a class="btn blue" href="/modifica/{{ l['id'] }}">Modifica</a>
                <a class="btn red" href="/elimina/{{ l['id'] }}"
                onclick="return confirm('Sei sicura di voler eliminare questo libro?')">
                Elimina
                </a>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    {% endif %}

    </div>
    """

    return render_template_string(html, libri=libri, generi=generi, scaffali=scaffali)


# =========================
# LIBRI CRUD
# =========================
@app.route("/aggiungi", methods=["POST"])
def aggiungi():
    if not is_admin():
        return "Non autorizzato", 403

    if not  request.form["titolo"].upper():
        return """
        <div class="card">❌ Titolo obbligatorio</div>
        """

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

    requests.delete(SUPABASE_URL + f"/rest/v1/libri?id=eq.{id}", headers=headers)
    return redirect("/")


# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
def admin():
    if not is_admin():
        return "Non autorizzato", 403

    return BASE + """
    <h2>⚙️ Admin</h2>

    <a class="btn dark" href="/admin/generi">Generi</a>
    <a class="btn dark" href="/admin/scaffali">Scaffali</a>
    <a class="btn dark" href="/admin/statistiche">Dashboard</a>
    </div>
    """


# =========================
# GENERI
# =========================
@app.route("/admin/generi")
def generi():
    if not is_admin():
        return "Non autorizzato", 403

    g = requests.get(SUPABASE_URL + "/rest/v1/generi?select=*", headers=headers).json()

    html = BASE + """
    <h2>📚 Generi</h2>
    <form method="POST" action="/admin/generi/add">
        <input name="nome">
        <button>Aggiungi</button>
    </form>

    {% for x in generi %}
        <div class="card">
            {{ x['nome'] }}
            <a class="btn red" href="/admin/generi/delete/{{ x['id'] }}">X</a>
        </div>
    {% endfor %}
    <hr>
    <a href="/" style="
        display:inline-block;
        padding:10px 14px;
        background:#2c3e50;
        color:white;
        border-radius:8px;
        text-decoration:none;
        margin-top:10px;
    ">
    🏠 Torna alla Home
    </a>
    """

    return render_template_string(html, generi=g)

@app.route("/admin/statistiche")
def statistiche():
    if not is_admin():
        return "Non autorizzato", 403

    libri = requests.get(
        SUPABASE_URL + "/rest/v1/libri?select=*",
        headers=headers
    ).json()

    conteggio_genere = {}

    for l in libri:
        genere = l.get("genere") or "Sconosciuto"
        conteggio_genere[genere] = conteggio_genere.get(genere, 0) + 1

    html = BASE + """
    <h3>📊 Libri per genere</h3>

    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-bottom:20px;">

    {% for genere, count in conteggio_genere.items() %}
    <div class="card">
        📚 <b>{{ genere }}</b><br>
        {{ count }} libri
    </div>
    {% endfor %}

    </div>

    <hr>

    <a href="/" style="
        display:inline-block;
        padding:10px 14px;
        background:#2c3e50;
        color:white;
        border-radius:8px;
        text-decoration:none;
        margin-top:10px;
    ">
    🏠 Torna alla Home
    </a>
    """

    return render_template_string(html, conteggio_genere=conteggio_genere)


@app.route("/admin/generi/add", methods=["POST"])
def add_genere():
    requests.post(SUPABASE_URL + "/rest/v1/generi",
                  headers=headers,
                  json={"nome": request.form["nome"].lower()})
    return redirect("/admin/generi")


@app.route("/admin/generi/delete/<int:id>")
def delete_genere(id):
    requests.delete(SUPABASE_URL + f"/rest/v1/generi?id=eq.{id}", headers=headers)
    return redirect("/admin/generi")


# =========================
# SCAFFALI
# =========================
@app.route("/admin/scaffali")
def scaffali():
    if not is_admin():
        return "Non autorizzato", 403

    s = requests.get(SUPABASE_URL + "/rest/v1/scaffali?select=*", headers=headers).json()

    html = BASE + """
    <h2>📚 Scaffali</h2>
    <form method="POST" action="/admin/scaffali/add">
        <input name="nome">
        <button>Aggiungi</button>
    </form>

    {% for x in scaffali %}
        <div class="card">
            {{ x['nome'] }}
            <a class="btn red" href="/admin/scaffali/delete/{{ x['id'] }}">X</a>
        </div>
    {% endfor %}
    <hr>
    <a href="/" style="
        display:inline-block;
        padding:10px 14px;
        background:#2c3e50;
        color:white;
        border-radius:8px;
        text-decoration:none;
        margin-top:10px;
    ">
    🏠 Torna alla Home
    </a>
    """

    return render_template_string(html, scaffali=s)


@app.route("/admin/scaffali/add", methods=["POST"])
def add_scaffale():
    requests.post(SUPABASE_URL + "/rest/v1/scaffali",
                  headers=headers,
                  json={"nome": request.form["nome"].upper()})
    return redirect("/admin/scaffali")


@app.route("/admin/scaffali/delete/<int:id>")
def delete_scaffale(id):
    requests.delete(SUPABASE_URL + f"/rest/v1/scaffali?id=eq.{id}", headers=headers)
    return redirect("/admin/scaffali")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)