import os
import pyodbc

def conexiondb():
    try:
        connection = pyodbc.connect(
            r"DRIVER={ODBC Driver 17 for SQL Server};"
            r"SERVER=(localdb)\MSSQLLocalDB;"
            r"DATABASE=ProyectoFMetodos2;"
            r"Trusted_Connection=yes;"
        )
        print("Conexion exitosa")
        return connection
    except Exception as ex:
        print(ex)
        return None

conexiondb()
