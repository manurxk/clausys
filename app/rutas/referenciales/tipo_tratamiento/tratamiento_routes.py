from flask import Blueprint, render_template

tipotratamientomod = Blueprint('tipo_tratamiento', __name__, template_folder='templates')

@tipotratamientomod.route('/tipo-tratamiento-index')
def tipoTratamientoIndex():
    return render_template('tratamiento-index.html')
