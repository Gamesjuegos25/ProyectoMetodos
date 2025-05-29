from sympy import symbols, sympify, lambdify, diff, sin, cos, tan, exp, log, sqrt
import sympy as sp
import numpy as np
from src.conexion_sqlS import conexiondb
from datetime import datetime
import matplotlib.pyplot as plt



# Diccionario seguro de funciones matemáticas
locals_dict = {'sin': sin, 'cos': cos, 'tan': tan, 'exp': exp, 'log': log, 'sqrt': sqrt}

# Método de Newton-Raphson
def newton_raphsonLogica(funcion_str, x0, max_iter=4000, tol=1e-6):
    iteraciones = []
    mensaje = None

    try:
        x = symbols('x')
        funcion_str = funcion_str.replace('^', '**')
        funcion = sympify(funcion_str, locals=locals_dict)
        f = lambdify(x, funcion, modules=["numpy", "sympy"])
        df = lambdify(x, diff(funcion, x), modules=["numpy", "sympy"])
    except Exception as e:
        mensaje = f"Error al interpretar la función: {e}"
        return None, iteraciones, mensaje

    for i in range(1, max_iter + 1):
        try:
            fx = f(x0)
            dfx = df(x0)

            if abs(dfx) < 1e-8:
                mensaje = f"Derivada demasiado pequeña en iteración {i}, posible división por cero o divergencia."
                return None, iteraciones, mensaje

            x1 = x0 - fx / dfx
            error = abs((x1 - x0) / x1) if x1 != 0 else abs(x1 - x0)

            iteraciones.append({
                'Iteración': i,
                'x': round(float(x0), 10),
                'f(x)': round(float(fx), 10),
                'Error': round(float(error), 10)
            })

            if error < tol:
                return round(float(x1), 15), iteraciones, None

            x0 = x1
        except Exception as e:
            mensaje = f"Error en la iteración {i}: {e}"
            return None, iteraciones, mensaje

    mensaje = "Advertencia: se alcanzó el máximo de iteraciones sin converger."
    return None, iteraciones, mensaje

# Método de la Secante
def secanteLogica(funcion_str, x0, x1, max_iter=4000, tol=1e-6):
    iteraciones = []
    mensaje = None

    try:
        x = symbols('x')
        funcion_str = funcion_str.replace('^', '**')
        funcion = sympify(funcion_str, locals=locals_dict)
        f = lambdify(x, funcion, modules=["numpy", "sympy"])
    except Exception as e:
        mensaje = f"Error al interpretar la función: {e}"
        return None, [], mensaje

    for i in range(1, max_iter + 1):
        try:
            f0 = f(x0)
            f1 = f(x1)

            if abs(f1 - f0) < 1e-12:
                mensaje = f"Diferencia f(x1) - f(x0) demasiado pequeña en iteración {i}, posible división por cero."
                return None, iteraciones, mensaje

            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
            error = abs((x2 - x1) / x2) if x2 != 0 else abs(x2 - x1)

            iteraciones.append({
                'Iteración': i,
                'x0': round(float(x0), 10),
                'x1': round(float(x1), 10),
                'f(x0)': round(float(f0), 10),
                'f(x1)': round(float(f1), 10),
                'Error': round(float(error), 10)
            })

            if error < tol:
                return round(float(x2), 15), iteraciones, None

            x0, x1 = x1, x2
        except Exception as e:
            mensaje = f"Error durante iteración {i}: {e}"
            return None, iteraciones, mensaje

    mensaje = "Advertencia: se alcanzó el máximo de iteraciones sin converger."
    return None, iteraciones, mensaje

# Método de Müller
def mullerLogica(funcion_str, x0, x1, x2, tol=1e-10, max_iter=50):
    x = sp.symbols('x')
    funcion = sp.sympify(funcion_str)
    f_lambda = sp.lambdify(x, funcion, modules=["numpy"])

    iteraciones = []
    try:
        for i in range(1, max_iter + 1):
            f0 = f_lambda(x0)
            f1 = f_lambda(x1)
            f2 = f_lambda(x2)

            h0 = x1 - x0
            h1 = x2 - x1
            delta0 = (f1 - f0) / h0
            delta1 = (f2 - f1) / h1
            a = (delta1 - delta0) / (h1 + h0)
            b = a * h1 + delta1
            c = f2

            rad = np.lib.scimath.sqrt(b ** 2 - 4 * a * c)

            if abs(b + rad) > abs(b - rad):
                den = b + rad
            else:
                den = b - rad

            if den == 0:
                # Evitar división por cero
                return None, iteraciones, "Denominador cero en cálculo."

            dx_r = -2 * c / den
            x_r = x2 + dx_r
            error = abs(dx_r / x_r) if x_r != 0 else abs(dx_r)

            iteraciones.append({
                'Iteración': i,
                'x0': round(float(x0), 10),
                'x1': round(float(x1), 10),
                'x2': round(float(x2), 10),
                'fX0': round(float(f0), 10),
                'fX1': round(float(f1), 10),
                'fX2': round(float(f2), 10),
                'Error': round(float(error), 10)
            })

            if error < tol:
                return x_r, iteraciones, "Convergencia alcanzada"

            x0, x1, x2 = x1, x2, x_r

        return x_r, iteraciones, "Máximo de iteraciones alcanzado sin convergencia"
    except Exception as e:
        return None, iteraciones, f"Error en cálculo: {str(e)}"
# Método de Gauss-Jordan
def gauss_jordan_logica(matriz_aumentada):
    matriz = matriz_aumentada.astype(float)
    n = matriz.shape[0]

    for i in range(n):
        # Buscar el pivote máximo en la columna i para mejorar estabilidad numérica
        max_row = i + np.argmax(abs(matriz[i:, i]))
        if abs(matriz[max_row, i]) < 1e-12:
            return None, "El sistema no tiene solución única (pivote nulo)."

        if max_row != i:
            matriz[[i, max_row]] = matriz[[max_row, i]]

        matriz[i] = matriz[i] / matriz[i, i]

        for j in range(n):
            if j != i:
                matriz[j] = matriz[j] - matriz[j, i] * matriz[i]

    soluciones = matriz[:, -1]

    return soluciones, None

# Ejemplo de uso:
# sistema: 
# 2x + y - z = 8
# -3x - y + 2z = -11
# -2x + y + 2z = -3
matriz = np.array([
    [2, 1, -1, 8],
    [-3, -1, 2, -11],
    [-2, 1, 2, -3]
])

soluciones, mensaje = gauss_jordan_logica(matriz)
if mensaje:
    print("Error:", mensaje)
else:
    print("Soluciones:", soluciones)
