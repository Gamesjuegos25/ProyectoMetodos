from src.conexion_sqlS import conexiondb

def obtener_historial_usuario(username, metodo='', fecha=''):
    connection = conexiondb()
    resultados = []

    tablas = {
        'Newton': 'ResultadosNewton',
        'Secante': 'ResultadosSecante',
        'Müller': 'ResultadosMuller'
    }

    try:
        cursor = connection.cursor()
        for nombre_metodo, tabla in tablas.items():
            if metodo and metodo != nombre_metodo:
                continue
            
            query = f"""
                SELECT ResultadoId, NombreUsuario, Funcion, Resultado, Iteraciones, Grafica, Fecha
                FROM {tabla}
                WHERE NombreUsuario = ?
            """
            params = [username]

            if fecha:
                query += " AND CONVERT(date, Fecha) = ?"
                params.append(fecha)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            for row in rows:
                tiene_grafica = row[5] is not None and len(row[5]) > 0  # row[5] es Grafica
                resultados.append({
                    'ResultadoId': row[0],
                    'metodo': nombre_metodo,
                    'usuario': row[1],
                    'funcion': row[2],
                    'resultado': row[3],
                    'iteraciones': row[4],
                    'tiene_grafica': tiene_grafica,
                    'fecha': row[6],
                })
    except Exception as e:
        print(f'Error obteniendo historial: {e}')
    finally:
        connection.close()

    return resultados
