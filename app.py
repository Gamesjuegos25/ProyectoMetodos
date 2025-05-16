from flask import Flask, render_template, request, redirect, url_for, session
from src.conexion_sqlS import conexiondb
from Metodos.MetodosLogica import newton_raphsonLogica, secanteLogica, mullerLogica
from src.GuardarEnDBMetodos import guardar_resultado_newton, guardar_resultado_secante, guardar_resultado_muller

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        connection = conexiondb()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Usuarios WHERE NombreUsuario = ? AND Contrasena = ?", (username, password))
                user = cursor.fetchone()
            except Exception as e:
                error = f'Error en la consulta: {e}'
                user = None
            finally:
                connection.close()

            if user:
                session['username'] = username
                return redirect(url_for('menu'))
            elif not error:
                error = 'Credenciales inválidas'
        else:
            error = 'Error de conexión a la base de datos'
    return render_template('login.html', error=error)

# REGISTRO
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            error = 'Debe llenar todos los campos.'
        else:
            connection = conexiondb()
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute("SELECT * FROM Usuarios WHERE NombreUsuario = ?", (username,))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        error = 'El usuario ya existe.'
                    else:
                        cursor.execute("INSERT INTO Usuarios (NombreUsuario, Contrasena) VALUES (?, ?)", (username, password))
                        connection.commit()
                        return redirect(url_for('login'))
                except Exception as e:
                    error = f'Error en la consulta: {e}'
                finally:
                    connection.close()
            else:
                error = 'Error de conexión a la base de datos'
    return render_template('registro.html', error=error)

# MENÚ PRINCIPAL
@app.route('/menu')
def menu():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html', username=session['username'])

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# MÉTODO NEWTON
@app.route('/metodo/newton', methods=['GET', 'POST'])
def metodo_newton():
    if 'username' not in session:
        return redirect(url_for('login'))

    error = ''
    resultado = None
    funcion = ''
    x0 = ''

    if request.method == 'POST':
        funcion = request.form.get('funcion', '').strip()
        x0 = request.form.get('x0', '').strip()
        accion = request.form.get('accion')

        if not funcion or not x0:
            error = 'Debe llenar todos los campos.'
        else:
            try:
                x0_float = float(x0)
                resultado = newton_raphsonLogica(funcion, x0_float)
                if resultado is None or resultado[0] is None:
                    error = 'No se pudo encontrar la raíz.'
                else:
                    if accion == 'guardar':
                        usuario = session['username']
                        raiz, iteraciones = resultado
                        exito = guardar_resultado_newton(usuario, funcion, x0_float, iteraciones, raiz)
                        if exito:
                            return redirect(url_for('menu'))
                        else:
                            error = 'Error al guardar el resultado en la base de datos.'
            except ValueError:
                error = 'X0 debe ser un número.'

    return render_template('metodo_generico.html', error=error, resultado=resultado, nombre_metodo='Newton', campos=['funcion', 'x0'])

# MÉTODO SECANTE
@app.route('/metodo/secante', methods=['GET', 'POST'])
def metodo_secante():
    if 'username' not in session:
        return redirect(url_for('login'))

    error = ''
    resultado = None

    if request.method == 'POST':
        funcion = request.form.get('funcion', '').strip()
        x0 = request.form.get('x0', '').strip()
        x1 = request.form.get('x1', '').strip()
        accion = request.form.get('accion')

        if not funcion or not x0 or not x1:
            error = 'Debe llenar todos los campos.'
        else:
            try:
                x0_float = float(x0)
                x1_float = float(x1)
                resultado, iteraciones = secanteLogica(funcion, x0_float, x1_float)
                if resultado is None:
                    error = 'No se pudo encontrar la raíz.'
                else:
                    if accion == 'guardar':
                        usuario = session['username']
                        exito = guardar_resultado_secante(usuario, funcion, x0_float, x1_float, iteraciones, resultado)
                        if exito:
                            return redirect(url_for('menu'))
                        else:
                            error = 'Error al guardar el resultado en la base de datos.'
            except ValueError:
                error = 'X0 y X1 deben ser números.'

    return render_template('metodo_generico.html', error=error, resultado=resultado, nombre_metodo='Secante', campos=['funcion', 'x0', 'x1'])

# MÉTODO MÜLLER
@app.route('/metodo/muller', methods=['GET', 'POST'])
def metodo_muller():
    if 'username' not in session:
        return redirect(url_for('login'))

    error = ''
    resultado = None

    if request.method == 'POST':
        funcion = request.form.get('funcion', '').strip()
        x0 = request.form.get('x0', '').strip()
        x1 = request.form.get('x1', '').strip()
        x2 = request.form.get('x2', '').strip()
        accion = request.form.get('accion')

        if not funcion or not x0 or not x1 or not x2:
            error = 'Debe llenar todos los campos.'
        else:
            try:
                x0_float = float(x0)
                x1_float = float(x1)
                x2_float = float(x2)
                resultado, iteraciones = mullerLogica(funcion, x0_float, x1_float, x2_float)
                if resultado is None:
                    error = 'No se pudo encontrar la raíz.'
                else:
                    if accion == 'guardar':
                        usuario = session['username']
                        exito = guardar_resultado_muller(usuario, funcion, x0_float, x1_float, x2_float, iteraciones, resultado)
                        if exito:
                            return redirect(url_for('menu'))
                        else:
                            error = 'Error al guardar el resultado en la base de datos.'
            except ValueError:
                error = 'Los valores deben ser números.'

    return render_template('metodo_generico.html', error=error, resultado=resultado, nombre_metodo='Müller', campos=['funcion', 'x0', 'x1', 'x2'])

if __name__ == '__main__':
    app.run(debug=True)
