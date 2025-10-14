from flask import Blueprint, render_template

citamod = Blueprint('cita', __name__, template_folder='templates')

@citamod.route('/cita-index')
def citaIndex():
    return render_template('cita-index.html')
