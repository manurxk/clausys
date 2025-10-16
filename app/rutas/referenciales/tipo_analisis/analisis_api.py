from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.tipo_analisis.AnalisisDao import TipoAnalisisDao

tipo_analisis_api = Blueprint('tipo_analisis_api', __name__)

# ===============================
# Trae todos los tipos de análisis
# ===============================
@tipo_analisis_api.route('/tipos-analisis', methods=['GET'])
def getTiposAnalisis():
    tipo_analisis_dao = TipoAnalisisDao()

    try:
        tipos_analisis = tipo_analisis_dao.getTiposAnalisis()

        return jsonify({
            'success': True,
            'data': tipos_analisis,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los tipos de análisis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un tipo de análisis por ID
# ===============================
@tipo_analisis_api.route('/tipos-analisis/<int:tipo_analisis_id>', methods=['GET'])
def getTipoAnalisis(tipo_analisis_id):
    tipo_analisis_dao = TipoAnalisisDao()

    try:
        tipo_analisis = tipo_analisis_dao.getTipoAnalisisById(tipo_analisis_id)

        if tipo_analisis:
            return jsonify({
                'success': True,
                'data': tipo_analisis,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de análisis con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener tipo de análisis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo tipo de análisis
# ===============================
@tipo_analisis_api.route('/tipos-analisis', methods=['POST'])
def addTipoAnalisis():
    data = request.get_json()
    tipo_analisis_dao = TipoAnalisisDao()

    campos_requeridos = ['descripcion', 'estado']

    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio.'
            }), 400
        if campo == 'descripcion' and (data[campo] is None or len(data[campo].strip()) == 0):
            return jsonify({
                'success': False,
                'error': 'La descripción no puede estar vacía.'
            }), 400

    try:
        descripcion = data['descripcion'].upper()
        estado = data.get('estado', 'A')

        # Validar que la descripción contenga solo letras, números, espacios y puntos
        if not tipo_analisis_dao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números, acentos, espacios y puntos.'
            }), 400

        # Validar estado
        if estado not in ['A', 'I']:
            return jsonify({
                'success': False,
                'error': 'El estado debe ser "A" (Activo) o "I" (Inactivo).'
            }), 400

        tipo_analisis_id = tipo_analisis_dao.guardarTipoAnalisis(descripcion, estado)
        if tipo_analisis_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': tipo_analisis_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el tipo de análisis (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar tipo de análisis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un tipo de análisis
# ===============================
@tipo_analisis_api.route('/tipos-analisis/<int:tipo_analisis_id>', methods=['PUT'])
def updateTipoAnalisis(tipo_analisis_id):
    data = request.get_json()
    tipo_analisis_dao = TipoAnalisisDao()

    campos_requeridos = ['descripcion', 'estado']

    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio.'
            }), 400
        if campo == 'descripcion' and (data[campo] is None or len(data[campo].strip()) == 0):
            return jsonify({
                'success': False,
                'error': 'La descripción no puede estar vacía.'
            }), 400

    try:
        descripcion = data['descripcion'].upper()
        estado = data.get('estado', 'A')

        # Validar que la descripción contenga solo letras, números, espacios y puntos
        if not tipo_analisis_dao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números, acentos, espacios y puntos.'
            }), 400

        # Validar estado
        if estado not in ['A', 'I']:
            return jsonify({
                'success': False,
                'error': 'El estado debe ser "A" (Activo) o "I" (Inactivo).'
            }), 400

        if tipo_analisis_dao.updateTipoAnalisis(tipo_analisis_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': tipo_analisis_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de análisis con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar tipo de análisis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un tipo de análisis
# ===============================
@tipo_analisis_api.route('/tipos-analisis/<int:tipo_analisis_id>', methods=['DELETE'])
def deleteTipoAnalisis(tipo_analisis_id):
    tipo_analisis_dao = TipoAnalisisDao()

    try:
        resultado = tipo_analisis_dao.deleteTipoAnalisis(tipo_analisis_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Tipo de análisis con ID {tipo_analisis_id} eliminado correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar este tipo de análisis porque está siendo usado en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el tipo de análisis porque está siendo usado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar tipo de análisis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
