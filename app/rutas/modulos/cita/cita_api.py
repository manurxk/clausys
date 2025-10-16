from flask import Blueprint, request, jsonify, current_app as app
from app.dao.modulos.cita.CitaDao import CitaDao

citaapi = Blueprint('citaapi', __name__)


# ============================================
# CRUD BÁSICO DE CITAS
# ============================================

@citaapi.route('/citas', methods=['GET'])
def getAllCitas():
    """Obtiene la lista completa de citas activas"""
    citadao = CitaDao()
    
    try:
        citas = citadao.getAllCitas()
        return jsonify({'success': True, 'data': citas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todas las citas: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@citaapi.route('/citas/<int:id_cita>', methods=['GET'])
def getCita(id_cita):
    """Obtiene una cita específica por su ID"""
    citadao = CitaDao()
    
    try:
        cita = citadao.getCitaById(id_cita)
        
        if cita:
            return jsonify({'success': True, 'data': cita, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró la cita con el ID proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener la cita: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@citaapi.route('/citas/<int:id_cita>/editar', methods=['GET'])
def getCitaParaEditar(id_cita):
    """Obtiene cita con IDs originales para formulario de edición"""
    citadao = CitaDao()

    try:
        cita = citadao.getCitaParaEditar(id_cita)

        if cita:
            return jsonify({'success': True, 'data': cita, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró la cita.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener cita para editar: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500








@citaapi.route('/pacientes/registro-rapido', methods=['POST'])
def registroPacienteRapido():
    """
    Registro rápido de paciente desde módulo de citas
    Body: { nombre, apellido, cedula, fecha_nacimiento }
    """
    data = request.get_json()
    citadao = CitaDao()
    
    # Validar campos requeridos
    campos_requeridos = ['nombre', 'apellido', 'cedula', 'fecha_nacimiento']
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio'
            }), 400
    
    try:
        paciente = citadao.registrarPacienteRapido(
            nombre=data['nombre'],
            apellido=data['apellido'],
            cedula=data['cedula'],
            fecha_nacimiento=data['fecha_nacimiento']
        )
        
        if paciente:
            return jsonify({
                'success': True,
                'data': paciente,
                'mensaje': 'Paciente registrado exitosamente'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo registrar el paciente. Verifique que la cédula no esté duplicada.'
            }), 400
    
    except Exception as e:
        app.logger.error(f"Error en registro rápido: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500







@citaapi.route('/citas', methods=['POST'])
def addCita():
    """Crea una nueva cita médica"""
    data = request.get_json()
    citadao = CitaDao()

    campos_requeridos = [
        'id_paciente', 'id_agenda_horario', 'id_especialista', 
        'id_especialidad', 'cita_fecha', 'cita_hora_inicio', 
        'cita_hora_fin', 'cita_tipo', 'cita_motivo', 'cita_creacion_usuario'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        cita_id = citadao.guardarCita(
            id_paciente=data['id_paciente'],
            id_agenda_horario=data['id_agenda_horario'],
            id_especialista=data['id_especialista'],
            id_especialidad=data['id_especialidad'],
            cita_fecha=data['cita_fecha'],
            cita_hora_inicio=data['cita_hora_inicio'],
            cita_hora_fin=data['cita_hora_fin'],
            cita_tipo=data['cita_tipo'],
            cita_motivo=data['cita_motivo'],
            cita_creacion_usuario=data['cita_creacion_usuario'],
            id_estado_cita=data.get('id_estado_cita', 1),  # AGENDADA por defecto
            cita_observaciones=data.get('cita_observaciones'),
            cita_numero_sesion=data.get('cita_numero_sesion')
        )

        if cita_id is not None:
            return jsonify({
                'success': True,
                'data': {'id_cita': cita_id, 'mensaje': 'Cita creada exitosamente'},
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar la cita. Verifique que haya cupos disponibles.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar cita: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


@citaapi.route('/citas/<int:id_cita>', methods=['PUT'])
def updateCita(id_cita):
    """Actualiza una cita existente"""
    data = request.get_json()
    citadao = CitaDao()

    cita_existente = citadao.getCitaById(id_cita)
    if not cita_existente:
        return jsonify({'success': False, 'error': 'No se encontró la cita con el ID proporcionado.'}), 404

    campos_requeridos = [
        'cita_fecha', 'cita_hora_inicio', 'cita_hora_fin',
        'cita_tipo', 'cita_motivo', 'id_estado_cita'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        resultado = citadao.updateCita(
            id_cita=id_cita,
            cita_fecha=data['cita_fecha'],
            cita_hora_inicio=data['cita_hora_inicio'],
            cita_hora_fin=data['cita_hora_fin'],
            cita_tipo=data['cita_tipo'],
            cita_motivo=data['cita_motivo'],
            cita_observaciones=data.get('cita_observaciones'),
            cita_numero_sesion=data.get('cita_numero_sesion'),
            id_estado_cita=data['id_estado_cita'],
            modificacion_usuario=data.get('modificacion_usuario', 1)
        )

        if resultado:
            return jsonify({
                'success': True,
                'data': {'id_cita': id_cita, 'mensaje': 'Cita actualizada exitosamente'},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo actualizar la cita.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al actualizar cita: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


@citaapi.route('/citas/<int:id_cita>', methods=['DELETE'])
def deleteCita(id_cita):
    """Elimina lógicamente una cita"""
    citadao = CitaDao()

    try:
        if citadao.deleteCita(id_cita):
            return jsonify({
                'success': True,
                'mensaje': f'Cita con ID {id_cita} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la cita con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar cita: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


# ============================================
# ENDPOINTS PARA MODALES DE BÚSQUEDA
# ============================================

@citaapi.route('/pacientes', methods=['GET'])
def getPacientes():
    """Obtiene lista de pacientes para modales"""
    citadao = CitaDao()
    
    try:
        pacientes = citadao.getPacientes()
        return jsonify({'success': True, 'data': pacientes, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener pacientes: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@citaapi.route('/especialistas', methods=['GET'])
def getEspecialistas():
    """Obtiene lista de especialistas para modales"""
    citadao = CitaDao()
    
    try:
        especialistas = citadao.getEspecialistas()
        return jsonify({'success': True, 'data': especialistas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener especialistas: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@citaapi.route('/especialidades', methods=['GET'])
def getEspecialidades():
    """Obtiene lista de especialidades para modales"""
    citadao = CitaDao()
    
    try:
        especialidades = citadao.getEspecialidades()
        return jsonify({'success': True, 'data': especialidades, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener especialidades: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@citaapi.route('/estados-citas', methods=['GET'])
def getEstadosCitas():
    """Obtiene lista de estados de citas"""
    citadao = CitaDao()
    
    try:
        estados = citadao.getEstadosCitas()
        return jsonify({'success': True, 'data': estados, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener estados de citas: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# CONSULTA DE CUPOS DISPONIBLES
# ============================================

@citaapi.route('/cupos/especialidad/<int:id_especialidad>', methods=['GET'])
def getCuposPorEspecialidad(id_especialidad):
    """
    Obtiene cupos disponibles para una especialidad.
    Query params: fecha_inicio (YYYY-MM-DD), fecha_fin (YYYY-MM-DD)
    """
    citadao = CitaDao()
    
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'success': False,
                'error': 'Debe proporcionar fecha_inicio y fecha_fin como parámetros.'
            }), 400
        
        cupos = citadao.getCuposDisponiblesPorEspecialidad(id_especialidad, fecha_inicio, fecha_fin)
        return jsonify({'success': True, 'data': cupos, 'error': None}), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener cupos por especialidad: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@citaapi.route('/cupos/especialista/<int:id_especialista>', methods=['GET'])
def getCuposPorEspecialista(id_especialista):
    """
    Obtiene cupos disponibles para un especialista.
    Query params: fecha_inicio (YYYY-MM-DD), fecha_fin (YYYY-MM-DD)
    """
    citadao = CitaDao()
    
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'success': False,
                'error': 'Debe proporcionar fecha_inicio y fecha_fin como parámetros.'
            }), 400
        
        cupos = citadao.getCuposDisponiblesPorEspecialista(id_especialista, fecha_inicio, fecha_fin)
        return jsonify({'success': True, 'data': cupos, 'error': None}), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener cupos por especialista: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500

# ============================================
# CAMBIO DE ESTADO DE CITAS
# ============================================

@citaapi.route('/citas/<int:id_cita>/confirmar', methods=['PATCH'])
def confirmarCita(id_cita):
    """Confirma una cita (atajo para cambiar estado a CONFIRMADA)"""
    data = request.get_json()
    citadao = CitaDao()
    
    usuario_id = data.get('usuario_id', 1) if data else 1
    
    try:
        resultado = citadao.confirmarCita(id_cita, usuario_id)
        
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': 'Cita confirmada exitosamente',
                'error': None
            }), 200
        else:
            return jsonify({'success': False, 'error': 'No se pudo confirmar la cita.'}), 400
    
    except Exception as e:
        app.logger.error(f"Error al confirmar cita: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@citaapi.route('/citas/<int:id_cita>/cancelar', methods=['PATCH'])
def cancelarCita(id_cita):
    """Cancela una cita (atajo para cambiar estado a CANCELADA)"""
    data = request.get_json()
    citadao = CitaDao()
    
    usuario_id = data.get('usuario_id', 1) if data else 1
    
    try:
        resultado = citadao.cancelarCita(id_cita, usuario_id)
        
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': 'Cita cancelada exitosamente',
                'error': None
            }), 200
        else:
            return jsonify({'success': False, 'error': 'No se pudo cancelar la cita.'}), 400
    
    except Exception as e:
        app.logger.error(f"Error al cancelar cita: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@citaapi.route('/citas/<int:id_cita>/estado', methods=['PATCH'])
def cambiarEstadoCita(id_cita):
    """
    Cambia el estado de una cita.
    Body: { "id_estado_cita": 2, "usuario_id": 1 }
    """
    data = request.get_json()
    citadao = CitaDao()
    
    if 'id_estado_cita' not in data:
        return jsonify({'success': False, 'error': 'Debe proporcionar id_estado_cita.'}), 400
    
    usuario_id = data.get('usuario_id', 1)
    
    try:
        resultado = citadao.cambiarEstadoCita(id_cita, data['id_estado_cita'], usuario_id)
        
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': 'Estado de la cita actualizado exitosamente',
                'error': None
            }), 200
        else:
            return jsonify({'success': False, 'error': 'No se pudo cambiar el estado de la cita.'}), 400
    
    except Exception as e:
        app.logger.error(f"Error al cambiar estado de cita: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# CONSULTAS ADICIONALES (OPCIONALES)
# ============================================

@citaapi.route('/citas/paciente/<int:id_paciente>', methods=['GET'])
def getCitasByPaciente(id_paciente):
    """Obtiene todas las citas de un paciente"""
    citadao = CitaDao()
    
    try:
        citas = citadao.getCitasByPaciente(id_paciente)
        return jsonify({'success': True, 'data': citas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener citas del paciente: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@citaapi.route('/citas/especialista/<int:id_especialista>', methods=['GET'])
def getCitasByEspecialista(id_especialista):
    """Obtiene todas las citas de un especialista"""
    citadao = CitaDao()
    
    try:
        citas = citadao.getCitasByEspecialista(id_especialista)
        return jsonify({'success': True, 'data': citas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener citas del especialista: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500