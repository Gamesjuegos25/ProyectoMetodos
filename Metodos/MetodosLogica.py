from sympy import symbols, sympify, lambdify, diff
import math
import cmath  # Para raíces complejas en el método de Müller

# Método de Newton-Raphson
def newton_raphsonLogica(funcion_str, x0, max_iter=100, tol=1e-6):
    try:
        x = symbols('x')
        funcion = sympify(funcion_str)
        f = lambdify(x, funcion, 'math')
        df = lambdify(x, diff(funcion, x), 'math')
    except Exception as e:
        print(f"[Newton] Error al interpretar la función: {e}")
        return None, 0

    for i in range(max_iter):
        try:
            fx = f(x0)
            dfx = df(x0)
            if dfx == 0:
                print("[Newton] Derivada igual a cero. No se puede continuar.")
                return None, i
            x1 = x0 - fx / dfx
            if abs(x1 - x0) < tol:
                return round(x1, 15), i + 1
            x0 = x1
        except Exception as e:
            print(f"[Newton] Error en la iteración {i + 1}: {e}")
            return None, i
    return None, max_iter

# Método de la Secante
def secanteLogica(funcion_str, x0, x1, max_iter=100, tol=1e-6):
    try:
        x = symbols('x')
        funcion = sympify(funcion_str)
        f = lambdify(x, funcion, 'math')
    except Exception as e:
        print(f"[Secante] Error al interpretar la función: {e}")
        return None, 0

    for i in range(max_iter):
        try:
            f0 = f(x0)
            f1 = f(x1)
            if f1 - f0 == 0:
                print("[Secante] División por cero detectada.")
                return None, i
            x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
            if abs(x2 - x1) < tol:
                return round(x2, 15), i + 1
            x0, x1 = x1, x2
        except Exception as e:
            print(f"[Secante] Error en la iteración {i + 1}: {e}")
            return None, i
    return None, max_iter

# Método de Müller
def mullerLogica(funcion_str, x0, x1, x2, max_iter=100, tol=1e-6):
    try:
        x = symbols('x')
        funcion = sympify(funcion_str)
        f = lambdify(x, funcion, 'math')
    except Exception as e:
        print(f"[Müller] Error al interpretar la función: {e}")
        return None, 0

    for i in range(max_iter):
        try:
            f0 = f(x0)
            f1 = f(x1)
            f2 = f(x2)

            h0 = x1 - x0
            h1 = x2 - x1

            d0 = (f1 - f0) / h0
            d1 = (f2 - f1) / h1

            a = (d1 - d0) / (h1 + h0)
            if a == 0:
                print("[Müller] Valor de a igual a cero. División indefinida.")
                return None, i

            b = a * h1 + d1
            c = f2

            discriminante = b**2 - 4*a*c
            sqrt_disc = cmath.sqrt(discriminante)

            den1 = b + sqrt_disc
            den2 = b - sqrt_disc

            den = den1 if abs(den1) > abs(den2) else den2

            if den == 0:
                print("[Müller] División por cero en denominador.")
                return None, i

            x_r = x2 - (2 * c) / den

            if abs(x_r - x2) < tol:
                return round(x_r.real, 15), i + 1

            x0, x1, x2 = x1, x2, x_r.real
        except Exception as e:
            print(f"[Müller] Error en la iteración {i + 1}: {e}")
            return None, i

    return None, max_iter

