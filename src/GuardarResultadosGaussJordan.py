from src.conexion_sqlS import conexiondb
import traceback
import pyodbc
import numpy as np


def guardar_resultado_gauss_jordan(usuario, matriz_original, soluciones):
    try:
        connection = conexiondb()
        cursor = connection.cursor()
        connection.autocommit = False

        # Obtener MetodoId
        cursor.execute("SELECT MetodoId FROM Metodos WHERE LOWER(Nombre) = ?", ('gauss-jordan',))
        fila = cursor.fetchone()
        if not fila:
            raise ValueError("Método 'gauss-jordan' no encontrado.")
        metodo_id = fila[0]

        # Preparar valores individuales
        valor_x = float(soluciones[0]) if len(soluciones) > 0 else None
        valor_y = float(soluciones[1]) if len(soluciones) > 1 else None
        valor_z = float(soluciones[2]) if len(soluciones) > 2 else None

        iteraciones = 1  # solo una "iteración" para Gauss-Jordan
        error_relativo = 0  # No aplica para este método

        # Insertar resultado principal
        cursor.execute("""
            INSERT INTO ResultadosMetodos (
                MetodoId, NombreUsuario, Funcion, X0, X1, X2,
                Iteraciones, Resultado, ErrorRelativo, Grafica,
                ValorX, ValorY, ValorZ
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metodo_id, usuario, "Sistema lineal", None, None, None,
            iteraciones, None, error_relativo, None,
            valor_x, valor_y, valor_z
        ))

        # Obtener ID del nuevo resultado
        cursor.execute("SELECT @@IDENTITY")
        resultado_id = cursor.fetchone()[0]

        # Guardar matriz original como iteración 0
        for i, fila in enumerate(matriz_original):
            # Asegura que cada fila tenga al menos 3 columnas
            fila_safe = list(fila) + [0] * (3 - len(fila))  # rellenar si faltan columnas
            cursor.execute("""
                INSERT INTO IteracionesDetalle (
                    ResultadoId, Iteracion, X0, X1, X2
                ) VALUES (?, ?, ?, ?, ?)
            """, (resultado_id, i + 1, *fila_safe[:3]))

        # Confirmar transacción
        connection.commit()
        cursor.close()
        connection.close()
        return resultado_id

    except Exception as e:
        print(f"[guardar_resultado_gauss_jordan] Error: {e}")
        print(traceback.format_exc())
        if 'connection' in locals():
            connection.rollback()
            connection.close()
        return None
