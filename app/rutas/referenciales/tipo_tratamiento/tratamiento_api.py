from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.tipo_tratamiento.TratamientoDao import TipoTratamientoDao

tipo_tratamiento_api = Blueprint('tipo_tratamiento_api', __name__)

# ===============================
# Trae todos los tipos de tratamientos
# ===============================
@tipo_tratamiento_api.route('/tipos-tratamientos', methods=['GET'])
def getTiposTratamientos():
    tipo_tratamiento_dao = TipoTratamientoDao()

    try:
        tipos_tratamientos = tipo_tratamiento_dao.getTiposTratamientos()

        return jsonify({
            'success': True,
            'data': tipos_tratamientos,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los tipos de tratamientos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un tipo de tratamiento por ID
# ===============================
@tipo_tratamiento_api.route('/tipos-tratamientos/<int:tipo_tratamiento_id>', methods=['GET'])
def getTipoTratamiento(tipo_tratamiento_id):
    tipo_tratamiento_dao = TipoTratamientoDao()

    try:
        tipo_tratamiento = tipo_tratamiento_dao.getTipoTratamientoById(tipo_tratamiento_id)

        if tipo_tratamiento:
            return jsonify({
                'success': True,
                'data': tipo_tratamiento,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de tratamiento con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener tipo de tratamiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo tipo de tratamiento
# ===============================
@tipo_tratamiento_api.route('/tipos-tratamientos', methods=['POST'])
def addTipoTratamiento():
    data = request.get_json()
    tipo_tratamiento_dao = TipoTratamientoDao()

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

        if not tipo_tratamiento_dao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números, acentos, espacios y puntos.'
            }), 400

        if estado not in ['A', 'I']:
            return jsonify({
                'success': False,
                'error': 'El estado debe ser "A" (Activo) o "I" (Inactivo).'
            }), 400

        tipo_tratamiento_id = tipo_tratamiento_dao.guardarTipoTratamiento(descripcion, estado)
        if tipo_tratamiento_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': tipo_tratamiento_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el tipo de tratamiento (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar tipo de tratamiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un tipo de tratamiento
# ===============================
@tipo_tratamiento_api.route('/tipos-tratamientos/<int:tipo_tratamiento_id>', methods=['PUT'])
def updateTipoTratamiento(tipo_tratamiento_id):
    data = request.get_json()
    tipo_tratamiento_dao = TipoTratamientoDao()

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

        if not tipo_tratamiento_dao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números, acentos, espacios y puntos.'
            }), 400

        if estado not in ['A', 'I']:
            return jsonify({
                'success': False,
                'error': 'El estado debe ser "A" o "I".'
            }), 400

        if tipo_tratamiento_dao.updateTipoTratamiento(tipo_tratamiento_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': tipo_tratamiento_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de tratamiento con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar tipo de tratamiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un tipo de tratamiento
# ===============================
@tipo_tratamiento_api.route('/tipos-tratamientos/<int:tipo_tratamiento_id>', methods=['DELETE'])
def deleteTipoTratamiento(tipo_tratamiento_id):
    tipo_tratamiento_dao = TipoTratamientoDao()

    try:
        resultado = tipo_tratamiento_dao.deleteTipoTratamiento(tipo_tratamiento_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Tipo de tratamiento con ID {tipo_tratamiento_id} eliminado correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar este tipo de tratamiento porque está siendo usado en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el tipo de tratamiento porque está siendo usado o no existe.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar tipo de tratamiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
