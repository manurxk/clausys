from flask import Blueprint, render_template

profmod = Blueprint('profesion', __name__, template_folder='templates')

@profmod.route('/profesion-index')
def profesionIndex():
    return render_template('profesion-index.html')
