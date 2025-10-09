from flask import Blueprint, render_template

consmod = Blueprint('consultorio', __name__, template_folder='templates')

@consmod.route('/consultorio-index')
def consultorioIndex():
    return render_template('consultorio-index.html')
