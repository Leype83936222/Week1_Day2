from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from flask_wtf.file import FileField, FileAllowed
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from wtforms.fields import DateField
from datetime import datetime, date
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # ensure this exists
db = SQLAlchemy(app)

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    image_filename = db.Column(db.String(255))

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Register Form
class RegisterForm(FlaskForm):
    image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    name = StringField('Full Name', validators=[DataRequired()])
    birthday = DateField('Birthday', format='%Y-%m-%d', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    # REMOVED confirm_password
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')
        
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('Users/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            f = form.image.data
            filename = secure_filename(f.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            f.save(filepath)
            image_filename = filename

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            password=hashed_password,
            name=form.name.data,
            birthday=form.birthday.data,
            address=form.address.data,
            image_filename=image_filename
        )
        db.session.add(new_user)
        db.session.commit()
        return render_template('Users/register.html', form=RegisterForm(), registration_success=True)
    else:
        print(form.errors)

    return render_template('Users/register.html', form=form)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['user']).first()
    
    # Calculate age
    today = date.today()
    age = today.year - user.birthday.year - ((today.month, today.day) < (user.birthday.month, user.birthday.day))
    
    return render_template('Users/dashboard.html', user=user, age=age)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
