from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


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

    conexion.commit()
    conexion.close()


@app.route("/", methods=["GET", "POST"])

def obtener_usuarios():
    conexion = conectar_db()

    usuarios = conexion.execute(
        "SELECT * FROM usuarios"
    ).fetchall()

    conexion.close()

    return usuarios

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
    conexion = conectar_db()

    usuarios = conexion.execute(
        "SELECT * FROM usuarios"
    ).fetchall()

    conexion.close()

    return render_template("usuarios.html", usuarios=usuarios)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexion = conectar_db()

    if request.method == "POST":
        nombre = request.form["nombre"]

        conexion.execute(
            "UPDATE usuarios SET nombre = ? WHERE id = ?",
            (nombre, id)
        )

        conexion.commit()
        conexion.close()

        return render_template("usuarios.html", usuarios=obtener_usuarios())

    usuario = conexion.execute(
        "SELECT * FROM usuarios WHERE id = ?",
        (id,)
    ).fetchone()

    conexion.close()

    return render_template("editar.html", usuario=usuario)

@app.route("/eliminar/<int:id>")
def eliminar(id):
    conexion = conectar_db()

    conexion.execute(
        "DELETE FROM usuarios WHERE id = ?",
        (id,)
    )

    conexion.commit()

    usuarios = conexion.execute(
        "SELECT * FROM usuarios"
    ).fetchall()

    conexion.close()

    return render_template("usuarios.html", usuarios=usuarios)


if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)

def obtener_usuarios():
    conexion = conectar_db()

    usuarios = conexion.execute(
        "SELECT * FROM usuarios"
    ).fetchall()

    conexion.close()

    return usuarios