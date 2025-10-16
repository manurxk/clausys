from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.tipo_estudio.EstudioDao import TipoEstudioDao

tipo_estudio_api = Blueprint('tipo_estudio_api', __name__)

# ===============================
# Trae todos los tipos de estudios
# ===============================
@tipo_estudio_api.route('/tipos_estudios', methods=['GET'])
def getTiposEstudios():
    tipo_estudio_dao = TipoEstudioDao()

    try:
        tipos_estudios = tipo_estudio_dao.getTiposEstudios()

        return jsonify({
            'success': True,
            'data': tipos_estudios,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los tipos de estudios: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un tipo de estudio por ID
# ===============================
@tipo_estudio_api.route('/tipos_estudios/<int:tipo_estudio_id>', methods=['GET'])
def getTipoEstudio(tipo_estudio_id):
    tipo_estudio_dao = TipoEstudioDao()

    try:
        tipo_estudio = tipo_estudio_dao.getTipoEstudioById(tipo_estudio_id)

        if tipo_estudio:
            return jsonify({
                'success': True,
                'data': tipo_estudio,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de estudio con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener tipo de estudio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo tipo de estudio
# ===============================
@tipo_estudio_api.route('/tipos_estudios', methods=['POST'])
def addTipoEstudio():
    data = request.get_json()
    tipo_estudio_dao = TipoEstudioDao()

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
        if not tipo_estudio_dao.validarDescripcion(descripcion):
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

        tipo_estudio_id = tipo_estudio_dao.guardarTipoEstudio(descripcion, estado)
        if tipo_estudio_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': tipo_estudio_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el tipo de estudio (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar tipo de estudio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un tipo de estudio
# ===============================
@tipo_estudio_api.route('/tipos_estudios/<int:tipo_estudio_id>', methods=['PUT'])
def updateTipoEstudio(tipo_estudio_id):
    data = request.get_json()
    tipo_estudio_dao = TipoEstudioDao()

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
        if not tipo_estudio_dao.validarDescripcion(descripcion):
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

        if tipo_estudio_dao.updateTipoEstudio(tipo_estudio_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': tipo_estudio_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de estudio con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar tipo de estudio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un tipo de estudio
# ===============================
@tipo_estudio_api.route('/tipos_estudios/<int:tipo_estudio_id>', methods=['DELETE'])
def deleteTipoEstudio(tipo_estudio_id):
    tipo_estudio_dao = TipoEstudioDao()

    try:
        resultado = tipo_estudio_dao.deleteTipoEstudio(tipo_estudio_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Tipo de estudio con ID {tipo_estudio_id} eliminado correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar este tipo de estudio porque está siendo usado en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el tipo de estudio porque está siendo usado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar tipo de estudio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
