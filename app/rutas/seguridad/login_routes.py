from flask import Blueprint, render_template, session, \
    request, redirect, url_for, flash, current_app as app
from werkzeug.security import check_password_hash
from app.dao.referenciales.usuario.login_dao import LoginDao

logmod = Blueprint('login', __name__, template_folder='templates')


@logmod.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # datos del form
        usuario_nombre = request.form['usuario_nombre']
        usuario_clave = request.form['usuario_clave']

        # buscar usuario en la BD
        login_dao = LoginDao()
        usuario_encontrado = login_dao.buscarUsuario(usuario_nombre)

        if usuario_encontrado and 'usu_nick' in usuario_encontrado:
            password_hash_del_usuario = usuario_encontrado['usu_clave']

            if check_password_hash(pwhash=password_hash_del_usuario,
                                   password=usuario_clave):
                # login correcto → crear sesión
                session.clear()
                session.permanent = True
                session['id_usuario'] = usuario_encontrado['id_usuario']
                session['usu_nick'] = usuario_encontrado['usu_nick']
                session['nombre_persona'] = usuario_encontrado['nombre_persona']
                session['grupo'] = usuario_encontrado['grupo']

                return redirect(url_for('login.inicio'))
            else:
                flash('Contraseña incorrecta', 'danger')
                return redirect(url_for('login.login'))
        else:
            flash('Usuario no encontrado', 'warning')
            return redirect(url_for('login.login'))

    # si es GET
    return render_template('login.html')


@logmod.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login.login'))


@logmod.route('/')
def inicio():
    if 'usu_nick' in session:
        return render_template('inicio.html',
                               usuario=session.get('nombre_persona'),
                               grupo=session.get('grupo'))
    else:
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login.login'))
