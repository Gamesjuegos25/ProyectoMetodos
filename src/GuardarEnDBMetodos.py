from src.conexion_sqlS import conexiondb
from datetime import datetime
import traceback
import io
import matplotlib.pyplot as plt
import sympy as sp
import numpy as np

def guardar_resultado_newton(usuario, funcion, x0, lista_iteraciones, resultado, error_relativo,grafica_bytes=None):
    try:
        iteraciones = len(lista_iteraciones)
        grafica_bytes = crear_grafica(funcion, resultado)
     
 
        connection = conexiondb()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO ResultadosNewton (NombreUsuario, Funcion, X0, Iteraciones, Resultado, ErrorRelativo, Grafica) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (usuario, funcion, x0, iteraciones, resultado, error_relativo, grafica_bytes)
)

        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"[Newton] Error: {e}")
        print(traceback.format_exc())
        return False


def guardar_resultado_secante(usuario, funcion, x0, x1, lista_iteraciones, resultado, error_relativo,grafica_bytes=None):
    try:
        iteraciones = len(lista_iteraciones)
        grafica_bytes = crear_grafica(funcion, resultado)
        
        connection = conexiondb()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO ResultadosSecante (NombreUsuario, Funcion, X0, X1, Iteraciones, Resultado, ErrorRelativo, Grafica) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (usuario, funcion, x0, x1, iteraciones, resultado, error_relativo,grafica_bytes)
        )
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"[Secante] Error: {e}")
        print(traceback.format_exc())
        return False

def guardar_resultado_muller(usuario, funcion, x0, x1, x2, lista_iteraciones, resultado, error_relativo,grafica_bytes=None):
    try:
        iteraciones = len(lista_iteraciones)
        grafica_bytes = crear_grafica(funcion, resultado)
        
        connection = conexiondb()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO ResultadosMuller (NombreUsuario, Funcion, X0, X1, X2, Iteraciones, Resultado, ErrorRelativo, Grafica) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (usuario, funcion, x0, x1, x2, iteraciones, resultado, error_relativo,grafica_bytes)
        )
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"[Müller] Error: {e}")
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
