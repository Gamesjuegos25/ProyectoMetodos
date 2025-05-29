from src.conexion_sqlS import conexiondb
from datetime import datetime
import traceback
import io
import matplotlib.pyplot as plt
import sympy as sp
import numpy as np
import pyodbc
import unicodedata
import json
from Metodos.MetodosLogica import mullerLogica

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



def guardar_resultado_completo(
    metodo_nombre, usuario, funcion, x0, lista_iteraciones, resultado, error_relativo,
    grafica_bytes=None, x1=None, x2=None, max_iteraciones=100
):
    try:
        if isinstance(lista_iteraciones, str):
            lista_iteraciones = json.loads(lista_iteraciones)
        
        if max_iteraciones is not None:
            lista_iteraciones = lista_iteraciones[:max_iteraciones]

        iteraciones = len(lista_iteraciones)
        if grafica_bytes is None:
            grafica_bytes = crear_grafica(funcion, resultado)
        error_relativo = float(error_relativo)

        connection = conexiondb()
        cursor = connection.cursor()
        connection.autocommit = False

        cursor.execute("SELECT MetodoId FROM Metodos WHERE LOWER(Nombre) = ?", (metodo_nombre.lower(),))
        fila = cursor.fetchone()
        if not fila:
            raise ValueError(f"Método '{metodo_nombre}' no encontrado en la base de datos.")
        metodo_id = fila[0]

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

        # Insertar la primera iteración con valores iniciales (sin error ni fX)
        cursor.execute("""
            INSERT INTO IteracionesDetalle (
                ResultadoId, Iteracion, ErrorRelativo, X0, X1, X2, fX0, fX1, fX2
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resultado_id,
            0,
            None,
            x0,
            x1,
            x2,
            None,
            None,
            None,
        ))

        # Insertar las iteraciones calculadas
        for i, iteracion in enumerate(lista_iteraciones, start=1):
            if isinstance(iteracion, str):
                iteracion = json.loads(iteracion)
            
            cursor.execute("""
                INSERT INTO IteracionesDetalle (
                    ResultadoId, Iteracion, ErrorRelativo, X0, X1, X2, fX0, fX1, fX2
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resultado_id,
                i,
                iteracion.get('Error', 0),
                iteracion.get('x0', None),
                iteracion.get('x1', None),
                iteracion.get('x2', None),
                iteracion.get('fX0', None),
                iteracion.get('fX1', None),
                iteracion.get('fX2', None),
            ))

        connection.commit()
        cursor.close()
        connection.close()
        return resultado_id

    except Exception as e:
        if 'connection' in locals():
            connection.rollback()
            connection.close()
        print(f"[Guardar Resultado Completo] Error inesperado: {e}")
        print(traceback.format_exc())
        return None


# Ejemplo de uso:
if __name__ == "__main__":
    funcion_str = "x**3 - 13*x - 12"
    x0, x1, x2 = 5.0, 6.0, 7.0
    usuario = "usuario_ejemplo"

    raiz, iteraciones, mensaje = mullerLogica(funcion_str, x0, x1, x2)

    if raiz is not None:
        resultado_id = guardar_resultado_completo(
            metodo_nombre='Müller',
            usuario=usuario,
            funcion=funcion_str,
            x0=x0,
            x1=x1,
            x2=x2,
            lista_iteraciones=iteraciones,
            resultado=raiz,
            error_relativo=iteraciones[-1]['Error'] if iteraciones else 0
        )
        print(f"Resultado guardado con ID: {resultado_id}")
    else:
        print(f"Error en cálculo: {mensaje}")
