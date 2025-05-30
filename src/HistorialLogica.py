from src.conexion_sqlS import conexiondb

def obtener_historial_usuario(username, metodo='', fecha=''):
    resultados = []

    connection = None
    cursor = None

    try:
        connection = conexiondb()
        cursor = connection.cursor()

        query = """
            SELECT r.ResultadoId, r.MetodoId, m.Nombre, r.NombreUsuario, r.Funcion,
                   r.Resultado, r.Iteraciones, r.Grafica, r.Fecha,
                   r.ValorX, r.ValorY, r.ValorZ
            FROM ResultadosMetodos r
            LEFT JOIN Metodos m ON r.MetodoId = m.MetodoId
            WHERE r.NombreUsuario = ?
        """
        params = [username]

        # Solo filtra por método si no es vacío ni "Todos"
        if metodo and metodo.lower() != 'todos':
            query += " AND m.Nombre = ?"
            params.append(metodo)

        if fecha:
            query += " AND CAST(r.Fecha AS DATE) = ?"
            params.append(fecha)

        query += " ORDER BY r.Fecha DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        for row in rows:
            metodo_nombre = row[2].lower()
            grafica = row[7]
            tiene_grafica = bool(grafica) and len(grafica) > 0
            fecha_str = row[8].strftime('%Y-%m-%d') if row[8] else ''

            # Mostrar resultado especial para gauss-jordan
            if metodo_nombre == 'gauss-jordan':
                resultado = f"X = {row[9]:.4f}, Y = {row[10]:.4f}, Z = {row[11]:.4f}"
            else:
                resultado = row[5]

            resultados.append({
                'ResultadoId': row[0],
                'metodo': row[2],
                'funcion': row[4],
                'resultado': resultado,
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
