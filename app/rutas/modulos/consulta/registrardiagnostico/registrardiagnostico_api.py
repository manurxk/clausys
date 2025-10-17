from flask import Blueprint, request, jsonify, current_app as app
from app.dao.modulos.consulta.ReDiagnosticoDao import RegistroDiagnosticoDao

registrodiagnosticoapi = Blueprint('registrodiagnosticoapi', __name__)

# ============================================
# CRUD BÁSICO DE REGISTRO DIAGNÓSTICOS
# ============================================

@registrodiagnosticoapi.route('/registro-diagnosticos', methods=['POST'])
def addRegistroDiagnostico():
    """Crea un nuevo registro de diagnóstico"""
    data = request.get_json()
    dao = RegistroDiagnosticoDao()

    # ✅ Logging para debugging
    app.logger.info(f"📥 Datos recibidos del frontend: {data}")

    # ✅ Validar campos obligatorios CON LOS NOMBRES QUE ENVÍA EL FRONTEND
    campos_requeridos = {
        'id_consulta': 'ID de consulta',
        'id_diagnostico': 'ID de diagnóstico',
        'tipo_diagnostico': 'Tipo de diagnóstico',
        'estado_diagnostico': 'Estado del diagnóstico',
        'registro_fecha': 'Fecha de registro'
    }

    for campo, nombre in campos_requeridos.items():
        if campo not in data or not data[campo]:
            error_msg = f'El campo {nombre} ({campo}) es obligatorio y no puede estar vacío.'
            app.logger.error(f"❌ Validación fallida: {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 400

    try:
        # ✅ MAPEO DE CAMPOS: Frontend → Backend
        # Frontend usa: tipo_diagnostico (PRINCIPAL/SECUNDARIO/DIFERENCIAL)
        # Backend usa: registro_tipo (PRESUNTIVO/DEFINITIVO/DIFERENCIAL)
        # Frontend usa: estado_diagnostico (CONFIRMADO/PRESUNTIVO/DESCARTADO)
        
        # Decidir el registro_tipo basado en el estado_diagnostico del frontend
        estado = data['estado_diagnostico'].upper()
        if estado == 'CONFIRMADO':
            registro_tipo = 'DEFINITIVO'
        elif estado == 'PRESUNTIVO':
            registro_tipo = 'PRESUNTIVO'
        elif estado == 'DESCARTADO':
            registro_tipo = 'DESCARTADO'  # Si tu BD lo soporta
        else:
            registro_tipo = 'PRESUNTIVO'  # Default
        
        # Mapear tipo_diagnostico a registro_gravedad (opcional)
        tipo = data['tipo_diagnostico'].upper()
        registro_gravedad = None
        if tipo == 'PRINCIPAL':
            registro_gravedad = 'GRAVE'  # Opcional: puedes ajustar esta lógica
        elif tipo == 'SECUNDARIO':
            registro_gravedad = 'MODERADO'
        
        app.logger.info(f"🔄 Mapeo realizado: estado={estado} → registro_tipo={registro_tipo}, tipo={tipo} → gravedad={registro_gravedad}")
        
        # ✅ Llamar al DAO con los nombres correctos
        diagnostico_id = dao.guardarRegistroDiagnostico(
            id_consulta=data['id_consulta'],
            id_diagnostico=data['id_diagnostico'],
            registro_fecha=data['registro_fecha'],
            registro_tipo=registro_tipo,  # ← Mapeado desde estado_diagnostico
            registro_gravedad=registro_gravedad,  # ← Derivado de tipo_diagnostico
            des_registro_diagnostico=data.get('descripcion_adicional'),  # ← Mapeado
            registro_observaciones=data.get('observaciones'),  # ← Correcto
            usuario_creacion=data.get('usuario_creacion', 'ADMIN')
        )

        if diagnostico_id is not None:
            app.logger.info(f"✅ Diagnóstico guardado con ID: {diagnostico_id}")
            return jsonify({
                'success': True,
                'data': {
                    'id_registro_diagnostico': diagnostico_id, 
                    'mensaje': 'Diagnóstico registrado exitosamente'
                },
                'error': None
            }), 201
        else:
            app.logger.error("❌ DAO retornó None - No se pudo guardar")
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el diagnóstico. Verifique los datos proporcionados.'
            }), 500
            
    except Exception as e:
        app.logger.error(f"💥 Error al agregar diagnóstico: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


# ============================================
# ENDPOINTS AUXILIARES (sin cambios necesarios)
# ============================================

@registrodiagnosticoapi.route('/registro-diagnosticos/consulta/<int:id_consulta>', methods=['GET'])
def getRegistroDiagnosticosPorConsulta(id_consulta):
    """Obtiene todos los diagnósticos registrados en una consulta"""
    dao = RegistroDiagnosticoDao()
    
    try:
        diagnosticos = dao.getDiagnosticosPorConsulta(id_consulta)
        
        # ✅ Mapear campos del DAO al formato del frontend
        diagnosticos_mapeados = []
        for d in diagnosticos:
            diagnosticos_mapeados.append({
                'id_registro_diagnostico': d['id_registro_diagnostico'],
                'descripcion': d['diagnostico'],
                'codigo_cie10': d['codigo_cie10'],
                'tipo': d['tipo'],  # PRESUNTIVO/DEFINITIVO
                'estado': 'CONFIRMADO' if d['tipo'] == 'DEFINITIVO' else 'PRESUNTIVO',
                'gravedad': d.get('gravedad'),
                'fecha': d['fecha'],
                'descripcion_adicional': d.get('descripcion')
            })
        
        return jsonify({'success': True, 'data': diagnosticos_mapeados, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener diagnósticos de la consulta: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


# ============================================
# RESTO DE ENDPOINTS (mantener igual)
# ============================================

@registrodiagnosticoapi.route('/registro-diagnosticos', methods=['GET'])
def getAllRegistroDiagnosticos():
    """Obtiene la lista completa de diagnósticos activos"""
    dao = RegistroDiagnosticoDao()
    
    try:
        diagnosticos = dao.getRegistrosDiagnosticos()
        return jsonify({'success': True, 'data': diagnosticos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los diagnósticos: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@registrodiagnosticoapi.route('/registro-diagnosticos/<int:id_registro_diagnostico>', methods=['GET'])
def getRegistroDiagnostico(id_registro_diagnostico):
    """Obtiene un diagnóstico específico por su ID"""
    dao = RegistroDiagnosticoDao()
    
    try:
        diagnostico = dao.getRegistroDiagnosticoById(id_registro_diagnostico)
        
        if diagnostico:
            return jsonify({'success': True, 'data': diagnostico, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el diagnóstico con el ID proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener el diagnóstico: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrodiagnosticoapi.route('/registro-diagnosticos/<int:id_registro_diagnostico>/editar', methods=['GET'])
def getRegistroDiagnosticoParaEditar(id_registro_diagnostico):
    """Obtiene diagnóstico con IDs originales para formulario de edición"""
    dao = RegistroDiagnosticoDao()

    try:
        diagnostico = dao.getRegistroDiagnosticoParaEditar(id_registro_diagnostico)

        if diagnostico:
            return jsonify({'success': True, 'data': diagnostico, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró el diagnóstico.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener diagnóstico para editar: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrodiagnosticoapi.route('/registro-diagnosticos/<int:id_registro_diagnostico>', methods=['PUT'])
def updateRegistroDiagnostico(id_registro_diagnostico):
    """Actualiza un diagnóstico existente"""
    data = request.get_json()
    dao = RegistroDiagnosticoDao()

    diagnostico_existente = dao.getRegistroDiagnosticoById(id_registro_diagnostico)
    if not diagnostico_existente:
        return jsonify({'success': False, 'error': 'No se encontró el diagnóstico con el ID proporcionado.'}), 404

    campos_requeridos = [
        'registro_tipo', 'registro_fecha'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        resultado = dao.updateRegistroDiagnostico(
            id_registro_diagnostico=id_registro_diagnostico,
            registro_tipo=data['registro_tipo'],
            registro_gravedad=data.get('registro_gravedad'),
            registro_fecha=data['registro_fecha'],
            des_registro_diagnostico=data.get('des_registro_diagnostico'),
            registro_observaciones=data.get('registro_observaciones'),
            usuario_modificacion=data.get('usuario_modificacion', 'ADMIN')
        )

        if resultado:
            return jsonify({
                'success': True,
                'data': {'id_registro_diagnostico': id_registro_diagnostico, 'mensaje': 'Diagnóstico actualizado exitosamente'},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo actualizar el diagnóstico.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al actualizar diagnóstico: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


@registrodiagnosticoapi.route('/registro-diagnosticos/<int:id_registro_diagnostico>', methods=['DELETE'])
def deleteRegistroDiagnostico(id_registro_diagnostico):
    """Elimina lógicamente un diagnóstico"""
    dao = RegistroDiagnosticoDao()

    try:
        if dao.deleteRegistroDiagnostico(id_registro_diagnostico):
            return jsonify({
                'success': True,
                'mensaje': f'Diagnóstico con ID {id_registro_diagnostico} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el diagnóstico con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar diagnóstico: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrodiagnosticoapi.route('/registro-diagnosticos/paciente/<int:id_paciente>', methods=['GET'])
def getRegistroDiagnosticosPorPaciente(id_paciente):
    """Obtiene todos los diagnósticos de un paciente (historial)"""
    dao = RegistroDiagnosticoDao()
    
    try:
        diagnosticos = dao.getDiagnosticosPorPaciente(id_paciente)
        return jsonify({'success': True, 'data': diagnosticos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener diagnósticos del paciente: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@registrodiagnosticoapi.route('/registro-diagnosticos/cie10/<string:codigo_cie10>', methods=['GET'])
def getRegistroDiagnosticosPorCodigo(codigo_cie10):
    """Obtiene registros de un diagnóstico específico por código CIE-10"""
    dao = RegistroDiagnosticoDao()
    
    try:
        diagnosticos = dao.getDiagnosticosPorCodigo(codigo_cie10)
        return jsonify({'success': True, 'data': diagnosticos, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener diagnósticos por código: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500