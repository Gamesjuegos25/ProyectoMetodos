from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Ruta de login
@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '1234':
            return '<h2>Login exitoso</h2>'
        else:
            error = 'Credenciales inválidas'
    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)
