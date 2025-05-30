import pyodbc

def conexiondb():
    try:
        connection = pyodbc.connect(
            r"DRIVER={ODBC Driver 17 for SQL Server};"
            r"SERVER=DESKTOP-28R16OM\SQLEXPRESS;"
            r"DATABASE=ProyectoFMetodos;"
            r"Trusted_Connection=yes;"
        )
        print("Conexión exitosa")
        return connection
    except Exception as ex:
        print("Error al conectar:", ex)
        return None

conexiondb()
