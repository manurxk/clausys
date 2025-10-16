from flask import Blueprint, render_template

sintmod = Blueprint('sintoma', __name__, template_folder='templates')

@sintmod.route('/sintoma-index')
def sintomaIndex():
    return render_template('sintoma-index.html')
