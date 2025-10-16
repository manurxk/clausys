from flask import Blueprint, request, jsonify, current_app as app
from app.dao.modulos.consulta.ConsultaDao import ConsultaDao
from datetime import date

consultaapi = Blueprint('consultaapi', __name__)


# ============================================
# CONSULTAS DEL DÍA Y LISTADOS
# ============================================

@consultaapi.route('/consultas/dia/<int:id_especialista>', methods=['GET'])
def getConsultasDelDia(id_especialista):
    """
    Obtiene las citas del día del especialista con estado de consulta
    Query params opcionales: fecha (YYYY-MM-DD)
    Si no se proporciona fecha, usa la fecha actual
    """
    consultadao = ConsultaDao()
    
    try:
        fecha = request.args.get('fecha')
        
        if fecha:
            # Validar formato de fecha
            try:
                fecha_obj = date.fromisoformat(fecha)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }), 400
        else:
            fecha_obj = None  # Usará fecha actual
        
        consultas = consultadao.getConsultasDelDia(id_especialista, fecha_obj)
        return jsonify({'success': True, 'data': consultas, 'error': None}), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener consultas del día: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@consultaapi.route('/consultas', methods=['GET'])
def getAllConsultas():
    """
    Obtiene todas las consultas
    Query params opcionales: id_especialista (filtro)
    """
    consultadao = ConsultaDao()
    
    try:
        id_especialista = request.args.get('id_especialista', type=int)
        
        consultas = consultadao.getAllConsultas(id_especialista)
        return jsonify({'success': True, 'data': consultas, 'error': None}), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener todas las consultas: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


# ============================================
# CONSULTA ESPECÍFICA - OBTENER POR ID
# ============================================

