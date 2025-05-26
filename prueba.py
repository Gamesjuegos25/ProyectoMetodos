import math

def newton_simple(f, df, x0, tol=1e-6, max_iter=50):
    xi = x0
    for i in range(max_iter):
        try:
            f_val = f(xi)
            df_val = df(xi)

            if abs(df_val) < 1e-12:
                return None, f"Derivada casi cero en iteración {i+1}, no se puede continuar."

            xi_next = xi - f_val / df_val

            if abs(xi_next - xi) < tol:
                return xi_next, None

            xi = xi_next
        except Exception as e:
            return None, f"Error numérico en iteración {i+1}: {str(e)}"

    return None, "No convergió en el número máximo de iteraciones."


def f1(x):
    return math.cos(x) - x

def df1(x):
    return -math.sin(x) - 1


def f2(x):
    return x**2 + 1

def df2(x):
    return 2*x


if __name__ == "__main__":
    raiz, error = newton_simple(f1, df1, 0.5)
    if error:
        print("Error test 1:", error)
    else:
        print("Raíz test 1 encontrada:", raiz)

    raiz, error = newton_simple(f2, df2, 1)
    if error:
        print("Error test 2:", error)
    else:
        print("Raíz test 2 encontrada:", raiz)
