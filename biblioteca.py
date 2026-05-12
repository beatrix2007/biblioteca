from flask import Flask, request, redirect, render_template_string, session
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# =========================
# SUPABASE CONFIG
# =========================
SUPABASE_URL = "https://ugviadmtvtkynvgztfmj.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

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
        <a class="btn dark" href="/logout">Logout</a>
        <a class="btn blue" href="/admin">Admin</a>
    {% else %}
        <a class="btn dark" href="/login">Login</a>
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

    {% if session.get("admin") %}
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

            <button>Aggiungi</button>
        </form>
    </div>
    {% endif %}

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
                <a class="btn red" href="/elimina/{{ l['id'] }}">Elimina</a>
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
    </div>
    """

    return render_template_string(html, generi=g)


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
    <h2>📦 Scaffali</h2>

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
    </div>
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