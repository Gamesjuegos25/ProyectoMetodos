import json
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from io import BytesIO
from src.conexion_sqlS import conexiondb
from Metodos.MetodosLogica import newton_raphsonLogica, secanteLogica, mullerLogica
from src.GuardarEnDBMetodos import guardar_resultado_newton, guardar_resultado_secante, guardar_resultado_muller
from src.HistorialLogica import obtener_historial_usuario

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
                return redirect(url_for('home'))
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

# HOME
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', username=session['username'])

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# MÉTODO NEWTON
@app.route('/metodo/newton', methods=['GET', 'POST'])
def metodo_newton():
    return metodo_generico('Newton', ['funcion', 'x0'])

# MÉTODO SECANTE
@app.route('/metodo/secante', methods=['GET', 'POST'])
def metodo_secante():
    return metodo_generico('Secante', ['funcion', 'x0', 'x1'])

# MÉTODO MÜLLER
@app.route('/metodo/muller', methods=['GET', 'POST'])
def metodo_muller():
    return metodo_generico('Müller', ['funcion', 'x0', 'x1', 'x2'])

@app.route('/autores')
def autores():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('autores.html')

# MÉTODO GENÉRICO (calcular y guardar)
@app.route('/metodo/<nombre_metodo>', methods=['GET', 'POST'])
def metodo_generico(nombre_metodo, campos=None):
    if 'username' not in session:
        return redirect(url_for('login'))

    error = ''
    resultado = None
    datos = {campo: '' for campo in campos or []}
    accion = request.form.get('accion')

    if request.method == 'POST':
        if accion == 'guardar':
            try:
                funcion = request.form.get('funcion')
                resultado_guardar = float(request.form.get('resultado_guardar'))
                datos_json = request.form.get('datos_guardar') 
                iteraciones_data = json.loads(datos_json)  
                valores = [float(request.form.get(campo)) for campo in campos if campo.startswith('x')]
                usuario = session['username']

                # Obtener último error relativo si existe
                error_relativo = None
                if iteraciones_data and isinstance(iteraciones_data, list):
                    ultima_iteracion = iteraciones_data[-1]
                    error_relativo = ultima_iteracion.get('Error')
                    try:
                        error_relativo = float(error_relativo)
                    except (ValueError, TypeError):
                        error_relativo = None

                # Guardar resultados según el método
                if nombre_metodo == 'Newton':
                    exito = guardar_resultado_newton(usuario, funcion, valores[0], datos_json, resultado_guardar, error_relativo)
                elif nombre_metodo == 'Secante':
                    exito = guardar_resultado_secante(usuario, funcion, valores[0], valores[1], datos_json, resultado_guardar, error_relativo)
                elif nombre_metodo == 'Müller':
                    exito = guardar_resultado_muller(usuario, funcion, valores[0], valores[1], valores[2], datos_json, resultado_guardar, error_relativo)

                if exito:
                    return redirect(url_for('home'))
                else:
                    error = 'Error al guardar el resultado en la base de datos.'
            except Exception as e:
                error = f'Error inesperado al guardar: {e}'

        else:  # Acción calcular
            for campo in datos:
                datos[campo] = request.form.get(campo, '').strip()

            if any(not valor for valor in datos.values()):
                error = 'Debe llenar todos los campos.'
            else:
                try:
                    valores = [float(datos[c]) for c in datos if c.startswith('x')]
                    funcion = datos['funcion']
                    if nombre_metodo == 'Newton':
                        resultado = newton_raphsonLogica(funcion, *valores)
                    elif nombre_metodo == 'Secante':
                        resultado = secanteLogica(funcion, *valores)
                    elif nombre_metodo == 'Müller':
                        resultado = mullerLogica(funcion, *valores)
                    if resultado is None or resultado[0] is None:
                        error = 'No se pudo encontrar la raíz.'
                except ValueError:
                    error = 'Los valores deben ser números.'

    return render_template('metodo_generico.html',
                           error=error,
                           resultado=resultado,
                           nombre_metodo=nombre_metodo,
                           campos=campos or [],
                           datos=datos)

# HISTORIAL
@app.route('/historial', methods=['GET', 'POST'])
def historial():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    metodo = request.form.get('metodo', '')
    fecha = request.form.get('fecha', '')
    
    resultados = obtener_historial_usuario(username, metodo, fecha)
    
    return render_template('historial.html', username=username, resultados=resultados, metodo=metodo, fecha=fecha)

# VER GRÁFICA
@app.route('/ver_grafica/<metodo>/<int:id>')
def ver_grafica(metodo, id):
    conn = conexiondb()
    cursor = conn.cursor()

    tabla = None
    metodo_lower = metodo.lower()
    if metodo_lower == 'newton':
        tabla = 'ResultadosNewton'
    elif metodo_lower == 'muller':
        tabla = 'ResultadosMuller'
    elif metodo_lower == 'secante':
        tabla = 'ResultadosSecante'
    else:
        return "Método no válido", 400

    try:
        cursor.execute(f"SELECT Grafica FROM {tabla} WHERE ResultadoId = ?", (id,))
        row = cursor.fetchone()
    except Exception as e:
        conn.close()
        return f"Error en la consulta: {e}", 500

    conn.close()

    if row and row[0]:
        grafica_bytes = row[0]  # Esto es un objeto tipo bytes
        return send_file(BytesIO(grafica_bytes), mimetype='image/png')
    else:
        return "Gráfica no encontrada", 404
    
if __name__ == '__main__':
    app.run(debug=True)
