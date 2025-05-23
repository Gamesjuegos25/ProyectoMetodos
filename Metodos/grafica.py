import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

def evaluar_funcion_en_rango(funcion_expr, x_min, x_max, puntos=400):
    x = sp.symbols('x')
    funcion_lambda = sp.lambdify(x, funcion_expr, modules=["numpy", "sympy"])

    x_vals = np.linspace(x_min, x_max, puntos)
    try:
        y_vals = funcion_lambda(x_vals)
        y_vals = np.array(y_vals, dtype=np.complex128)

        # Si hay valores complejos, tomar la parte real y avisar
        if np.any(np.iscomplex(y_vals)):
            print("Advertencia: valores complejos encontrados, usando solo la parte real.")
            y_vals = np.real(y_vals)

        # Reemplazar valores demasiado grandes por NaN para evitar distorsión en la gráfica
        y_vals = np.where(np.abs(y_vals) > 1e6, np.nan, y_vals)
        

    except Exception as e:
        print(f"Error al evaluar la función: {e}")
        return None, None

    return x_vals, y_vals

def graficar_funcion(funcion_expr, x_min, x_max):
    x_vals, y_vals = evaluar_funcion_en_rango(funcion_expr, x_min, x_max)
    if x_vals is None or y_vals is None:
        print("No se puede graficar debido a error en la evaluación de la función.")
        return

    plt.figure(figsize=(8,5))
    plt.plot(x_vals, y_vals, label=f"f(x) = {sp.pretty(funcion_expr)}", color='blue')
    plt.axhline(0, color='gray', lw=0.8)
    plt.axvline(0, color='gray', lw=0.8)
    plt.title("Gráfica de la función")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.grid(True)
    plt.legend()

    y_valid = y_vals[~np.isnan(y_vals)]
    if len(y_valid) > 0:
        y_min, y_max = np.min(y_valid), np.max(y_valid)
        margen = 0.1 * (y_max - y_min) if y_max != y_min else 1
        plt.ylim(y_min - margen, y_max + margen)
    else:
        plt.ylim(-1, 1)

    plt.tight_layout()
    plt.show()
    
    
def graficar_funcion_y_iteraciones(funcion_expr, aproximaciones):
    """
    Grafica la función y las aproximaciones (iteraciones) del método numérico
    como puntos rojos sobre la curva.
    """
    if not aproximaciones:
        print("No hay aproximaciones para graficar.")
        return

    # Rango dinámico basado en aproximaciones para que se vea todo bien
    min_x = min(aproximaciones) - 1
    max_x = max(aproximaciones) + 1

    # Evaluar la función en ese rango
    x_vals, y_vals = evaluar_funcion_en_rango(funcion_expr, min_x, max_x)
    if x_vals is None or y_vals is None:
        print("Error al evaluar función, no se puede graficar.")
        return

    plt.figure(figsize=(8,5))
    plt.plot(x_vals, y_vals, label=f"f(x) = {sp.pretty(funcion_expr)}", color='blue')

    # Evaluar función en los puntos de aproximación para graficar los puntos
    f_lambda = sp.lambdify(sp.symbols('x'), funcion_expr, modules=["numpy", "sympy"])
    y_aprox = f_lambda(np.array(aproximaciones))
    y_aprox = np.real_if_close(y_aprox)

    plt.scatter(aproximaciones, y_aprox, color='red', label='Aproximaciones', zorder=5)

    plt.axhline(0, color='gray', lw=0.8)
    plt.axvline(0, color='gray', lw=0.8)
    plt.title("Función y aproximaciones del método numérico")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.grid(True)
    plt.legend()

    y_valid = y_vals[~np.isnan(y_vals)]
    if len(y_valid) > 0:
        y_min, y_max = np.min(y_valid), np.max(y_valid)
        margen = 0.1 * (y_max - y_min) if y_max != y_min else 1
        plt.ylim(y_min - margen, y_max + margen)
    else:
        plt.ylim(-1, 1)

    plt.tight_layout()
    plt.show()
