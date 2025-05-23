from sympy import symbols, sympify, lambdify, diff, sin, cos, tan, exp, log, sqrt
import numpy as np
import cmath

# Diccionario común para parsing seguro de funciones
locals_dict = {'sin': sin, 'cos': cos, 'tan': tan, 'exp': exp, 'log': log, 'sqrt': sqrt}

def newton_raphsonLogica(funcion_str, x0, max_iter=4000, tol=1e-6):
    iteraciones = []
    try:
        x = symbols('x')
        funcion_str = funcion_str.replace('^', '**')
        funcion = sympify(funcion_str, locals=locals_dict)
        f = lambdify(x, funcion, modules=["numpy", "sympy"])
        df = lambdify(x, diff(funcion, x), modules=["numpy", "sympy"])
    except Exception:
        return None, []

    for i in range(1, max_iter + 1):
        try:
            fx = f(x0)
            dfx = df(x0)
            if dfx == 0:
                return None, iteraciones
            x1 = x0 - fx / dfx
            error = abs((x1 - x0) / x1) if x1 != 0 else abs(x1 - x0)

            iteraciones.append({
                'Iteración': i,
                'x': round(float(x0), 10),
                'f(x)': round(float(fx), 10),
                'Error': round(float(error), 10)
            })

            if error < tol:
                return round(float(x1), 15), iteraciones
            x0 = x1
        except Exception:
            return None, iteraciones
    return None, iteraciones


def secanteLogica(funcion_str, x0, x1, max_iter=4000, tol=1e-6):
    iteraciones = []
    try:
        x = symbols('x')
        funcion_str = funcion_str.replace('^', '**')
        funcion = sympify(funcion_str, locals=locals_dict)
        f = lambdify(x, funcion, modules=["numpy", "sympy"])
    except Exception:
        return None, []

    for i in range(1, max_iter + 1):
        try:
            f0 = f(x0)
            f1 = f(x1)
            if f1 - f0 == 0:
                return None, iteraciones
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
                return round(float(x2), 15), iteraciones
            x0, x1 = x1, x2
        except Exception:
            return None, iteraciones
    return None, iteraciones


def mullerLogica(funcion_str, x0, x1, x2, max_iter=4000, tol=1e-6):
    iteraciones = []
    try:
        x = symbols('x')
        funcion_str = funcion_str.replace('^', '**')
        funcion = sympify(funcion_str, locals=locals_dict)
        f = lambdify(x, funcion, modules=["numpy", "sympy"])
    except Exception as e:
        print("Error al interpretar la función:", e)
        return None, []

    for i in range(1, max_iter + 1):
        try:
            f0, f1, f2 = f(x0), f(x1), f(x2)
            h0 = x1 - x0
            h1 = x2 - x1
            d0 = (f1 - f0) / h0
            d1 = (f2 - f1) / h1
            a = (d1 - d0) / (h1 + h0)
            if a == 0:
                return None, iteraciones

            b = a * h1 + d1
            c = f2
            discriminante = b**2 - 4 * a * c
            sqrt_disc = cmath.sqrt(complex(discriminante))
            den1, den2 = b + sqrt_disc, b - sqrt_disc
            den = den1 if abs(den1) > abs(den2) else den2
            if den == 0:
                return None, iteraciones

            x_r = x2 - (2 * c) / den

            if abs(x_r.imag) < 1e-6:
                x_r = x_r.real
            else:
                return None, iteraciones

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
                return round(float(x_r), 15), iteraciones

            x0, x1, x2 = x1, x2, x_r
        except Exception as e:
            print("Error durante iteración:", e)
            return None, iteraciones

    return None, iteraciones
