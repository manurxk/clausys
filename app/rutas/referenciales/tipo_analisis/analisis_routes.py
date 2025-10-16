from flask import Blueprint, render_template

tipoanalisismod = Blueprint('tipo_analisis', __name__, template_folder='templates')

@tipoanalisismod.route('/tipo-analisis-index')
def tipoAnalisisIndex():
    return render_template('analisis-index.html')
