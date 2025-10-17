from flask import Blueprint, request, jsonify, current_app as app
from app.dao.modulos.consulta.ReTratamientoDao import TratamientoDao

registrotratamientoapi = Blueprint('registrotratamientoapi', __name__)


# ============================================
# CRUD BÁSICO DE REGISTRO TRATAMIENTOS
# ============================================

@registrotratamientoapi.route('/tratamientos', methods=['GET'])
def getAllTratamientos():
    """Obtiene la lista completa de tratamientos activos"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientos()
        return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los tratamientos: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@registrotratamientoapi.route('/tratamientos/<int:id_tratamiento>', methods=['GET'])
def getTratamiento(id_tratamiento):
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


@registrotratamientoapi.route('/tratamientos/<int:id_tratamiento>/editar', methods=['GET'])
def getTratamientoParaEditar(id_tratamiento):
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


@registrotratamientoapi.route('/tratamientos', methods=['POST'])
def addTratamiento():
    """
    Crea un nuevo registro de tratamiento psicológico
    
    Body JSON esperado:
    {
        "id_consulta": 123,
        "id_paciente": 456,
        "id_registro_diagnostico": 789,
        "id_tipo_tratamiento": 1,
        "des_tratamiento": "Terapia Cognitiva para Ansiedad",
        "tratamiento_objetivos": "Reducir niveles de ansiedad...",
        "numero_sesiones": 12,
        "frecuencia_sesiones": "SEMANAL",
        "duracion_sesion": 60,
        "tratamiento_fecha_inicio": "2025-01-20",
        "tratamiento_fecha_fin": "2025-04-20",
        "tratamiento_estado": "ACTIVO",
        "tratamiento_observaciones": "Paciente muy receptivo",
        "usuario_creacion": "ADMIN"
    }
    """
    data = request.get_json()
    dao = TratamientoDao()

    # Validar campos obligatorios
    campos_requeridos = [
        'id_consulta',
        'id_paciente', 
        'id_registro_diagnostico',
        'id_tipo_tratamiento',
        'des_tratamiento', 
        'tratamiento_fecha_inicio',
        'tratamiento_estado'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({
                'success': False, 
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        tratamiento_id = dao.guardarTratamiento(
            # IDs relacionales
            id_consulta=data['id_consulta'],
            id_paciente=data['id_paciente'],
            id_registro_diagnostico=data['id_registro_diagnostico'],
            id_tipo_tratamiento=data['id_tipo_tratamiento'],
            
            # Información del tratamiento
            des_tratamiento=data['des_tratamiento'],
            tratamiento_objetivos=data.get('tratamiento_objetivos'),
            
            # Sesiones psicológicas
            numero_sesiones=data.get('numero_sesiones'),
            frecuencia_sesiones=data.get('frecuencia_sesiones'),
            duracion_sesion=data.get('duracion_sesion'),
            
            # Fechas
            tratamiento_fecha_inicio=data['tratamiento_fecha_inicio'],
            tratamiento_fecha_fin=data.get('tratamiento_fecha_fin'),
            
            # Estado y observaciones
            tratamiento_estado=data.get('tratamiento_estado', 'ACTIVO'),
            tratamiento_observaciones=data.get('tratamiento_observaciones'),
            
            # Auditoría
            usuario_creacion=data.get('usuario_creacion', 'ADMIN')
        )

        if tratamiento_id is not None:
            return jsonify({
                'success': True,
                'data': {
                    'id_tratamiento': tratamiento_id, 
                    'mensaje': 'Tratamiento psicológico creado exitosamente'
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el tratamiento. Verifique los datos proporcionados.'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Error al agregar tratamiento: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Ocurrió un error interno: {str(e)}'
        }), 500


@registrotratamientoapi.route('/tratamientos/<int:id_tratamiento>', methods=['PUT'])
def updateTratamiento(id_tratamiento):
    """Actualiza un tratamiento existente"""
    data = request.get_json()
    dao = TratamientoDao()

    # Validar que existe el tratamiento
    tratamiento_existente = dao.getTratamientoById(id_tratamiento)
    if not tratamiento_existente:
        return jsonify({
            'success': False, 
            'error': 'No se encontró el tratamiento con el ID proporcionado.'
        }), 404

    # Validar campos obligatorios para actualización
    campos_requeridos = [
        'id_tipo_tratamiento',
        'des_tratamiento',
        'tratamiento_fecha_inicio', 
        'tratamiento_estado'
    ]

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None:
            return jsonify({
                'success': False, 
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        resultado = dao.updateTratamiento(
            id_tratamiento=id_tratamiento,
            id_tipo_tratamiento=data['id_tipo_tratamiento'],
            des_tratamiento=data['des_tratamiento'],
            tratamiento_objetivos=data.get('tratamiento_objetivos'),
            numero_sesiones=data.get('numero_sesiones'),
            frecuencia_sesiones=data.get('frecuencia_sesiones'),
            duracion_sesion=data.get('duracion_sesion'),
            tratamiento_fecha_inicio=data['tratamiento_fecha_inicio'],
            tratamiento_fecha_fin=data.get('tratamiento_fecha_fin'),
            tratamiento_estado=data['tratamiento_estado'],
            tratamiento_observaciones=data.get('tratamiento_observaciones'),
            usuario_modificacion=data.get('usuario_modificacion', 'ADMIN')
        )

        if resultado:
            return jsonify({
                'success': True,
                'data': {
                    'id_tratamiento': id_tratamiento, 
                    'mensaje': 'Tratamiento actualizado exitosamente'
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo actualizar el tratamiento.'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Error al actualizar tratamiento: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Ocurrió un error interno: {str(e)}'
        }), 500


@registrotratamientoapi.route('/tratamientos/<int:id_tratamiento>', methods=['DELETE'])
def deleteTratamiento(id_tratamiento):
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

@registrotratamientoapi.route('/tratamientos/<int:id_tratamiento>/finalizar', methods=['PATCH'])
def finalizarTratamiento(id_tratamiento):
    """
    Finaliza un tratamiento activo
    
    Body (opcional):
    {
        "fecha_fin": "2025-01-20",
        "observaciones": "Tratamiento completado exitosamente. Paciente muestra mejora significativa."
    }
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


