from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user_model import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Aciona o método de busca da Classe
        if User.buscar_por_username(username):
            flash("Este nome de usuário já está em uso.", "error")
            return redirect(url_for('auth.register'))

        # Instancia o objeto, manipula e manda salvar no banco (Active Record)
        novo_usuario = User(username=username)
        novo_usuario.set_password(password)
        novo_usuario.salvar()

        flash("Cadastro realizado com sucesso! Faça o login.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home.welcome'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        usuario = User.buscar_por_username(username)

        if usuario and usuario.verify_password(password):
            session['user_id'] = usuario.id
            session['username'] = usuario.username
            return redirect(url_for('home.welcome'))
        else:
            flash("Usuário ou senha inválidos.", "error")

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))