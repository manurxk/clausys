from flask import Blueprint, render_template

tipo_procedimiento_mod = Blueprint('tipo_procedimiento', __name__, template_folder='templates')

@tipo_procedimiento_mod.route('/tipo-procedimiento-index')
def tipoProcedimientoIndex():
    return render_template('procedimiento-index.html')
