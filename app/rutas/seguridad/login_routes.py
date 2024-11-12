from flask import Blueprint, render_template, session, \
    request, redirect, url_for, flash, current_app as app

logmod = Blueprint('login', __name__, template_folder='templates')

@logmod.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # hacer la validacion contra la bd
        usuario_nombre = request.form['usuario_nombre']
        usuario_clave = request.form['usuario_clave']
        if usuario_nombre == 'pepito' and usuario_clave == '123':
            # crear la sesión
            session.clear() # limpiar cualquier sesión previa
            session.permanent = True
            session['usuario_nombre'] = request.form['usuario_nombre']
            session['rol'] = 'contabilidad'
            return redirect(url_for('login.inicio'))
        else:
            flash('Error de log in, no existe este usuario', 'warning')
            return redirect(url_for('login.login'))
    elif request.method == 'GET':
        return render_template('login.html')

@logmod.route('/logout')
def logout():
    session.clear() # limpiar cualquier sesión previa
    flash('Sesion cerrada', 'warning')
    return redirect(url_for('login.login'))

@logmod.route('/')
def inicio():
    if 'usuario_nombre' in session:
        return render_template('inicio.html')
    else:
        return redirect(url_for('login.login'))