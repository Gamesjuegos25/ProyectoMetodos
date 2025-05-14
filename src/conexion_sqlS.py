import pyodbc

def conexiondb():
    
    try:
            connection = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=(localdb)\MSSQLLocalDB;DATABASE=ProyectoFMetodos;Trusted_Connection=yes;')
            print ("Conexion exitosa")
            return connection
    except Exception as ex:
            print(ex)       
            return None