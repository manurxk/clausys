from flask import Blueprint, request, jsonify, current_app as app
from app.dao.modulos.consulta.ReProcedimientoDao import RegistroProcedimientoDao

registroprocedimientoapi = Blueprint('registroprocedimientoapi', __name__)


# ============================================
# CRUD BÁSICO DE REGISTRO PROCEDIMIENTOS
# ============================================

@registroprocedimientoapi.route('/registro-procedimientos', methods=['GET'])
def getAllRegistroProcedimientos():
    """Obtiene la lista completa de procedimientos activos"""
    dao = RegistroProcedimientoDao()
    
    try:
        procedimientos = dao.getRegistrosProcedimientos()
        return jsonify({'success': True, 'data': procedimientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los procedimientos: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@registroprocedimientoapi.route('/registro-procedimientos/<int:id_registro_procedimiento>', methods=['GET'])
def getRegistroProcedimiento(id_registro_procedimiento):
    """Obtiene un procedimiento específico por su ID"""
    dao = RegistroProcedimientoDao()
    
    try:
        procedimiento = dao.getRegistroProcedimientoById(id_registro_procedimiento)
        
        if procedimiento:
            return jsonify({'success': True, 'data': procedimiento, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el procedimiento con el ID proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener el procedimiento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registroprocedimientoapi.route('/registro-procedimientos/<int:id_registro_procedimiento>/editar', methods=['GET'])
def getRegistroProcedimientoParaEditar(id_registro_procedimiento):
    """Obtiene procedimiento con IDs originales para formulario de edición"""
    dao = RegistroProcedimientoDao()

    try:
        procedimiento = dao.getRegistroProcedimientoParaEditar(id_registro_procedimiento)

        if procedimiento:
            return jsonify({'success': True, 'data': procedimiento, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el procedimiento.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener procedimiento para editar: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registroprocedimientoapi.route('/registro-procedimientos', methods=['POST'])
def addRegistroProcedimiento():
    """Crea un nuevo registro de procedimiento"""
    data = request.get_json()
    dao = RegistroProcedimientoDao()

    # Validar campos obligatorios
    campos_requeridos = [
        'id_consulta', 'id_paciente', 'id_tipo_procedimiento',
        'des_registro_procedimiento', 'registro_fecha'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        procedimiento_id = dao.guardarRegistroProcedimiento(
            id_consulta=data['id_consulta'],
            id_paciente=data['id_paciente'],
            id_tipo_procedimiento=data['id_tipo_procedimiento'],
            des_registro_procedimiento=data['des_registro_procedimiento'],
            registro_fecha=data['registro_fecha'],
            registro_duracion=data.get('registro_duracion'),
            registro_resultado=data.get('registro_resultado'),
            registro_observaciones=data.get('registro_observaciones'),
            usuario_creacion=data.get('usuario_creacion', 'ADMIN')
        )

        if procedimiento_id is not None:
            return jsonify({
                'success': True,
                'data': {'id_registro_procedimiento': procedimiento_id, 'mensaje': 'Procedimiento creado exitosamente'},
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el procedimiento. Verifique los datos proporcionados.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar procedimiento: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


@registroprocedimientoapi.route('/registro-procedimientos/<int:id_registro_procedimiento>', methods=['PUT'])
def updateRegistroProcedimiento(id_registro_procedimiento):
    """Actualiza un procedimiento existente"""
    data = request.get_json()
    dao = RegistroProcedimientoDao()

    # Validar que existe el procedimiento
    procedimiento_existente = dao.getRegistroProcedimientoById(id_registro_procedimiento)
    if not procedimiento_existente:
        return jsonify({'success': False, 'error': 'No se encontró el procedimiento con el ID proporcionado.'}), 404

    # Validar campos obligatorios
    campos_requeridos = [
        'des_registro_procedimiento', 'registro_fecha'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        resultado = dao.updateRegistroProcedimiento(
            id_registro_procedimiento=id_registro_procedimiento,
            des_registro_procedimiento=data['des_registro_procedimiento'],
            registro_fecha=data['registro_fecha'],
            registro_duracion=data.get('registro_duracion'),
            registro_resultado=data.get('registro_resultado'),
            registro_observaciones=data.get('registro_observaciones'),
            usuario_modificacion=data.get('usuario_modificacion', 'ADMIN')
        )

        if resultado:
            return jsonify({
                'success': True,
                'data': {'id_registro_procedimiento': id_registro_procedimiento, 'mensaje': 'Procedimiento actualizado exitosamente'},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo actualizar el procedimiento.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al actualizar procedimiento: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


@registroprocedimientoapi.route('/registro-procedimientos/<int:id_registro_procedimiento>', methods=['DELETE'])
def deleteRegistroProcedimiento(id_registro_procedimiento):
    """Elimina lógicamente un procedimiento"""
    dao = RegistroProcedimientoDao()

    try:
        if dao.deleteRegistroProcedimiento(id_registro_procedimiento):
            return jsonify({
                'success': True,
                'mensaje': f'Procedimiento con ID {id_registro_procedimiento} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el procedimiento con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar procedimiento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# ENDPOINTS DE FILTRADO AUXILIARES
# ============================================

@registroprocedimientoapi.route('/registro-procedimientos/consulta/<int:id_consulta>', methods=['GET'])
def getRegistroProcedimientosPorConsulta(id_consulta):
    """Obtiene todos los procedimientos registrados en una consulta"""
    dao = RegistroProcedimientoDao()
    
    try:
        procedimientos = dao.getProcedimientosPorConsulta(id_consulta)
        return jsonify({'success': True, 'data': procedimientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener procedimientos de la consulta: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registroprocedimientoapi.route('/registro-procedimientos/paciente/<int:id_paciente>', methods=['GET'])
def getRegistroProcedimientosPorPaciente(id_paciente):
    """Obtiene todos los procedimientos de un paciente (historial)"""
    dao = RegistroProcedimientoDao()
    
    try:
        procedimientos = dao.getProcedimientosPorPaciente(id_paciente)
        return jsonify({'success': True, 'data': procedimientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener procedimientos del paciente: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registroprocedimientoapi.route('/registro-procedimientos/tipo/<int:id_tipo_procedimiento>', methods=['GET'])
def getRegistroProcedimientosPorTipo(id_tipo_procedimiento):
    """Obtiene registros de un tipo específico de procedimiento"""
    dao = RegistroProcedimientoDao()
    
    try:
        procedimientos = dao.getProcedimientosPorTipo(id_tipo_procedimiento)
        return jsonify({'success': True, 'data': procedimientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener procedimientos por tipo: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registroprocedimientoapi.route('/registro-procedimientos/profesional/<int:id_profesional>', methods=['GET'])
def getRegistroProcedimientosPorProfesional(id_profesional):
    """Obtiene todos los procedimientos realizados por un profesional"""
    dao = RegistroProcedimientoDao()
    
    try:
        procedimientos = dao.getProcedimientosPorProfesional(id_profesional)
        return jsonify({'success': True, 'data': procedimientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener procedimientos del profesional: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500