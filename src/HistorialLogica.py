from src.conexion_sqlS import conexiondb

def obtener_historial_usuario(username, metodo='', fecha=''):
    resultados = []

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
            query += " AND CONVERT(date, r.Fecha) = ?"
            params.append(fecha)

        query += " ORDER BY r.Fecha DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        for row in rows:
            grafica = row[7]
            tiene_grafica = bool(grafica) and len(grafica) > 0

            resultados.append({
                'ResultadoId': row[0],
                'metodoId': row[1],
                'metodo': row[2],      
                'usuario': row[3],
                'funcion': row[4],
                'resultado': row[5],
                'iteraciones': row[6],
                'tiene_grafica': tiene_grafica,
                'fecha': row[8],
            })

    except Exception as e:
        print(f'Error obteniendo historial: {e}')
    finally:
        connection.close()

    return resultados
