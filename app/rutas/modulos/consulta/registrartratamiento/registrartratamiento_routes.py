from flask import Blueprint, render_template

tratamientomod = Blueprint('registrartratamiento', __name__, template_folder='templates')

@tratamientomod.route('/tratamiento-index')
def tratamientoIndex():
    return render_template('registrartratamiento-index.html')