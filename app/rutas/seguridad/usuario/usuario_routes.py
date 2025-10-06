from flask import Blueprint, render_template

usumod = Blueprint('usuario', __name__, template_folder='templates')

@usumod.route('/usuario-index')
def usuarioIndex():
    return render_template('usuario-index.html')