from datetime import timedelta
from flask import Flask
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# creamos el token
csrf = CSRFProtect()
csrf.init_app(app)

# inicializar el secret key
app.secret_key = b'_5#y2L"F6Q7z\n\xec]/'

# Establecer duración de la sesión, 15 minutos
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

# importar modulo de seguridad
from app.rutas.seguridad.login_routes import logmod
app.register_blueprint(logmod)

# importar referenciales
from app.rutas.referenciales.ciudad.ciudad_routes import ciumod

# registrar referenciales
modulo0 = '/referenciales'
app.register_blueprint(ciumod, url_prefix=f'{modulo0}/ciudad')

# importar gestionar compras
from app.rutas.gestionar_compras.registrar_pedido_compras.registrar_pedidos_compras_routes \
    import pdcmod

# registro de modulos - gestionar compras
modulo1 = '/gestionar-compras'
app.register_blueprint(pdcmod, url_prefix=f'{modulo1}/registrar-pedido-compras')

# APIS v1
from app.rutas.referenciales.ciudad.ciudad_api import ciuapi
from app.rutas.referenciales.sucursal.sucursal_api import sucapi
from app.rutas.gestionar_compras.registrar_pedido_compras.registrar_pedido_compras_api \
    import pdcapi

apiversion1 = '/api/v1'
app.register_blueprint(ciuapi, url_prefix=apiversion1)
app.register_blueprint(sucapi, url_prefix=apiversion1)

# Gestionar compras API
app.register_blueprint(pdcapi, url_prefix=f'{apiversion1}/{modulo1}/registrar-pedido-compras')