from flask import Blueprint, request, jsonify, current_app as app
from app.dao.modulos.consulta.ReConsultaDao import ConsultaDao

consultaapi = Blueprint('consultaapi', __name__)


# ============================================
# CRUD BÁSICO DE CONSULTAS
# ============================================

@consultaapi.route('/consultas', methods=['GET'])
def getAllConsultas():
    """Obtiene la lista completa de consultas activas"""
    dao = ConsultaDao()
    
    try:
        consultas = dao.getConsultas()
        return jsonify({'success': True, 'data': consultas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todas las consultas: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@consultaapi.route('/consultas/<int:id_consulta>', methods=['GET'])
def getConsulta(id_consulta):
    """Obtiene una consulta específica por su ID"""
    dao = ConsultaDao()
    
    try:
        consulta = dao.getConsultaById(id_consulta)
        
        if consulta:
            return jsonify({'success': True, 'data': consulta, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró la consulta con el ID proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener la consulta: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@consultaapi.route('/consultas/<int:id_consulta>/editar', methods=['GET'])
def getConsultaParaEditar(id_consulta):
    """Obtiene consulta con IDs originales para formulario de edición"""
    dao = ConsultaDao()

    try:
        consulta = dao.getConsultaParaEditar(id_consulta)

        if consulta:
            return jsonify({'success': True, 'data': consulta, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró la consulta.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener consulta para editar: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@consultaapi.route('/consultas', methods=['POST'])
def addConsulta():
    """Crea una nueva consulta médica"""
    data = request.get_json()
    dao = ConsultaDao()

    # Validar campos obligatorios
    campos_requeridos = [
        'id_paciente', 'id_profesional', 'consulta_fecha', 'consulta_motivo'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        consulta_id = dao.guardarConsulta(
            id_paciente=data['id_paciente'],
            id_profesional=data['id_profesional'],
            consulta_fecha=data['consulta_fecha'],
            consulta_motivo=data['consulta_motivo'],
            consulta_estado=data.get('consulta_estado', 'PENDIENTE'),
            id_cita=data.get('id_cita'),
            des_consulta=data.get('des_consulta'),
            consulta_observaciones=data.get('consulta_observaciones'),
            usuario_creacion=data.get('usuario_creacion', 'ADMIN')
        )

        if consulta_id is not None:
            return jsonify({
                'success': True,
                'data': {'id_consulta': consulta_id, 'mensaje': 'Consulta creada exitosamente'},
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar la consulta. Verifique los datos proporcionados.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar consulta: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


@consultaapi.route('/consultas/<int:id_consulta>', methods=['PUT'])
def updateConsulta(id_consulta):
    """Actualiza una consulta existente"""
    data = request.get_json()
    dao = ConsultaDao()

    # Validar que existe la consulta
    consulta_existente = dao.getConsultaById(id_consulta)
    if not consulta_existente:
        return jsonify({'success': False, 'error': 'No se encontró la consulta con el ID proporcionado.'}), 404

    # Validar campos obligatorios
    campos_requeridos = [
        'consulta_fecha', 'consulta_motivo', 'consulta_estado'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        resultado = dao.updateConsulta(
            id_consulta=id_consulta,
            consulta_fecha=data['consulta_fecha'],
            consulta_motivo=data['consulta_motivo'],
            consulta_estado=data['consulta_estado'],
            des_consulta=data.get('des_consulta'),
            consulta_observaciones=data.get('consulta_observaciones'),
            usuario_modificacion=data.get('usuario_modificacion', 'ADMIN')
        )

        if resultado:
            return jsonify({
                'success': True,
                'data': {'id_consulta': id_consulta, 'mensaje': 'Consulta actualizada exitosamente'},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo actualizar la consulta.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al actualizar consulta: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


@consultaapi.route('/consultas/<int:id_consulta>', methods=['DELETE'])
def deleteConsulta(id_consulta):
    """Elimina lógicamente una consulta"""
    dao = ConsultaDao()

    try:
        if dao.deleteConsulta(id_consulta):
            return jsonify({
                'success': True,
                'mensaje': f'Consulta con ID {id_consulta} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la consulta con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar consulta: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# ENDPOINTS DE FILTRADO AUXILIARES
# ============================================

@consultaapi.route('/consultas/paciente/<int:id_paciente>', methods=['GET'])
def getConsultasPorPaciente(id_paciente):
    """Obtiene todas las consultas de un paciente específico"""
    dao = ConsultaDao()
    
    try:
        consultas = dao.getConsultasPorPaciente(id_paciente)
        return jsonify({'success': True, 'data': consultas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas del paciente: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@consultaapi.route('/consultas/profesional/<int:id_profesional>', methods=['GET'])
def getConsultasPorProfesional(id_profesional):
    """Obtiene todas las consultas de un profesional específico"""
    dao = ConsultaDao()
    
    try:
        consultas = dao.getConsultasPorProfesional(id_profesional)
        return jsonify({'success': True, 'data': consultas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas del profesional: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@consultaapi.route('/consultas/estado/<string:estado>', methods=['GET'])
def getConsultasPorEstado(estado):
    """Obtiene consultas filtradas por estado"""
    dao = ConsultaDao()
    
    try:
        consultas = dao.getConsultasPorEstado(estado)
        return jsonify({'success': True, 'data': consultas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultas por estado: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@consultaapi.route('/consultas/cita/<int:id_cita>', methods=['GET'])
def getConsultaDesdeCita(id_cita):
    """Obtiene la consulta asociada a una cita específica"""
    dao = ConsultaDao()
    
    try:
        consulta = dao.getConsultaDesdeCita(id_cita)
        
        if consulta:
            return jsonify({'success': True, 'data': consulta, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró consulta asociada a esta cita.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener consulta desde cita: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500