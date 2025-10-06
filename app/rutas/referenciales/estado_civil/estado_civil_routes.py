from flask import Blueprint, render_template

ecivmod = Blueprint('estado_civil', __name__, template_folder='templates')

@ecivmod.route('/estado-civil-index')
def estadoCivilIndex():
    return render_template('estado_civil-index.html')
