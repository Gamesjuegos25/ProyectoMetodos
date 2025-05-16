from src.conexion_sqlS import conexiondb
import traceback

def guardar_resultado_newton(usuario, funcion, x0, iteraciones, resultado):
    try:
        connection = conexiondb()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO ResultadosNewton (NombreUsuario, Funcion, X0, Iteraciones, Resultado) VALUES (?, ?, ?, ?, ?)",
            (usuario, funcion, x0, iteraciones, resultado)
        )
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"[Newton] Error: {e}")
        print(traceback.format_exc())
        return False

def guardar_resultado_secante(usuario, funcion, x0, x1, iteraciones, resultado):
    try:
        connection = conexiondb()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO ResultadosSecante (NombreUsuario, Funcion, X0, X1, Iteraciones, Resultado) VALUES (?, ?, ?, ?, ?, ?)",
            (usuario, funcion, x0, x1, iteraciones, resultado)
        )
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"[Secante] Error: {e}")
        print(traceback.format_exc())
        return False

def guardar_resultado_muller(usuario, funcion, x0, x1, x2, iteraciones, resultado):
    try:
        connection = conexiondb()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO ResultadosMuller (NombreUsuario, Funcion, X0, X1, X2, Iteraciones, Resultado) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (usuario, funcion, x0, x1, x2, iteraciones, resultado)
        )
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"[Müller] Error: {e}")
        print(traceback.format_exc())
        return False
