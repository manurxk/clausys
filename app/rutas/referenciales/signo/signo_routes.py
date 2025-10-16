from flask import Blueprint, render_template

signomod = Blueprint('signo', __name__, template_folder='templates')

@signomod.route('/signo-index')
def signoIndex():
    return render_template('signo-index.html')
