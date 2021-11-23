#Importar bibliotecas
from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

#Criar auth
auth = Blueprint("auth", __name__)

#Criar route para login
@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logado com sucesso!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Senha errada.', category='error')
        else:
            flash('Email não existe.', category='error')

    return render_template("login.html", user=current_user)

#Criar route para sign-up
@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email já está em uso.', category='error')
        elif username_exists:
            flash('Usuário já está em uso.', category='error')
        elif password1 != password2:
            flash('Senha não confere!', category='error')
        elif len(username) < 2:
            flash('Usuário muito curto.', category='error')
        elif len(password1) < 6:
            flash('Senha muito curta.', category='error')
        elif len(email) < 4:
            flash("Email inválido.", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Usuário criado!')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)

#Criar route para logout
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))
