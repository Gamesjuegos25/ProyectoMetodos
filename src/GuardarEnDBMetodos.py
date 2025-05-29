from src.conexion_sqlS import conexiondb
import traceback
import io
import matplotlib.pyplot as plt
import sympy as sp
import numpy as np
import pyodbc
import json

def crear_grafica(funcion_str, raiz):
    try:
        x = sp.symbols('x')
        funcion = sp.sympify(funcion_str)
        f_lambda = sp.lambdify(x, funcion, modules=["numpy"])
        x_vals = np.linspace(raiz - 1, raiz + 1, 100)
        y_vals = f_lambda(x_vals)

        plt.figure()
        plt.plot(x_vals, y_vals, label='f(x)')
        plt.scatter([raiz], [0], color='red', label='Raíz aproximada')
        plt.legend()
        plt.title('Gráfica de la función y raíz')
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        print("[crear_grafica] Gráfica creada correctamente")
        return buf.read()
    except Exception as e:
        print(f"[crear_grafica] Error al crear gráfica: {e}")
        print(traceback.format_exc())
        return None

def insertar_iteracion(cursor, resultado_id, iteracion_num, error, x0, x1, x2, fx0, fx1, fx2):
    try:
        print(f"[insertar_iteracion] Insertando iteración {iteracion_num} con valores:")
        print(f"  ResultadoId={resultado_id}, ErrorRelativo={error}, X0={x0}, X1={x1}, X2={x2}, fX0={fx0}, fX1={fx1}, fX2={fx2}")
        cursor.execute("""
            INSERT INTO IteracionesDetalle (
                ResultadoId, Iteracion, ErrorRelativo, X0, X1, X2, fX0, fX1, fX2
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (resultado_id, iteracion_num, error, x0, x1, x2, fx0, fx1, fx2))
    except Exception as e:
        print(f"[insertar_iteracion] Error al insertar iteración {iteracion_num}: {e}")
        print(traceback.format_exc())
        raise

def guardar_resultado_newton(cursor, resultado_id, lista_iteraciones):
    for i, iteracion in enumerate(lista_iteraciones, start=1):
        if isinstance(iteracion, str):
            iteracion = json.loads(iteracion)
        x0_val = iteracion.get('x', iteracion.get('x0', None))
        fx0_val = iteracion.get('fx0', iteracion.get('f(x0)', None))
        error_val = iteracion.get('Error', 0)
        insertar_iteracion(cursor, resultado_id, i, error_val, x0_val, None, None, fx0_val, None, None)

def guardar_resultado_secante(cursor, resultado_id, lista_iteraciones):
    for i, iteracion in enumerate(lista_iteraciones, start=1):
        if isinstance(iteracion, str):
            iteracion = json.loads(iteracion)
        x0_val = iteracion.get('x0', None)
        x1_val = iteracion.get('x1', None)
        fX0_val = iteracion.get('f(x0)', None)
        fX1_val = iteracion.get('f(x1)', None)
        error_val = iteracion.get('Error', 0)
        insertar_iteracion(cursor, resultado_id, i, error_val, x0_val, x1_val, None, fX0_val, fX1_val, None)

def guardar_resultado_muller(cursor, resultado_id, lista_iteraciones):
    for i, iteracion in enumerate(lista_iteraciones, start=1):
        if isinstance(iteracion, str):
            iteracion = json.loads(iteracion)
        x0_val = iteracion.get('x0', None)
        x1_val = iteracion.get('x1', None)
        x2_val = iteracion.get('x2', None)
        fX0_val = iteracion.get('fX0', None)
        fX1_val = iteracion.get('fX1', None)
        fX2_val = iteracion.get('fX2', None)
        error_val = iteracion.get('Error', 0)
        insertar_iteracion(cursor, resultado_id, i, error_val, x0_val, x1_val, x2_val, fX0_val, fX1_val, fX2_val)

def guardar_resultado_completo(
    metodo_nombre, usuario, funcion, x0, lista_iteraciones, resultado, error_relativo,
    grafica_bytes=None, x1=None, x2=None, max_iteraciones=100
):
    try:
        print("[guardar_resultado_completo] Inicio de guardado")
        if isinstance(lista_iteraciones, str):
            print("[guardar_resultado_completo] Parseando lista_iteraciones de JSON")
            lista_iteraciones = json.loads(lista_iteraciones)
        
        if max_iteraciones is not None:
            lista_iteraciones = lista_iteraciones[:max_iteraciones]
            print(f"[guardar_resultado_completo] Limitando iteraciones a {max_iteraciones}")

        iteraciones = len(lista_iteraciones)
        print(f"[guardar_resultado_completo] Total iteraciones a guardar: {iteraciones}")

        if grafica_bytes is None:
            print("[guardar_resultado_completo] Creando gráfica porque no se recibió")
            grafica_bytes = crear_grafica(funcion, resultado)
            if grafica_bytes is None:
                print("[guardar_resultado_completo] Advertencia: gráfica no creada")

        error_relativo = float(error_relativo)
        print(f"[guardar_resultado_completo] Error relativo: {error_relativo}")

        connection = conexiondb()
        cursor = connection.cursor()
        connection.autocommit = False
        print("[guardar_resultado_completo] Conexión abierta")

        cursor.execute("SELECT MetodoId FROM Metodos WHERE LOWER(Nombre) = ?", (metodo_nombre.lower(),))
        fila = cursor.fetchone()
        if not fila:
            raise ValueError(f"Método '{metodo_nombre}' no encontrado en la base de datos.")
        metodo_id = fila[0]
        print(f"[guardar_resultado_completo] MetodoId encontrado: {metodo_id}")

        print("[guardar_resultado_completo] Insertando resultado principal")
        cursor.execute("""
            INSERT INTO ResultadosMetodos (
                MetodoId, NombreUsuario, Funcion, X0, X1, X2,
                Iteraciones, Resultado, ErrorRelativo, Grafica
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metodo_id, usuario, funcion, x0, x1, x2,
            iteraciones, resultado, error_relativo, pyodbc.Binary(grafica_bytes)
        ))

        cursor.execute("SELECT @@IDENTITY")
        resultado_id = cursor.fetchone()[0]
        print(f"[guardar_resultado_completo] ResultadoId insertado: {resultado_id}")

        # Insertar iteración inicial (iteración 0)
        print("[guardar_resultado_completo] Insertando iteración inicial (0)")
        cursor.execute("""
            INSERT INTO IteracionesDetalle (
                ResultadoId, Iteracion, ErrorRelativo, X0, X1, X2, fX0, fX1, fX2
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resultado_id, 0, None, x0, x1, x2, None, None, None,
        ))

        metodo_lower = metodo_nombre.lower()
        print(f"[guardar_resultado_completo] Guardando iteraciones según método '{metodo_lower}'")

        if metodo_lower in ['newton', 'newton-raphson']:
            guardar_resultado_newton(cursor, resultado_id, lista_iteraciones)
        elif metodo_lower == 'secante':
            guardar_resultado_secante(cursor, resultado_id, lista_iteraciones)
        elif metodo_lower in ('müller', 'muller'):
            guardar_resultado_muller(cursor, resultado_id, lista_iteraciones)
        else:
            # código para otros métodos o genérico

            print("[guardar_resultado_completo] Método no reconocido, guardando iteraciones genéricas")
            for i, iteracion in enumerate(lista_iteraciones, start=1):
                if isinstance(iteracion, str):
                    iteracion = json.loads(iteracion)
                x0_val = iteracion.get('x0', None)
                x1_val = iteracion.get('x1', None)
                x2_val = iteracion.get('x2', None)
                fX0_val = iteracion.get('fX0', None)
                fX1_val = iteracion.get('fX1', None)
                fX2_val = iteracion.get('fX2', None)
                error_val = iteracion.get('Error', 0)
                insertar_iteracion(cursor, resultado_id, i, error_val, x0_val, x1_val, x2_val, fX0_val, fX1_val, fX2_val)

        connection.commit()
        print("[guardar_resultado_completo] Guardado exitoso y commit realizado")
        cursor.close()
        connection.close()
        return resultado_id

    except Exception as e:
        print(f"[guardar_resultado_completo] Error inesperado: {e}")
        print(traceback.format_exc())
        if 'connection' in locals():
            connection.rollback()
            connection.close()
        return None
