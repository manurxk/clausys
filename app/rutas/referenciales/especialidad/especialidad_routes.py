from flask import Blueprint, render_template

espmod = Blueprint('especialidad', __name__, template_folder='templates')

@espmod.route('/especialidad-index')
def especialidadIndex():
    return render_template('especialidad-index.html')
