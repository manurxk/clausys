from flask import Blueprint, render_template

tipo_estudio_mod = Blueprint('tipo_estudio', __name__, template_folder='templates')

@tipo_estudio_mod.route('/tipo-estudio-index')
def tipoEstudioIndex():
    return render_template('estudio-index.html')
