from flask import Blueprint, render_template

consultamod = Blueprint('registrarconsulta', __name__, template_folder='templates')

@consultamod.route('/consulta-index')
def consultaIndex():
    return render_template('registrarconsulta-index.html')