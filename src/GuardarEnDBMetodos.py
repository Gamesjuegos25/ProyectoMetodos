from src.conexion_sqlS import conexiondb
from datetime import datetime
import traceback
import io
import matplotlib.pyplot as plt
import sympy as sp
import numpy as np
import pyodbc


def guardar_resultado_metodo(metodo,usuario, funcion, x0, lista_iteraciones, resultado, error_relativo, grafica_bytes=None,x1=None,x2=None):

    try:
        iteraciones = len(lista_iteraciones)
        if grafica_bytes is None:
            
            grafica_bytes = crear_grafica(funcion, resultado)
            
        error_relativo_str = f"{float(error_relativo):.15f}"

        connection = conexiondb()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO ResultadosMetodos (Metodo,NombreUsuario, Funcion, X0,X1,X2, Iteraciones, Resultado, ErrorRelativo, Grafica) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (metodo,usuario, funcion, x0,x1,x2, iteraciones, resultado, error_relativo_str, pyodbc.Binary(grafica_bytes))
        )


        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"[Newton] Error inesperado al guardar: {e}")
        print(traceback.format_exc())
        return False


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
