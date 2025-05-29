import sys
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from io import BytesIO

from flask import jsonify
# Importación de funciones y conexiones propias
from Metodos.GaussJordan import gauss_jordan_logica, parse_matriz
from src.conexion_sqlS import conexiondb
from Metodos.MetodosLogica import newton_raphsonLogica, secanteLogica, mullerLogica, gauss_jordan_logica
from src.GuardarEnDBMetodos import guardar_resultado_completo
from src.HistorialLogica import obtener_historial_usuario
from werkzeug.security import generate_password_hash, check_password_hash
from src.PdfLogica import Greporte  # Función para generar PDF

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'tu_clave_secreta_aqui_muy_segura')


# Decorador para proteger rutas que requieren que el usuario esté logueado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# RUTA LOGIN
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
                cursor.execute("SELECT Contrasena FROM Usuarios WHERE NombreUsuario = ?", (username,))
                row = cursor.fetchone()
            except Exception as e:
                error = f'Error en la consulta: {e}'
                row = None
            finally:
                connection.close()

            if row and check_password_hash(row[0], password):
                session['username'] = username
                return redirect(url_for('home'))
            elif not error:
                error = 'Credenciales inválidas'
        else:
            error = 'Error de conexión a la base de datos'
    return render_template('login.html', error=error)


# RUTA REGISTRO
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

                    # Verificar si usuario ya existe

                    cursor.execute("SELECT * FROM Usuarios WHERE NombreUsuario = ?", (username,))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        error = 'El usuario ya existe.'
                    else:

                        # Generar hash de contraseña
                        hashed_password = generate_password_hash(password)

                        # Recortar prefijo scrypt: si existe
                        if hashed_password.startswith("scrypt:"):
                            hashed_password = hashed_password[len("scrypt:"):]

                        # Insertar nuevo usuario con hash sin prefijo
                        cursor.execute(
                            "INSERT INTO Usuarios (NombreUsuario, Contrasena) VALUES (?, ?)",
                            (username, hashed_password)
                        )

                        connection.commit()
                        return redirect(url_for('login'))
                except Exception as e:
                    error = f'Error en la consulta: {e}'
                finally:
                    connection.close()
            else:
                error = 'Error de conexión a la base de datos'
    return render_template('registro.html', error=error)


# RUTA HOME (página principal tras login)
@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=session['username'])


# RUTA LOGOUT
@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# Función para calcular raíz según método seleccionado
def calcular_metodo(nombre_metodo, funcion, valores):
    if nombre_metodo == 'Newton':
        return newton_raphsonLogica(funcion, *valores)
    elif nombre_metodo == 'Secante':
        return secanteLogica(funcion, *valores)
    elif nombre_metodo == 'Müller':
        return mullerLogica(funcion, *valores)
    elif nombre_metodo == 'gauss_jordan':
        return gauss_jordan_logica(funcion, *valores)
    return None


# RUTAS DE MÉTODOS NUMÉRICOS
@app.route('/metodo/newton', methods=['GET', 'POST'])
@login_required
def metodo_newton():
    return metodo_generico('Newton', ['funcion', 'x0'])


@app.route('/metodo/secante', methods=['GET', 'POST'])
@login_required
def metodo_secante():
    return metodo_generico('Secante', ['funcion', 'x0', 'x1'])


@app.route('/metodo/muller', methods=['GET', 'POST'])
@login_required
def metodo_muller():
    return metodo_generico('Müller', ['funcion', 'x0', 'x1', 'x2'])


# Añadir protección de login a gauss_jordan
@app.route('/metodo/gauss_jordan', methods=['GET', 'POST'])
@login_required
def gauss_jordan():
    error = None
    resultado = None

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            matriz_texto = data.get('matriz', '')
            matriz = parse_matriz(matriz_texto)

            if matriz is None or matriz.shape[0] == 0:
                return jsonify({'error': 'Formato de matriz inválido.'})

            soluciones, mensaje = gauss_jordan_logica(matriz)
            if mensaje:
                return jsonify({'error': mensaje})
            else:
                return jsonify({'soluciones': soluciones.tolist()})
        
        # Si es POST pero no JSON (por formulario clásico)

        accion = request.form.get('accion')
        matriz_texto = request.form.get('matriz', '')

        if accion == 'calcular':
            matriz = parse_matriz(matriz_texto)
            if matriz is None or matriz.shape[0] == 0:
                error = "Formato de matriz inválido. Asegúrate de ingresar números separados por espacios y filas por líneas."
            else:
                soluciones, mensaje = gauss_jordan_logica(matriz)
                if mensaje:
                    error = mensaje
                else:
                    resultado = soluciones.tolist()

        elif accion == 'guardar':


            return redirect(url_for('gauss_jordan'))

    return render_template('gauss_jordan.html',
                           error=error,
                           resultado=resultado,
                           request=request)

