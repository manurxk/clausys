from flask import Flask

app = Flask(__name__)

# importar referenciales
from app.rutas.referenciales.ciudad.ciudad_routes import ciumod

# registrar referenciales
modulo0 = '/referenciales'
app.register_blueprint(ciumod, url_prefix=f'{modulo0}/ciudad')

from app.rutas.referenciales.ciudad.ciudad_api import ciuapi
from app.rutas.gestionar_compras.registrar_pedido_compras.registrar_pedido_compras_api \
    import pdcapi

# APIS v1
version1 = '/api/v1'
app.register_blueprint(ciuapi, url_prefix=version1)

# Gestionar compras
modulo1 = '/gestionar-compras'
app.register_blueprint(pdcapi, url_prefix=f'{version1}/{modulo1}/registrar-pedido-compras')