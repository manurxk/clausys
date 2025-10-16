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




# ✅ CORRECTO
from app.rutas.modulos.consulta.consulta_routes import consultamod
app.register_blueprint(consultamod, url_prefix='/consulta')

# ✅ CORRECTO
from app.rutas.modulos.consulta.consulta_api import consultaapi
app.register_blueprint(consultaapi, url_prefix='/api/v1')





















from app.rutas.referenciales.diagnostico.diagnostico_routes import diagmod
from app.rutas.referenciales.diagnostico.diagnostico_api import diagapi

app.register_blueprint(diagmod, url_prefix=f'{MODULO_REFERENCIALES}/diagnostico')
app.register_blueprint(diagapi, url_prefix=API_V1)






# En el archivo principal de la aplicación (app.py)

# Registrar el Blueprint para Medicamento
from app.rutas.referenciales.medicamento.medicamento_routes import medmod
app.register_blueprint(medmod, url_prefix='/medicamento')

# Registrar el Blueprint para la API de Medicamento
from app.rutas.referenciales.medicamento.medicamento_api import medapi
app.register_blueprint(medapi, url_prefix='/api/v1')













# Registrar el Blueprint para Signos
from app.rutas.referenciales.signo.signo_routes import signomod
app.register_blueprint(signomod, url_prefix='/signo')

# Registrar el Blueprint para la API de Signos
from app.rutas.referenciales.signo.signo_api import signoapi
app.register_blueprint(signoapi, url_prefix='/api/v1')

# Registrar el Blueprint para Síntomas
from app.rutas.referenciales.sintoma.sintoma_routes import sintmod
app.register_blueprint(sintmod, url_prefix='/sintoma')

# Registrar el Blueprint para la API de Síntomas
from app.rutas.referenciales.sintoma.sintoma_api import sintapi
app.register_blueprint(sintapi, url_prefix='/api/v1')


# Registrar el Blueprint para Tipos de Análisis
from app.rutas.referenciales.tipo_analisis.analisis_routes import tipoanalisismod
app.register_blueprint(tipoanalisismod, url_prefix='/tipo-analisis')

# Registrar el Blueprint para la API de Tipos de Análisis
from app.rutas.referenciales.tipo_analisis.analisis_api import tipo_analisis_api
app.register_blueprint(tipo_analisis_api, url_prefix='/api/v1')



# Registrar el Blueprint para Tipos de Estudios
from app.rutas.referenciales.tipo_estudio.estudio_routes import tipo_estudio_mod
app.register_blueprint(tipo_estudio_mod, url_prefix='/tipo-estudio')

# Registrar el Blueprint para la API de Tipos de Estudios
from app.rutas.referenciales.tipo_estudio.estudio_api import tipo_estudio_api
app.register_blueprint(tipo_estudio_api, url_prefix='/api/v1')

# Registrar el Blueprint para Tipos de Procedimientos
from app.rutas.referenciales.tipo_procedimiento.procedimiento_routes import tipo_procedimiento_mod
app.register_blueprint(tipo_procedimiento_mod, url_prefix='/tipo-procedimiento')

# Registrar el Blueprint para la API de Tipos de Procedimientos
from app.rutas.referenciales.tipo_procedimiento.procedimiento_api import tipo_procedimiento_api
app.register_blueprint(tipo_procedimiento_api, url_prefix='/api/v1')
