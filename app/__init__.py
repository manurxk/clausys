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



# APIS v1
from app.rutas.referenciales.ciudad.ciudad_api import ciuapi


apiversion1 = '/api/v1'
app.register_blueprint(ciuapi, url_prefix=apiversion1)





# importar referenciales
from app.rutas.referenciales.especialidad.especialidad_routes import espmod

# registrar referenciales
modulo0 = '/referenciales'
app.register_blueprint(espmod, url_prefix=f'{modulo0}/especialidad')


# APIS v1
from app.rutas.referenciales.especialidad.especialidad_api import espapi

apiversion1 = '/api/v1'
app.register_blueprint(espapi, url_prefix=apiversion1)





# importar referenciales
from app.rutas.referenciales.genero.genero_routes import genmod

# registrar referenciales
modulo0 = '/referenciales'
app.register_blueprint(genmod, url_prefix=f'{modulo0}/genero')


# APIS v1
from app.rutas.referenciales.genero.genero_api import genapi

apiversion1 = '/api/v1'
app.register_blueprint(genapi, url_prefix=apiversion1)




# importar referenciales
from app.rutas.referenciales.estado_civil.estado_civil_routes import ecivmod

# registrar referenciales
modulo0 = '/referenciales'
app.register_blueprint(ecivmod, url_prefix=f'{modulo0}/estado-civil')


# APIS v1
from app.rutas.referenciales.estado_civil.estado_civil_api import ecapi

apiversion1 = '/api/v1'
app.register_blueprint(ecapi, url_prefix=apiversion1)



# importar referenciales
from app.rutas.referenciales.nivel_instruccion.nivel_instruccion_routes import nivmod

# registrar referenciales
modulo0 = '/referenciales'
app.register_blueprint(nivmod, url_prefix=f'{modulo0}/nivel-instruccion')


# APIS v1
from app.rutas.referenciales.nivel_instruccion.nivel_instruccion_api import nivapi

apiversion1 = '/api/v1'
app.register_blueprint(nivapi, url_prefix=apiversion1)



# importar referenciales
from app.rutas.referenciales.ocupacion.profesion_routes import profmod

# registrar referenciales
modulo0 = '/referenciales'
app.register_blueprint(profmod, url_prefix=f'{modulo0}/profesion')

# APIS v1
from app.rutas.referenciales.ocupacion.profesion_api import profapi

apiversion1 = '/api/v1'
app.register_blueprint(profapi, url_prefix=apiversion1)



# importar referenciales
from app.rutas.referenciales.cargo.cargo_routes import cargomod

# registrar referenciales
modulo0 = '/referenciales'
app.register_blueprint(cargomod, url_prefix=f'{modulo0}/cargo')

# APIS v1
from app.rutas.referenciales.cargo.cargo_api import cargoapi

apiversion1 = '/api/v1'
app.register_blueprint(cargoapi, url_prefix=apiversion1)


# importar referenciales
from app.rutas.referenciales.grupo.grupo_routes import grupomod

# registrar referenciales
modulo0 = '/referenciales'
app.register_blueprint(grupomod, url_prefix=f'{modulo0}/grupo')

# APIS v1
from app.rutas.referenciales.grupo.grupo_api import grupoapi

apiversion1 = '/api/v1'
app.register_blueprint(grupoapi, url_prefix=apiversion1)



# importar referenciales
from app.rutas.referenciales.modulo.modulo_routes import modmod

# registrar referenciales
modulo0 = '/referenciales'
app.register_blueprint(modmod, url_prefix=f'{modulo0}/modulo')

# APIS v1
from app.rutas.referenciales.modulo.modulo_api import modapi

apiversion1 = '/api/v1'
app.register_blueprint(modapi, url_prefix=apiversion1)




# importar referenciales
from app.rutas.gestionar_personas.paciente.paciente_routes import pacientemod

# registrar referenciales
modulo1 = '/modulos'
app.register_blueprint(pacientemod, url_prefix=f'{modulo1}/paciente')

# APIS v1
from app.rutas.gestionar_personas.paciente.paciente_api import pacienteapi

apiversion1 = '/api/v1'
app.register_blueprint(pacienteapi, url_prefix=apiversion1)


# Después de registrar el blueprint
for rule in app.url_map.iter_rules():
    if 'pacientes' in str(rule):
        print(f"{rule.rule} --> {rule.methods} --> {rule.endpoint}")





        # importar referenciales
from app.rutas.gestionar_personas.funcionario.funcionario_routes import funcionariomod

# registrar referenciales
modulo1 = '/modulos'
app.register_blueprint(funcionariomod, url_prefix=f'{modulo1}/funcionario')

# APIS v1
from app.rutas.gestionar_personas.funcionario.funcionario_api import funcionarioapi

apiversion1 = '/api/v1'
app.register_blueprint(funcionarioapi, url_prefix=apiversion1)



# Registrar módulo de usuarios
from app.rutas.seguridad.usuario.usuario_routes import usumod

modulo1 = '/modulos'
app.register_blueprint(usumod, url_prefix=f'{modulo1}/usuario')

# API de usuarios
from app.rutas.seguridad.usuario.usuario_api import usuarioapi

apiversion1 = '/api/v1'
app.register_blueprint(usuarioapi, url_prefix=apiversion1)