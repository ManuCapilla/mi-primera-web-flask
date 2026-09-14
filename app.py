from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "clave-secreta-temporal"


def conectar_db():
    conexion = sqlite3.connect("usuarios.db")
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tabla():
    conexion = conectar_db()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS cuentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


def obtener_usuarios():
    conexion = conectar_db()

    usuarios = conexion.execute(
        "SELECT * FROM usuarios"
    ).fetchall()

    conexion.close()

    return usuarios

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]

        conexion = conectar_db()

        cuenta = conexion.execute(
            "SELECT * FROM cuentas WHERE usuario = ?",
            (usuario,)
        ).fetchone()

        conexion.close()

        if cuenta and check_password_hash(cuenta["password"], password):

            session["usuario"] = usuario

            return redirect(url_for("inicio"))

        return render_template(
            "login.html",
            error="Usuario o contraseña incorrectos."
        )

    return render_template("login.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST":

        usuario = request.form["usuario"]
        password = request.form["password"]

        password_hash = generate_password_hash(password)

        conexion = conectar_db()

        try:

            conexion.execute(
                "INSERT INTO cuentas (usuario, password) VALUES (?, ?)",
                (usuario, password_hash)
            )

            conexion.commit()
            conexion.close()

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            conexion.close()

            return render_template(
                "registro.html",
                error="Ese usuario ya existe."
            )

    return render_template("registro.html")

@app.route("/logout")
def logout():

    session.pop("usuario", None)

    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def inicio():
    if request.method == "POST":
        nombre = request.form["nombre"]

        conexion = conectar_db()

        conexion.execute(
            "INSERT INTO usuarios (nombre) VALUES (?)",
            (nombre,)
        )

        conexion.commit()
        conexion.close()

        return render_template("index.html", nombre=nombre)

    return render_template("index.html")


@app.route("/usuarios")
def usuarios():

    if "usuario" not in session:
        return redirect(url_for("login"))

    usuarios = obtener_usuarios()

    return render_template(
        "usuarios.html",
        usuarios=usuarios
    )


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    if "usuario" not in session:
        return redirect(url_for("login"))

    conexion = conectar_db()

    if request.method == "POST":
        nombre = request.form["nombre"]

        conexion.execute(
            "UPDATE usuarios SET nombre = ? WHERE id = ?",
            (nombre, id)
        )

        conexion.commit()
        conexion.close()

        return render_template(
            "usuarios.html",
            usuarios=obtener_usuarios()
        )

    usuario = conexion.execute(
        "SELECT * FROM usuarios WHERE id = ?",
        (id,)
    ).fetchone()

    conexion.close()

    return render_template(
        "editar.html",
        usuario=usuario
    )


    conexion.commit()
    conexion.close()

    return render_template(
        "usuarios.html",
        usuarios=obtener_usuarios()
    )

@app.route("/eliminar/<int:id>")
def eliminar(id):

    if "usuario" not in session:
        return redirect(url_for("login"))

    conexion = conectar_db()

    conexion.execute(
        "DELETE FROM usuarios WHERE id = ?",
        (id,)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("usuarios"))


crear_tabla()
def crear_admin():
    conexion = conectar_db()

    usuario = "admin"
    password = generate_password_hash("admin123")

    try:
        conexion.execute(
            "INSERT INTO cuentas (usuario, password) VALUES (?, ?)",
            (usuario, password)
        )

        conexion.commit()

    except sqlite3.IntegrityError:
        pass

    conexion.close()


crear_admin()

if __name__ == "__main__":
    app.run(debug=True)