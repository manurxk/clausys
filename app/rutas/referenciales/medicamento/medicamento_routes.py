from flask import Blueprint, render_template

medmod = Blueprint('medicamento', __name__, template_folder='templates')

@medmod.route('/medicamento-index')
def medicamentoIndex():
    return render_template('medicamento-index.html')
