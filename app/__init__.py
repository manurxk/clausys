from datetime import timedelta
from flask import Flask
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

csrf = CSRFProtect()
csrf.init_app(app)

app.secret_key = b'_5#y2L"F6Q7z\n\xec]/'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

MODULO_REFERENCIALES = '/referenciales'
MODULO_GESTION = '/modulos'
API_V1 = '/api/v1'

from app.rutas.seguridad.login_routes import logmod
app.register_blueprint(logmod)

from app.rutas.referenciales.ciudad.ciudad_routes import ciumod
from app.rutas.referenciales.ciudad.ciudad_api import ciuapi
app.register_blueprint(ciumod, url_prefix=f'{MODULO_REFERENCIALES}/ciudad')
app.register_blueprint(ciuapi, url_prefix=API_V1)

from app.rutas.referenciales.especialidad.especialidad_routes import espmod
from app.rutas.referenciales.especialidad.especialidad_api import espapi
app.register_blueprint(espmod, url_prefix=f'{MODULO_REFERENCIALES}/especialidad')
app.register_blueprint(espapi, url_prefix=API_V1)

from app.rutas.referenciales.genero.genero_routes import genmod
from app.rutas.referenciales.genero.genero_api import genapi
app.register_blueprint(genmod, url_prefix=f'{MODULO_REFERENCIALES}/genero')
app.register_blueprint(genapi, url_prefix=API_V1)

from app.rutas.referenciales.estado_civil.estado_civil_routes import ecivmod
from app.rutas.referenciales.estado_civil.estado_civil_api import ecapi
app.register_blueprint(ecivmod, url_prefix=f'{MODULO_REFERENCIALES}/estado-civil')
app.register_blueprint(ecapi, url_prefix=API_V1)

from app.rutas.referenciales.nivel_instruccion.nivel_instruccion_routes import nivmod
from app.rutas.referenciales.nivel_instruccion.nivel_instruccion_api import nivapi
app.register_blueprint(nivmod, url_prefix=f'{MODULO_REFERENCIALES}/nivel-instruccion')
app.register_blueprint(nivapi, url_prefix=API_V1)

from app.rutas.referenciales.ocupacion.profesion_routes import profmod
from app.rutas.referenciales.ocupacion.profesion_api import profapi
app.register_blueprint(profmod, url_prefix=f'{MODULO_REFERENCIALES}/profesion')
app.register_blueprint(profapi, url_prefix=API_V1)

from app.rutas.referenciales.dia.dia_routes import diamod
from app.rutas.referenciales.dia.dia_api import diaapi
app.register_blueprint(diamod, url_prefix=f'{MODULO_REFERENCIALES}/dia')
app.register_blueprint(diaapi, url_prefix=API_V1)

from app.rutas.referenciales.consultorio.consultorio_routes import consmod
from app.rutas.referenciales.consultorio.consultorio_api import consapi
app.register_blueprint(consmod, url_prefix=f'{MODULO_REFERENCIALES}/consultorio')
app.register_blueprint(consapi, url_prefix=API_V1)

from app.rutas.referenciales.cargo.cargo_routes import cargomod
from app.rutas.referenciales.cargo.cargo_api import cargoapi
app.register_blueprint(cargomod, url_prefix=f'{MODULO_REFERENCIALES}/cargo')
app.register_blueprint(cargoapi, url_prefix=API_V1)

from app.rutas.referenciales.grupo.grupo_routes import grupomod
from app.rutas.referenciales.grupo.grupo_api import grupoapi
app.register_blueprint(grupomod, url_prefix=f'{MODULO_REFERENCIALES}/grupo')
app.register_blueprint(grupoapi, url_prefix=API_V1)

from app.rutas.referenciales.modulo.modulo_routes import modmod
from app.rutas.referenciales.modulo.modulo_api import modapi
app.register_blueprint(modmod, url_prefix=f'{MODULO_REFERENCIALES}/modulo')
app.register_blueprint(modapi, url_prefix=API_V1)

from app.rutas.gestionar_personas.paciente.paciente_routes import pacientemod
from app.rutas.gestionar_personas.paciente.paciente_api import pacienteapi
app.register_blueprint(pacientemod, url_prefix=f'{MODULO_GESTION}/paciente')
app.register_blueprint(pacienteapi, url_prefix=API_V1)

from app.rutas.gestionar_personas.funcionario.funcionario_routes import funcionariomod
from app.rutas.gestionar_personas.funcionario.funcionario_api import funcionarioapi
app.register_blueprint(funcionariomod, url_prefix=f'{MODULO_GESTION}/funcionario')
app.register_blueprint(funcionarioapi, url_prefix=API_V1)

from app.rutas.seguridad.usuario.usuario_routes import usumod
from app.rutas.seguridad.usuario.usuario_api import usuarioapi
app.register_blueprint(usumod, url_prefix=f'{MODULO_GESTION}/usuario')
app.register_blueprint(usuarioapi, url_prefix=API_V1)






from app.rutas.modulos.agenda_medica.agenda_medica_routes import agendamod
from app.rutas.modulos.agenda_medica.agenda_medica_api import agendaapi


# Agenda Médica - Routes (HTML) - Igual que especialidad
app.register_blueprint(agendamod, url_prefix='/agenda')

# Agenda Médica - API (Endpoints JSON) - Igual que especialidad  
app.register_blueprint(agendaapi, url_prefix='/api/v1')



# Citas - Routes (HTML)
from app.rutas.modulos.cita.cita_routes import citamod
app.register_blueprint(citamod, url_prefix='/cita')

# Citas - API (Endpoints JSON)
from app.rutas.modulos.cita.cita_api import citaapi
app.register_blueprint(citaapi, url_prefix='/api/v1')
