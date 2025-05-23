from src.conexion_sqlS import conexiondb

from src.conexion_sqlS import conexiondb

def obtener_historial_usuario(username, metodo='', fecha=''):
    connection = conexiondb()
    resultados = []

    try:
        cursor = connection.cursor()
        query = """
            SELECT ResultadoId, Metodo, NombreUsuario, Funcion, Resultado, Iteraciones, Grafica, Fecha
            FROM ResultadosMetodos
            WHERE NombreUsuario = ?
        """
        params = [username]

        if metodo:
            query += " AND Metodo = ?"
            params.append(metodo)

        if fecha:
            query += " AND CONVERT(date, Fecha) = ?"
            params.append(fecha)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        for row in rows:
            tiene_grafica = row[6] is not None and len(row[6]) > 0  # Grafica
            resultados.append({
                'ResultadoId': row[0],
                'metodo': row[1],
                'usuario': row[2],
                'funcion': row[3],
                'resultado': row[4],
                'iteraciones': row[5],
                'tiene_grafica': tiene_grafica,
                'fecha': row[7],
            })
    except Exception as e:
        print(f'Error obteniendo historial: {e}')
    finally:
        connection.close()

    return resultados

