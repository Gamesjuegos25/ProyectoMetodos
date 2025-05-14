from flask import Flask, render_template, request, redirect, url_for
from src.conexion_sqlS import conexiondb  #  función de conexión

app = Flask(__name__)

# Ruta de login
@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        

        connection = conexiondb()
        
        if connection:
            cursor = connection.cursor()
            
           
            cursor.execute("SELECT * FROM Usuarios WHERE NombreUsuario = ? AND Contrasena = ?", (username, password))
            user = cursor.fetchone()
            
          
            if user:
                return '<h2>Login exitoso</h2>'
            else:
                error = 'Credenciales inválidas'
                
     
            connection.close()
        else:
            error = 'Error de conexión a la base de datos'
    
    return render_template('login.html', error=error)

# Ruta de registro
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    error = ''
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = conexiondb()

        if connection:
            cursor = connection.cursor()

            # Verificar si el usuario ya existe
            cursor.execute("SELECT * FROM Usuarios WHERE NombreUsuario = ?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                error = 'El usuario ya existe.'
            else:
                # Insertar nuevo usuario
                cursor.execute("INSERT INTO Usuarios (NombreUsuario, Contrasena) VALUES (?, ?)", (username, password))
                connection.commit()
                connection.close()
                return redirect(url_for('login'))

            connection.close()
        else:
            error = 'Error de conexión a la base de datos'

    return render_template('registro.html', error=error)
if __name__ == '__main__':
    app.run(debug=True)
