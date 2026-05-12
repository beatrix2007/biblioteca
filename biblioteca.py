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

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")

# =========================
# AUTH
# =========================
def is_admin():
    return session.get("admin") is True


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
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

input, select, textarea {
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

<script>
function toggleTrama(id) {
    const el = document.getElementById("trama-" + id);
    if (!el) return;

    if (el.style.display === "none" || el.style.display === "") {
        el.style.display = "block";
    } else {
        el.style.display = "none";
    }
}
</script>

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

    if titolo:
        url += f"&titolo=ilike.*{titolo}*"
    if autore:
        url += f"&autore=ilike.*{autore}*"

    libri = requests.get(url, headers=headers).json()

    html = BASE + """
    <h2>📚 Biblioteca</h2>

    {% if session.get("admin") %}
        <a class="btn dark" href="/logout">Logout</a>
    {% else %}
        <a class="btn dark" href="/login">Login</a>
    {% endif %}

    {% if session.get("admin") %}
    <div class="card">
        <h3>➕ Aggiungi libro</h3>
        <form method="POST" action="/aggiungi">

            <input name="titolo" placeholder="Titolo" required>
            <input name="autore" placeholder="Autore">
            <textarea name="trama" placeholder="Trama"></textarea>

            <button>Aggiungi</button>
        </form>
    </div>
    {% endif %}

    <h3>📖 Libri</h3>

    {% for l in libri %}
    <div class="card">
        <b>{{ l['titolo'] }}</b><br>
        ✍️ {{ l['autore'] }}

        {% if l.get('trama') %}
        <div style="margin-top:10px;">
            <button onclick="toggleTrama({{ l['id'] }})">➕</button>

            <div id="trama-{{ l['id'] }}" style="display:none;">
                {{ l['trama'] }}
            </div>
        </div>
        {% endif %}

        {% if session.get("admin") %}
        <div style="margin-top:10px;">
            <a class="btn blue" href="/modifica/{{ l['id'] }}">Modifica</a>
            <a class="btn red" href="/elimina/{{ l['id'] }}"
            onclick="return confirm('Sei sicura?')">Elimina</a>
        </div>
        {% endif %}
    </div>
    {% endfor %}
    </div>
    """

    return render_template_string(html, libri=libri)


# =========================
# AGGIUNGI
# =========================
@app.route("/aggiungi", methods=["POST"])
def aggiungi():
    if not is_admin():
        return "Non autorizzato", 403

    titolo = request.form.get("titolo", "").strip()
    autore = request.form.get("autore", "").strip()
    trama = request.form.get("trama", "").strip()

    if not titolo:
        return "Titolo obbligatorio"

    data = {
        "titolo": titolo.upper(),
        "autore": autore.upper(),
        "trama": trama
    }

    requests.post(SUPABASE_URL + "/rest/v1/libri", headers=headers, json=data)

    return redirect("/")


# =========================
# MODIFICA
# =========================
@app.route("/modifica/<int:id>", methods=["GET", "POST"])
def modifica(id):
    if not is_admin():
        return "Non autorizzato", 403

    if request.method == "GET":
        libro = requests.get(
            SUPABASE_URL + f"/rest/v1/libri?id=eq.{id}&select=*",
            headers=headers
        ).json()[0]

        html = BASE + """
        <h2>✏️ Modifica</h2>

        <form method="POST">
            <input name="titolo" value="{{ libro['titolo'] }}" required>
            <input name="autore" value="{{ libro['autore'] }}">
            <textarea name="trama">{{ libro['trama'] }}</textarea>

            <button>Salva</button>
        </form>
        """

        return render_template_string(html, libro=libro)

    titolo = request.form.get("titolo", "").strip()
    autore = request.form.get("autore", "").strip()
    trama = request.form.get("trama", "").strip()

    data = {
        "titolo": titolo.upper(),
        "autore": autore.upper(),
        "trama": trama
    }

    requests.patch(
        SUPABASE_URL + f"/rest/v1/libri?id=eq.{id}",
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

    requests.delete(SUPABASE_URL + f"/rest/v1/libri?id=eq.{id}", headers=headers)
    return redirect("/")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)