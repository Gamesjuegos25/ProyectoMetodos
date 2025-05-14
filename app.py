from flask import Flask, render_template, request, redirect, url_for
from src.conexion_sqlS import conexiondb  # Importar la función de conexión

app = Flask(__name__)

# Ruta de login
@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Conectar a la base de datos usando la función importada
        connection = conexiondb()
        
        if connection:
            cursor = connection.cursor()
            
            # Modificar la consulta para usar los nombres de las columnas correctas
            cursor.execute("SELECT * FROM Usuarios WHERE NombreUsuario = ? AND Contrasena = ?", (username, password))
            user = cursor.fetchone()
            
            # Si se encuentra un usuario con esas credenciales
            if user:
                return '<h2>Login exitoso</h2>'
            else:
                error = 'Credenciales inválidas'
                
            # Cerrar la conexión
            connection.close()
        else:
            error = 'Error de conexión a la base de datos'
    
    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)
