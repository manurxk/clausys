from flask import Blueprint, render_template

diagmod = Blueprint('diagnostico', __name__, template_folder='templates')

@diagmod.route('/diagnostico-index')
def diagnosticoIndex():
    return render_template('diagnostico-index.html')

