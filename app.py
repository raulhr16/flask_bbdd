from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'some_secret_key'

# Función para obtener las bases de datos disponibles
def obtener_bases_de_datos():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="raulhr",
            password="raulhr",
            host="localhost"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        bases_de_datos = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return bases_de_datos
    except Exception as e:
        print(f"Error al obtener bases de datos: {e}")
        return []

# Función para obtener las tablas accesibles para el usuario
def obtener_tablas(database, user, password):
    try:
        conn = psycopg2.connect(
            dbname=database,
            user=user,
            password=password,
            host="localhost"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tablas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tablas
    except Exception as e:
        print(f"Error al obtener tablas: {e}")
        return []

# Función para obtener registros de una tabla
def obtener_registros(database, user, password, tabla):
    try:
        conn = psycopg2.connect(
            dbname=database,
            user=user,
            password=password,
            host="localhost"
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {tabla};")
        registros = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]  # Obtener nombres de columnas
        cursor.close()
        conn.close()
        return columnas, registros
    except Exception as e:
        print(f"Error al obtener registros: {e}")
        return [], []

@app.route('/')
def inicio():
    databases = obtener_bases_de_datos()
    return render_template("index.html", databases=databases)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    database = request.form['database']

    try:
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host="localhost"
        )
        conn.close()

        # Si la conexión es exitosa, guardar información en la sesión
        session['username'] = username
        session['password'] = password
        session['database'] = database

        flash(f"Conectado exitosamente a la base de datos {database}.", "success")
        return redirect(url_for('tablas'))
    except psycopg2.Error as e:
        flash(f"Error al conectar a la base de datos {database}: {e}", "danger")
        return redirect(url_for('inicio'))

@app.route('/tablas')
def tablas():
    if 'username' not in session:
        return redirect(url_for('inicio'))

    tablas = obtener_tablas(session['database'], session['username'], session['password'])
    return render_template("tablas.html", tablas=tablas)

@app.route('/tabla/<nombre_tabla>')
def tabla(nombre_tabla):
    if 'username' not in session:
        return redirect(url_for('inicio'))

    columnas, registros = obtener_registros(session['database'], session['username'], session['password'], nombre_tabla)
    return render_template("registros.html", nombre_tabla=nombre_tabla, columnas=columnas, registros=registros)

if __name__ == '__main__':
    app.run(debug=True)
