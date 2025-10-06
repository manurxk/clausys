from flask import Blueprint, render_template

modmod = Blueprint('modulo', __name__, template_folder='templates')

@modmod.route('/modulo-index')
def moduloIndex():
    return render_template('modulo-index.html')
