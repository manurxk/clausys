from flask import Blueprint, render_template

genmod = Blueprint('genero', __name__, template_folder='templates')

@genmod.route('/genero-index')
def generoIndex():
    return render_template('genero-index.html')
