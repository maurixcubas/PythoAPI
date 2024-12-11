from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = "secret_key"



#Configure SQL ALchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)  # Nombre
    last_name = db.Column(db.String(50), nullable=False)   # Apellido
    email = db.Column(db.String(100), nullable=False, unique=True)  # Email
    phone = db.Column(db.String(20), nullable=False)  # Número de Celular
    password_hash = db.Column(db.String(150), nullable=False)  # Contraseña

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


#Routes 
@app.route('/')
def home():
    if "username" in session:
        return "youre logged in"
    return "Hello to our APP please Log in"

#Login
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']  # Cambia a email
    password = request.form['password']
    
    # Busca al usuario por email
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session['username'] = email  # Cambia a email para la sesión
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('home'))  # Manejo de login incorrecto


#Register
@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']

    # Verifica si el usuario ya existe por email
    user = User.query.filter_by(email=email).first()
    if user:
        return redirect(url_for('home'))  # Puedes agregar un mensaje de error aquí

    # Crea un nuevo usuario
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    session['username'] = email  # Guarda la sesión del usuario
    return redirect(url_for('dashboard'))



#Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


#dashboard
@app.route('/dashboard')
def dashboard():
    if "username" in session:
        user = User.query.filter_by(email=session['username']).first()
        return f"Welcome {user.first_name} {user.last_name}! Your email is {user.email}."
    return redirect(url_for('home'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)