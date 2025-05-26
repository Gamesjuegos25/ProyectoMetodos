from src.conexion_sqlS import conexiondb
from datetime import datetime
import traceback
import io
import matplotlib.pyplot as plt
import sympy as sp
import numpy as np
import pyodbc
import unicodedata

# Mapeo de métodos a IDs según tu tabla en la base de datos
mapa_metodos = {
    'newton': 1,       # Newton-Raphson
    'secante': 2,
    'gauss': 3,
    'muller': 4,       # SIN tilde, coincidirá con "Müller" gracias a normalización
}

def normalizar_texto(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()

def crear_grafica(funcion_str, raiz):
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
    return buf.read()

def guardar_resultado_metodo(metodo_nombre, usuario, funcion, x0, lista_iteraciones, resultado, error_relativo, grafica_bytes=None, x1=None, x2=None):
    try:
        iteraciones = len(lista_iteraciones)
        if grafica_bytes is None:
            grafica_bytes = crear_grafica(funcion, resultado)

        error_relativo = float(error_relativo)

        metodo_nombre_normalizado = normalizar_texto(metodo_nombre)
        metodo_id = mapa_metodos.get(metodo_nombre_normalizado)
        if metodo_id is None:
            raise ValueError(f"Método desconocido: {metodo_nombre}")

        connection = conexiondb()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO ResultadosMetodos (
                MetodoId, NombreUsuario, Funcion, X0, X1, X2, 
                Iteraciones, Resultado, ErrorRelativo, Grafica
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metodo_id, usuario, funcion, x0, x1, x2,
            iteraciones, resultado, error_relativo, pyodbc.Binary(grafica_bytes)
        ))

        connection.commit()
        cursor.execute("SELECT @@IDENTITY")
        resultado_id = cursor.fetchone()[0]

        connection.close()
        return resultado_id

    except Exception as e:
        print(f"[Guardar Resultado] Error inesperado: {e}")
        print(traceback.format_exc())
        return None

def guardar_iteraciones_detalle(resultado_id, lista_iteraciones):
    try:
        connection = conexiondb()
        cursor = connection.cursor()

        # Tomar solo las últimas 4 iteraciones (si hay menos de 4, toma todas)
        ultimas_iteraciones = lista_iteraciones[-4:]

        offset = len(lista_iteraciones) - len(ultimas_iteraciones)
        for i, iteracion in enumerate(ultimas_iteraciones, start=offset + 1):

            valor = iteracion.get('x') or iteracion.get('x_r') or iteracion.get('x1') or 0
            error = iteracion.get('Error', 0)

            cursor.execute("""
                INSERT INTO IteracionesDetalle (
                    ResultadoId, NumeroIteracion, Valor, ErrorRelativo
                ) VALUES (?, ?, ?, ?)
            """, (resultado_id, i, valor, error))

        connection.commit()
        connection.close()
        return True

    except Exception as e:
        print(f"[Guardar Iteraciones] Error: {e}")
        print(traceback.format_exc())
        return False
