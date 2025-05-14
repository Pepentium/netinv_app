from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth.utils import load_user, create_user
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inventory.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(usr_name=username).first()
        
        if not user or not user.check_password(password):
            flash('🔐 Usuario o contraseña incorrectos', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        return redirect(url_for('inventory.dashboard'))
    
    return render_template('auth/login.html', show_sidebar=False)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(usr_name=username).first():
            flash('🔐 El usuario ya existe', 'error')
            return redirect(url_for('auth.register'))
        
        create_user(username, password)
        flash('🔐 Usuario registrado correctamente', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', show_sidebar=False)