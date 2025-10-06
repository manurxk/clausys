from flask import Blueprint, render_template

grupomod = Blueprint('grupo', __name__, template_folder='templates')

@grupomod.route('/grupo-index')
def grupoIndex():
    return render_template('grupo-index.html')
