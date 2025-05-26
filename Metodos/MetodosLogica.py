from sympy import symbols, sympify, lambdify, diff, sin, cos, tan, exp, log, sqrt
import numpy as np
import cmath

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
def mullerLogica(funcion_str, x0, x1, x2, max_iter=4000, tol=1e-6):
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
            f0, f1, f2 = f(x0), f(x1), f(x2)
            h0 = x1 - x0
            h1 = x2 - x1
            d0 = (f1 - f0) / h0
            d1 = (f2 - f1) / h1
            a = (d1 - d0) / (h1 + h0)

            if abs(a) < 1e-12:
                mensaje = f"Coeficiente cuadrático a ≈ 0 en iteración {i}, posible división por cero."
                return None, iteraciones, mensaje

            b = a * h1 + d1
            c = f2
            discriminante = b**2 - 4 * a * c
            sqrt_disc = cmath.sqrt(complex(discriminante))
            den1, den2 = b + sqrt_disc, b - sqrt_disc
            den = den1 if abs(den1) > abs(den2) else den2

            if abs(den) < 1e-12:
                mensaje = f"Denominador ≈ 0 en iteración {i}, división inválida."
                return None, iteraciones, mensaje

            x_r = x2 - (2 * c) / den

            if abs(x_r.imag) > 1e-6:
                mensaje = f"Raíz compleja detectada en iteración {i}. Método se detiene."
                return None, iteraciones, mensaje

            x_r = x_r.real
            error = abs((x_r - x2) / x_r) if x_r != 0 else abs(x_r - x2)

            iteraciones.append({
                'Iteración': i,
                'x0': round(float(x0), 10),
                'x1': round(float(x1), 10),
                'x2': round(float(x2), 10),
                'f(x2)': round(float(f2), 10),
                'x_r': round(float(x_r), 10),
                'Error': round(float(error), 10)
            })

            if error < tol:
                return round(float(x_r), 15), iteraciones, None

            x0, x1, x2 = x1, x2, x_r
        except Exception as e:
            mensaje = f"Error durante iteración {i}: {e}"
            return None, iteraciones, mensaje

    mensaje = "Advertencia: se alcanzó el máximo de iteraciones sin converger."
    return None, iteraciones, mensaje

# Espacio para la lógica del método de Gauss (a completar)
def gaussLogica():
    return