@consultaapi.route('/consultas/<int:id_consulta>', methods=['GET'])
def getConsulta(id_consulta):
    """Obtiene una consulta específica por su ID con todos los detalles"""
    consultadao = ConsultaDao()
    
    try:
        consulta = consultadao.getConsultaById(id_consulta)
        
        if consulta:
            return jsonify({'success': True, 'data': consulta, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró la consulta con el ID proporcionado.'}), 404
    
    except Exception as e:
        app.logger.error(f"Error al obtener la consulta: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@consultaapi.route('/consultas/verificar/<int:id_cita>', methods=['GET'])
def verificarConsultaExistente(id_cita):
    """Verifica si ya existe una consulta para una cita específica"""
    consultadao = ConsultaDao()
    
    try:
        resultado = consultadao.verificarConsultaExistente(id_cita)
        return jsonify({'success': True, 'data': resultado, 'error': None}), 200
    
    except Exception as e:
        app.logger.error(f"Error al verificar consulta existente: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# INICIAR Y CREAR CONSULTA
# ============================================

@consultaapi.route('/consultas/iniciar', methods=['POST'])
def iniciarConsulta():
    """
    Inicia una nueva consulta o carga una existente en borrador
    Body: {
        "id_cita": 1,
        "id_paciente": 1,
        "id_especialista": 1,
        "consulta_fecha": "2025-10-15",
        "consulta_hora_inicio": "09:00",
        "consulta_tipo": "primera_vez",
        "consulta_numero_sesion": 1,
        "creacion_usuario": 1
    }
    """
    data = request.get_json()
    consultadao = ConsultaDao()
    
    campos_requeridos = [
        'id_cita', 'id_paciente', 'id_especialista',
        'consulta_fecha', 'consulta_hora_inicio',
        'consulta_tipo', 'consulta_numero_sesion', 'creacion_usuario'
    ]
    
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400
    
    try:
        # 1. Verificar si ya existe consulta para esta cita
        verificacion = consultadao.verificarConsultaExistente(data['id_cita'])
        
        if verificacion['existe']:
            # Ya existe, devolver la consulta existente
            consulta_existente = consultadao.getConsultaById(verificacion['id_consulta'])
            return jsonify({
                'success': True,
                'data': {
                    'es_nueva': False,
                    'consulta': consulta_existente,
                    'mensaje': 'Consulta ya existente cargada correctamente'
                },
                'error': None
            }), 200
        
        # 2. No existe, crear nueva consulta
        consulta_id = consultadao.crearConsulta(
            id_cita=data['id_cita'],
            id_paciente=data['id_paciente'],
            id_especialista=data['id_especialista'],
            consulta_fecha=data['consulta_fecha'],
            consulta_hora_inicio=data['consulta_hora_inicio'],
            consulta_tipo=data['consulta_tipo'],
            consulta_numero_sesion=data['consulta_numero_sesion'],
            creacion_usuario=data['creacion_usuario'],
            consulta_observaciones_generales=data.get('consulta_observaciones_generales')
        )
        
        if consulta_id:
            # Obtener la consulta recién creada
            nueva_consulta = consultadao.getConsultaById(consulta_id)
            return jsonify({
                'success': True,
                'data': {
                    'es_nueva': True,
                    'consulta': nueva_consulta,
                    'mensaje': 'Consulta iniciada exitosamente'
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo crear la consulta.'
            }), 500
    
    except Exception as e:
        app.logger.error(f"Error al iniciar consulta: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


# ============================================
# ACTUALIZAR DATOS BÁSICOS DE CONSULTA
# ============================================

@consultaapi.route('/consultas/<int:id_consulta>/datos-basicos', methods=['PUT'])
def actualizarDatosBasicos(id_consulta):
    """
    Actualiza los datos básicos de una consulta
    Body: {
        "consulta_fecha": "2025-10-15",
        "consulta_hora_inicio": "09:00",
        "consulta_hora_fin": "10:00",
        "consulta_observaciones_generales": "...",
        "modificacion_usuario": 1
    }
    """
    data = request.get_json()
    consultadao = ConsultaDao()
    
    # Verificar que la consulta existe
    consulta_existente = consultadao.getConsultaById(id_consulta)
    if not consulta_existente:
        return jsonify({
            'success': False,
            'error': 'No se encontró la consulta con el ID proporcionado.'
        }), 404
    
    campos_requeridos = [
        'consulta_fecha', 'consulta_hora_inicio',
        'modificacion_usuario'
    ]
    
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio.'
            }), 400
    
    try:
        resultado = consultadao.actualizarDatosBasicos(
            id_consulta=id_consulta,
            consulta_fecha=data['consulta_fecha'],
            consulta_hora_inicio=data['consulta_hora_inicio'],
            consulta_hora_fin=data.get('consulta_hora_fin'),
            consulta_observaciones_generales=data.get('consulta_observaciones_generales'),
            modificacion_usuario=data['modificacion_usuario']
        )
        
        if resultado:
            return jsonify({
                'success': True,
                'data': {'id_consulta': id_consulta, 'mensaje': 'Datos básicos actualizados exitosamente'},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudieron actualizar los datos básicos.'
            }), 500
    
    except Exception as e:
        app.logger.error(f"Error al actualizar datos básicos: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


# ============================================
# CAMBIO DE ESTADO DE CONSULTA
# ============================================

@consultaapi.route('/consultas/<int:id_consulta>/estado', methods=['PATCH'])
def cambiarEstadoConsulta(id_consulta):
    """
    Cambia el estado de una consulta
    Body: {
        "estado": "borrador" | "en_curso" | "completada" | "cancelada",
        "modificacion_usuario": 1
    }
    """
    data = request.get_json()
    consultadao = ConsultaDao()
    
    if 'estado' not in data:
        return jsonify({'success': False, 'error': 'Debe proporcionar el nuevo estado.'}), 400
    
    estados_validos = ['en_curso', 'borrador', 'completada', 'cancelada']
    if data['estado'] not in estados_validos:
        return jsonify({
            'success': False,
            'error': f'Estado inválido. Valores permitidos: {", ".join(estados_validos)}'
        }), 400
    
    modificacion_usuario = data.get('modificacion_usuario', 1)
    
    try:
        resultado = consultadao.cambiarEstadoConsulta(id_consulta, data['estado'], modificacion_usuario)
        
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': f'Estado de la consulta cambiado a {data["estado"]} exitosamente',
                'error': None
            }), 200
        else:
            return jsonify({'success': False, 'error': 'No se pudo cambiar el estado de la consulta.'}), 400
    
    except Exception as e:
        app.logger.error(f"Error al cambiar estado de consulta: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@consultaapi.route('/consultas/<int:id_consulta>/finalizar', methods=['POST'])
def finalizarConsulta(id_consulta):
    """
    Finaliza una consulta:
    - Cambia estado a 'completada'
    - Registra hora_fin
    - Actualiza estado de la cita a 'completada'
    Body: { "modificacion_usuario": 1 }
    """
    data = request.get_json()
    consultadao = ConsultaDao()
    
    modificacion_usuario = data.get('modificacion_usuario', 1) if data else 1
    
    try:
        resultado = consultadao.finalizarConsulta(id_consulta, modificacion_usuario)
        
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': 'Consulta finalizada exitosamente',
                'error': None
            }), 200
        else:
            return jsonify({'success': False, 'error': 'No se pudo finalizar la consulta.'}), 400
    
    except Exception as e:
        app.logger.error(f"Error al finalizar consulta: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# SIDEBAR - DATOS DEL PACIENTE
# ============================================

@consultaapi.route('/consultas/paciente/<int:id_paciente>/datos', methods=['GET'])
def getDatosPaciente(id_paciente):
    """Obtiene datos completos del paciente para el sidebar"""
    consultadao = ConsultaDao()
    
    try:
        datos = consultadao.getDatosPaciente(id_paciente)
        
        if datos:
            return jsonify({'success': True, 'data': datos, 'error': None}), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el paciente con el ID proporcionado.'
            }), 404
    
    except Exception as e:
        app.logger.error(f"Error al obtener datos del paciente: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@consultaapi.route('/consultas/paciente/<int:id_paciente>/historial', methods=['GET'])
def getHistorialConsultas(id_paciente):
    """
    Obtiene el historial de consultas del paciente
    Query params opcionales: limite (default: 5)
    """
    consultadao = ConsultaDao()
    
    try:
        limite = request.args.get('limite', default=5, type=int)
        
        historial = consultadao.getHistorialConsultas(id_paciente, limite)
        return jsonify({'success': True, 'data': historial, 'error': None}), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener historial de consultas: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# ANAMNESIS
# ============================================

@consultaapi.route('/consultas/anamnesis/verificar/<int:id_paciente>', methods=['GET'])
def verificarAnamnesis(id_paciente):
    """Verifica si el paciente ya tiene anamnesis"""
    consultadao = ConsultaDao()
    
    try:
        resultado = consultadao.verificarAnamnesis(id_paciente)
        return jsonify({'success': True, 'data': resultado, 'error': None}), 200
    
    except Exception as e:
        app.logger.error(f"Error al verificar anamnesis: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@consultaapi.route('/consultas/anamnesis/<int:id_paciente>', methods=['GET'])
def getAnamnesis(id_paciente):
    """Obtiene la anamnesis completa del paciente"""
    consultadao = ConsultaDao()
    
    try:
        anamnesis = consultadao.getAnamnesis(id_paciente)
        
        if anamnesis:
            return jsonify({'success': True, 'data': anamnesis, 'error': None}), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró anamnesis para este paciente.'
            }), 404
    
    except Exception as e:
        app.logger.error(f"Error al obtener anamnesis: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@consultaapi.route('/consultas/anamnesis', methods=['POST', 'PUT'])
def guardarAnamnesis():
    """
    Guarda o actualiza la anamnesis de un paciente
    Body: {
        "id_paciente": 1,
        "id_consulta_creacion": 1,
        "anm_nombre": "...",
        "anm_informantes": "...",
        ... (todos los campos de anamnesis)
        "creacion_usuario": 1 (solo para INSERT)
        "modificacion_usuario": 1 (solo para UPDATE)
    }
    """
    data = request.get_json()
    consultadao = ConsultaDao()
    
    if 'id_paciente' not in data:
        return jsonify({
            'success': False,
            'error': 'El campo id_paciente es obligatorio.'
        }), 400
    
    # Si es POST y no existe anamnesis, requiere id_consulta_creacion
    if request.method == 'POST':
        verificacion = consultadao.verificarAnamnesis(data['id_paciente'])
        if not verificacion['existe'] and 'id_consulta_creacion' not in data:
            return jsonify({
                'success': False,
                'error': 'El campo id_consulta_creacion es obligatorio para crear nueva anamnesis.'
            }), 400
    
    try:
        anamnesis_id = consultadao.guardarAnamnesis(data)
        
        if anamnesis_id:
            return jsonify({
                'success': True,
                'data': {
                    'id_anamnesis': anamnesis_id,
                    'mensaje': 'Anamnesis guardada exitosamente'
                },
                'error': None
            }), 200 if request.method == 'PUT' else 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar la anamnesis.'
            }), 500
    
    except Exception as e:
        app.logger.error(f"Error al guardar anamnesis: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


# ============================================
# CONTENIDO DE SESIÓN
# ============================================

@consultaapi.route('/consultas/<int:id_consulta>/contenido-sesion', methods=['GET'])
def getContenidoSesion(id_consulta):
    """Obtiene el contenido de una sesión específica"""
    consultadao = ConsultaDao()
    
    try:
        contenido = consultadao.getContenidoSesion(id_consulta)
        
        if contenido:
            return jsonify({'success': True, 'data': contenido, 'error': None}), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró contenido para esta sesión.'
            }), 404
    
    except Exception as e:
        app.logger.error(f"Error al obtener contenido de sesión: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@consultaapi.route('/consultas/contenido-sesion', methods=['POST', 'PUT'])
def guardarContenidoSesion():
    """
    Guarda o actualiza el contenido de una sesión
    Body: {
        "id_consulta": 1,
        "cont_evolucion": "...",
        "cont_temas_abordados": "...",
        "cont_intervenciones": "...",
        "cont_observaciones": "...",
        "cont_tareas_asignadas": "...",
        "cont_indicaciones": "...",
        "creacion_usuario": 1
    }
    """
    data = request.get_json()
    consultadao = ConsultaDao()
    
    if 'id_consulta' not in data:
        return jsonify({
            'success': False,
            'error': 'El campo id_consulta es obligatorio.'
        }), 400
    
    try:
        contenido_id = consultadao.guardarContenidoSesion(data)
        
        if contenido_id:
            return jsonify({
                'success': True,
                'data': {
                    'id_contenido_sesion': contenido_id,
                    'mensaje': 'Contenido de sesión guardado exitosamente'
                },
                'error': None
            }), 200 if request.method == 'PUT' else 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el contenido de la sesión.'
            }), 500
    
    except Exception as e:
        app.logger.error(f"Error al guardar contenido de sesión: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


# ============================================
# FILTROS Y BÚSQUEDAS ADICIONALES
# ============================================

@consultaapi.route('/consultas/paciente/<int:id_paciente>', methods=['GET'])
def getConsultasByPaciente(id_paciente):
    """Obtiene todas las consultas de un paciente"""
    consultadao = ConsultaDao()
    
    try:
        consultas = consultadao.getConsultasByPaciente(id_paciente)
        return jsonify({'success': True, 'data': consultas, 'error': None}), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener consultas del paciente: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@consultaapi.route('/consultas/fecha', methods=['GET'])
def getConsultasByFecha():
    """
    Obtiene consultas en un rango de fechas
    Query params: fecha_inicio (YYYY-MM-DD), fecha_fin (YYYY-MM-DD), id_especialista (opcional)
    """
    consultadao = ConsultaDao()
    
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        id_especialista = request.args.get('id_especialista', type=int)
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'success': False,
                'error': 'Debe proporcionar fecha_inicio y fecha_fin como parámetros.'
            }), 400
        
        consultas = consultadao.getConsultasByFecha(fecha_inicio, fecha_fin, id_especialista)
        return jsonify({'success': True, 'data': consultas, 'error': None}), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener consultas por fecha: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# ESTADÍSTICAS Y REPORTES
# ============================================

@consultaapi.route('/consultas/estadisticas/<int:id_especialista>', methods=['GET'])
def getEstadisticasEspecialista(id_especialista):
    """
    Obtiene estadísticas de consultas de un especialista
    Query params: fecha_inicio (YYYY-MM-DD), fecha_fin (YYYY-MM-DD)
    """
    consultadao = ConsultaDao()
    
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'success': False,
                'error': 'Debe proporcionar fecha_inicio y fecha_fin como parámetros.'
            }), 400
        
        estadisticas = consultadao.getEstadisticasEspecialista(id_especialista, fecha_inicio, fecha_fin)
        
        if estadisticas:
            return jsonify({'success': True, 'data': estadisticas, 'error': None}), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontraron estadísticas.'
            }), 404
    
    except Exception as e:
        app.logger.error(f"Error al obtener estadísticas: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500