# Función genérica para manejar la lógica común de los métodos
@app.route('/metodo/<nombre_metodo>', methods=['GET', 'POST'])
@login_required
def metodo_generico(nombre_metodo, campos=None):
    error = ''
    resultado = None
    datos = {campo: '' for campo in campos or []}
    accion = request.form.get('accion')

    if request.method == 'POST':
        if accion == 'guardar':
            import json
            try:
                funcion = request.form.get('funcion')
                resultado_guardar = float(request.form.get('resultado_guardar'))
                datos_json = request.form.get('datos_guardar')
                iteraciones_data = json.loads(datos_json)
                valores = [float(request.form.get(campo)) for campo in campos if campo.startswith('x')]
                usuario = session['username']

                error_relativo = None
                if iteraciones_data and isinstance(iteraciones_data, list):
                    ultima_iteracion = iteraciones_data[-1]
                    error_relativo = ultima_iteracion.get('Error')
                    try:
                        error_relativo = float(error_relativo)
                    except (ValueError, TypeError):
                        error_relativo = None

                # Guardar según método
                if nombre_metodo == 'Newton':
                    exito = guardar_resultado_completo(nombre_metodo, usuario, funcion, valores[0], datos_json, resultado_guardar, error_relativo)
                elif nombre_metodo == 'Secante':
                    exito = guardar_resultado_completo(nombre_metodo, usuario, funcion, valores[0], datos_json, resultado_guardar, error_relativo, x1=valores[1])
                elif nombre_metodo == 'Müller':
                    exito = guardar_resultado_completo(nombre_metodo, usuario, funcion, valores[0], datos_json, resultado_guardar, error_relativo, x1=valores[1], x2=valores[2])
                else:
                    exito = False

                if exito:
                    return redirect(url_for('home'))
                else:
                    error = 'Error al guardar el resultado en la base de datos.'
            except Exception as e:
                error = f'Error inesperado al guardar: {e}'

        else:
            # Recoger datos del formulario
            for campo in datos:
                datos[campo] = request.form.get(campo, '').strip()

            if any(not valor for valor in datos.values()):
                error = 'Debe llenar todos los campos.'
            else:
                try:
                    valores = [float(datos[c]) for c in datos if c.startswith('x')]
                    funcion = datos['funcion']
                    resultado = calcular_metodo(nombre_metodo, funcion, valores)

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


# RUTA HISTORIAL: muestra resultados guardados, con opción de filtrar por método y fecha
@app.route('/historial', methods=['GET', 'POST'])
@login_required
def historial():
    username = session['username']
    metodo = request.form.get('metodo', '')
    fecha = request.form.get('fecha', '')

    resultados = obtener_historial_usuario(username, metodo, fecha)

    return render_template('historial.html', username=username, resultados=resultados, metodo=metodo, fecha=fecha)

@app.route('/acerca-de')
def acerca_de():
    return render_template('acerca_de.html')


# RUTA PARA VER GRÁFICA ALMACENADA
@app.route('/ver_grafica/<int:id>')
@login_required
def ver_grafica(id):
    conn = conexiondb()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Grafica FROM ResultadosMetodos WHERE ResultadoId = ?", (id,))
        row = cursor.fetchone()
    except Exception as e:
        conn.close()
        return f"Error en la consulta: {e}", 500
    finally:
        conn.close()

    if row and row[0]:
        grafica_bytes = row[0]
        return send_file(BytesIO(grafica_bytes), mimetype='image/png')
    else:
        return "Gráfica no encontrada", 404


# RUTA PARA GENERAR REPORTE PDF
@app.route('/Greporte', methods=['POST'])
@login_required
def generar_pdf():
    print("[DEBUG] Entrando a generar_pdf()")

    resultado_id = request.form.get('resultado_id')
    nombre_usuario = request.form.get('nombre_usuario')
    fecha = request.form.get('fecha')
    nombre_metodo = request.form.get('nombre_metodo')  # Parámetro nuevo para el método

    print(f"[DEBUG] Parámetros recibidos: resultado_id={resultado_id}, nombre_usuario={nombre_usuario}, fecha={fecha}, metodo={nombre_metodo}")

    try:
        resultado_id = int(resultado_id) if resultado_id else None
    except ValueError:
        return "ID inválido.", 400

    # Validar fecha
    from datetime import datetime
    if fecha:
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return "Fecha inválida. Formato esperado: YYYY-MM-DD", 400

    pdf_buffer = Greporte(resultado_id=resultado_id, nombre_usuario=nombre_usuario, fecha=fecha, nombre_metodo=nombre_metodo)

    if not pdf_buffer:
        return "No hay datos para generar PDF.", 404

    return send_file(pdf_buffer, as_attachment=True, download_name='reporte.pdf', mimetype='application/pdf')


# PÁGINA DE AUTORES
@app.route('/autores')
@login_required
def autores():
    return render_template('autores.html')


if __name__ == '__main__':
    app.run(debug=True)
