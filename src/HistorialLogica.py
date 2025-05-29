from src.conexion_sqlS import conexiondb

def obtener_historial_usuario(username, metodo='', fecha=''):
    resultados = []

    connection = None
    cursor = None

    try:
        connection = conexiondb()
        cursor = connection.cursor()

        query = """
            SELECT r.ResultadoId, r.MetodoId, m.Nombre, r.NombreUsuario, r.Funcion, r.Resultado, r.Iteraciones, r.Grafica, r.Fecha
            FROM ResultadosMetodos r
            LEFT JOIN Metodos m ON r.MetodoId = m.MetodoId
            WHERE r.NombreUsuario = ?
        """
        params = [username]

        if metodo:
            query += " AND m.Nombre = ?"
            params.append(metodo)

        if fecha:
            query += " AND CAST(r.Fecha AS DATE) = ?"
            params.append(fecha)

        query += " ORDER BY r.Fecha DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        for row in rows:
            grafica = row[7]
            tiene_grafica = bool(grafica) and len(grafica) > 0

            fecha_str = row[8].strftime('%Y-%m-%d') if row[8] else ''

            resultados.append({
                'ResultadoId': row[0],
                'metodo': row[2],         # Nombre del método
                'funcion': row[4],
                'resultado': row[5],
                'iteraciones': row[6],
                'tiene_grafica': tiene_grafica,
                'fecha': fecha_str,
            })

    except Exception as e:
        print(f'Error obteniendo historial: {e}')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return resultados
