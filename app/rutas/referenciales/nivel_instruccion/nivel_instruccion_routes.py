from flask import Blueprint, render_template

nivmod = Blueprint('nivel_instruccion', __name__, template_folder='templates')

@nivmod.route('/nivel-instruccion-index')
def nivelInstruccionIndex():
    return render_template('nivel_instruccion-index.html')