@registrotratamientoapi.route('/tratamientos/<int:id_tratamiento>/suspender', methods=['PATCH'])
def suspenderTratamiento(id_tratamiento):
    """
    Suspende un tratamiento activo
    
    Body (opcional):
    {
        "observaciones": "Suspendido temporalmente por motivos personales del paciente"
    }
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


@registrotratamientoapi.route('/tratamientos/<int:id_tratamiento>/reactivar', methods=['PATCH'])
def reactivarTratamiento(id_tratamiento):
    """
    Reactiva un tratamiento suspendido o en pausa
    
    Body (opcional):
    {
        "observaciones": "Paciente retoma el tratamiento"
    }
    """
    data = request.get_json() if request.get_json() else {}
    dao = TratamientoDao()

    try:
        resultado = dao.reactivarTratamiento(
            id_tratamiento=id_tratamiento,
            observaciones=data.get('observaciones')
        )

        if resultado:
            return jsonify({
                'success': True,
                'mensaje': f'Tratamiento {id_tratamiento} reactivado exitosamente',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo reactivar el tratamiento.'
            }), 400

    except Exception as e:
        app.logger.error(f"Error al reactivar tratamiento: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# ENDPOINTS DE FILTRADO AUXILIARES
# ============================================

@registrotratamientoapi.route('/tratamientos/paciente/<int:id_paciente>', methods=['GET'])
def getTratamientosPorPaciente(id_paciente):
    """Obtiene todos los tratamientos de un paciente específico"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientosPorPaciente(id_paciente)
        
        if tratamientos:
            return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontraron tratamientos para este paciente.'}), 404
            
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos del paciente: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/tratamientos/consulta/<int:id_consulta>', methods=['GET'])
def getTratamientosPorConsulta(id_consulta):
    """Obtiene todos los tratamientos asociados a una consulta específica"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientosPorConsulta(id_consulta)
        
        if tratamientos:
            return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontraron tratamientos para esta consulta.'}), 404
            
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos de la consulta: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/tratamientos/estado/<string:estado>', methods=['GET'])
def getTratamientosPorEstado(estado):
    """Obtiene tratamientos filtrados por estado (ACTIVO, EN_PAUSA, SUSPENDIDO, FINALIZADO)"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientosPorEstado(estado)
        return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos por estado: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/tratamientos/diagnostico/<int:id_registro_diagnostico>', methods=['GET'])
def getTratamientosPorDiagnostico(id_registro_diagnostico):
    """Obtiene todos los tratamientos asociados a un diagnóstico específico"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientosPorDiagnostico(id_registro_diagnostico)
        
        if tratamientos:
            return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontraron tratamientos para este diagnóstico.'}), 404
            
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos por diagnóstico: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/tratamientos/tipo/<int:id_tipo_tratamiento>', methods=['GET'])
def getTratamientosPorTipo(id_tipo_tratamiento):
    """Obtiene tratamientos filtrados por tipo de tratamiento"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientosPorTipo(id_tipo_tratamiento)
        return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos por tipo: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrotratamientoapi.route('/tratamientos/activos', methods=['GET'])
def getTratamientosActivos():
    """Obtiene todos los tratamientos activos del sistema"""
    dao = TratamientoDao()
    
    try:
        tratamientos = dao.getTratamientosActivos()
        return jsonify({'success': True, 'data': tratamientos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener tratamientos activos: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# ENDPOINT PARA TIPOS DE TRATAMIENTO
# ============================================

@registrotratamientoapi.route('/tipos-tratamientos', methods=['GET'])
def getTiposTratamientos():
    """
    Obtiene todos los tipos de tratamiento activos de la tabla tipos_tratamientos
    Usado por el modal de búsqueda en el frontend
    
    Respuesta:
    {
        "success": true,
        "data": [
            {
                "id_tipo_tratamiento": 1,
                "des_tipo_tratamiento": "Terapia Cognitiva Conductual",
                "est_tipo_tratamiento": "A"
            }
        ],
        "error": null
    }
    """
    dao = TratamientoDao()
    
    try:
        app.logger.info("Obteniendo tipos de tratamiento...")
        tipos = dao.getTiposTratamientos()
        
        if tipos:
            app.logger.info(f"Total tipos de tratamiento encontrados: {len(tipos)}")
            return jsonify({'success': True, 'data': tipos, 'error': None}), 200
        else:
            app.logger.warning("No se encontraron tipos de tratamiento activos")
            return jsonify({'success': True, 'data': [], 'error': None}), 200
            
    except Exception as e:
        app.logger.error(f"Error al obtener tipos de tratamiento: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500