from flask import Blueprint, request, jsonify, current_app as app
from app.dao.modulos.consulta.ReTratamientoDao import TratamientoDao

registrotratamientoapi = Blueprint('registrotratamientoapi', __name__)


# ============================================
# CRUD BÁSICO DE REGISTRO TRATAMIENTOS
# ============================================

@registrotratamientoapi.route('/registro-tratamientos', methods=['GET'])
def getAllRegistroTratamientos():
    """Obtiene la lista completa de tratamientos activos"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientos()
        return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los tratamientos: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@registrotratamientoapi.route('/registro-tratamientos/<int:id_tratamiento>', methods=['GET'])
def getRegistroTratamiento(id_tratamiento):
    """Obtiene un tratamiento específico por su ID"""
    dao = TratamientoDao()
    
    try:
        tratamiento = dao.getTratamientoById(id_tratamiento)
        
        if tratamiento:
            return jsonify({'success': True, 'data': tratamiento, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el tratamiento con el ID proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener el tratamiento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/registro-tratamientos/<int:id_tratamiento>/editar', methods=['GET'])
def getRegistroTratamientoParaEditar(id_tratamiento):
    """Obtiene tratamiento con IDs originales para formulario de edición"""
    dao = TratamientoDao()

    try:
        tratamiento = dao.getTratamientoParaEditar(id_tratamiento)

        if tratamiento:
            return jsonify({'success': True, 'data': tratamiento, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el tratamiento.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener tratamiento para editar: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/registro-tratamientos', methods=['POST'])
def addRegistroTratamiento():
    """Crea un nuevo registro de tratamiento"""
    data = request.get_json()
    dao = TratamientoDao()

    # Validar campos obligatorios
    campos_requeridos = [
        'id_paciente', 'des_tratamiento', 'tratamiento_fecha_inicio'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        tratamiento_id = dao.guardarTratamiento(
            id_paciente=data['id_paciente'],
            des_tratamiento=data['des_tratamiento'],
            tratamiento_fecha_inicio=data['tratamiento_fecha_inicio'],
            tratamiento_tipo=data.get('tratamiento_tipo'),
            id_diagnostico=data.get('id_diagnostico'),
            tratamiento_fecha_fin=data.get('tratamiento_fecha_fin'),
            tratamiento_estado=data.get('tratamiento_estado', 'ACTIVO'),
            tratamiento_objetivos=data.get('tratamiento_objetivos'),
            tratamiento_observaciones=data.get('tratamiento_observaciones'),
            usuario_creacion=data.get('usuario_creacion', 'ADMIN')
        )

        if tratamiento_id is not None:
            return jsonify({
                'success': True,
                'data': {'id_tratamiento': tratamiento_id, 'mensaje': 'Tratamiento creado exitosamente'},
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el tratamiento. Verifique los datos proporcionados.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar tratamiento: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


@registrotratamientoapi.route('/registro-tratamientos/<int:id_tratamiento>', methods=['PUT'])
def updateRegistroTratamiento(id_tratamiento):
    """Actualiza un tratamiento existente"""
    data = request.get_json()
    dao = TratamientoDao()

    # Validar que existe el tratamiento
    tratamiento_existente = dao.getTratamientoById(id_tratamiento)
    if not tratamiento_existente:
        return jsonify({'success': False, 'error': 'No se encontró el tratamiento con el ID proporcionado.'}), 404

    # Validar campos obligatorios
    campos_requeridos = [
        'des_tratamiento', 'tratamiento_tipo', 'tratamiento_fecha_inicio', 
        'tratamiento_fecha_fin', 'tratamiento_estado'
    ]

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        resultado = dao.updateTratamiento(
            id_tratamiento=id_tratamiento,
            des_tratamiento=data['des_tratamiento'],
            tratamiento_tipo=data['tratamiento_tipo'],
            tratamiento_fecha_inicio=data['tratamiento_fecha_inicio'],
            tratamiento_fecha_fin=data['tratamiento_fecha_fin'],
            tratamiento_estado=data['tratamiento_estado'],
            tratamiento_objetivos=data.get('tratamiento_objetivos'),
            tratamiento_observaciones=data.get('tratamiento_observaciones'),
            usuario_modificacion=data.get('usuario_modificacion', 'ADMIN')
        )

        if resultado:
            return jsonify({
                'success': True,
                'data': {'id_tratamiento': id_tratamiento, 'mensaje': 'Tratamiento actualizado exitosamente'},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo actualizar el tratamiento.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al actualizar tratamiento: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


@registrotratamientoapi.route('/registro-tratamientos/<int:id_tratamiento>', methods=['DELETE'])
def deleteRegistroTratamiento(id_tratamiento):
    """Elimina lógicamente un tratamiento"""
    dao = TratamientoDao()

    try:
        if dao.deleteTratamiento(id_tratamiento):
            return jsonify({
                'success': True,
                'mensaje': f'Tratamiento con ID {id_tratamiento} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tratamiento con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar tratamiento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# ACCIONES ESPECIALES DE TRATAMIENTOS
# ============================================

@registrotratamientoapi.route('/registro-tratamientos/<int:id_tratamiento>/finalizar', methods=['PATCH'])
def finalizarRegistroTratamiento(id_tratamiento):
    """
    Finaliza un tratamiento activo
    Body (opcional): { "fecha_fin": "2025-01-20", "observaciones": "Observaciones finales" }
    """
    data = request.get_json() if request.get_json() else {}
    dao = TratamientoDao()

    try:
        resultado = dao.finalizarTratamiento(
            id_tratamiento=id_tratamiento,
            fecha_fin=data.get('fecha_fin'),
            observaciones=data.get('observaciones')
        )

        if resultado:
            return jsonify({
                'success': True,
                'mensaje': f'Tratamiento {id_tratamiento} finalizado exitosamente',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo finalizar el tratamiento. Verifique que esté activo.'
            }), 400

    except Exception as e:
        app.logger.error(f"Error al finalizar tratamiento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/registro-tratamientos/<int:id_tratamiento>/suspender', methods=['PATCH'])
def suspenderRegistroTratamiento(id_tratamiento):
    """
    Suspende un tratamiento activo
    Body (opcional): { "observaciones": "Motivo de la suspensión" }
    """
    data = request.get_json() if request.get_json() else {}
    dao = TratamientoDao()

    try:
        resultado = dao.suspenderTratamiento(
            id_tratamiento=id_tratamiento,
            observaciones=data.get('observaciones')
        )

        if resultado:
            return jsonify({
                'success': True,
                'mensaje': f'Tratamiento {id_tratamiento} suspendido exitosamente',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo suspender el tratamiento. Verifique que esté activo.'
            }), 400

    except Exception as e:
        app.logger.error(f"Error al suspender tratamiento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# ENDPOINTS DE FILTRADO AUXILIARES
# ============================================

@registrotratamientoapi.route('/registro-tratamientos/paciente/<int:id_paciente>', methods=['GET'])
def getRegistroTratamientosPorPaciente(id_paciente):
    """Obtiene todos los tratamientos de un paciente específico"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientosPorPaciente(id_paciente)
        return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos del paciente: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/registro-tratamientos/estado/<string:estado>', methods=['GET'])
def getRegistroTratamientosPorEstado(estado):
    """Obtiene tratamientos filtrados por estado (ACTIVO, FINALIZADO, SUSPENDIDO)"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientosPorEstado(estado)
        return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos por estado: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/registro-tratamientos/diagnostico/<int:id_diagnostico>', methods=['GET'])
def getRegistroTratamientosPorDiagnostico(id_diagnostico):
    """Obtiene todos los tratamientos asociados a un diagnóstico específico"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientosPorDiagnostico(id_diagnostico)
        return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos por diagnóstico: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/registro-tratamientos/tipo/<string:tipo>', methods=['GET'])
def getRegistroTratamientosPorTipo(tipo):
    """Obtiene tratamientos filtrados por tipo (FARMACOLÓGICO, PSICOTERAPÉUTICO, MIXTO)"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientosPorTipo(tipo)
        return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos por tipo: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/registro-tratamientos/activos', methods=['GET'])
def getRegistroTratamientosActivos():
    """Obtiene todos los tratamientos activos del sistema"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientosActivos()
        return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos activos: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500