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

    return render_template_string(HTML, libri=libri, generi=generi, scaffali=scaffali)


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
# ADMIN PANNELLO LINKS
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


@app.route("/admin/scaffali")
def admin_scaffali():

    if not is_admin():
        return "Non autorizzato", 403

    scaffali = requests.get(
        SUPABASE_URL + "/rest/v1/scaffali?select=*",
        headers=headers
    ).json()

    return render_template_string(SCAFFALI_HTML, scaffali=scaffali)


# =========================
# GENERI CRUD
# =========================
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
# SCAFFALI CRUD
# =========================
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


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)