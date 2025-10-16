from flask import Blueprint, render_template

consultamod = Blueprint('consulta', __name__, template_folder='templates')

@consultamod.route('/consulta-index')
def consultaIndex():
    """Vista de citas del día con opción de iniciar consulta"""
    return render_template('consulta-index.html')



