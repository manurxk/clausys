from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.sintoma.SintomaDao import SintomaDao

sintapi = Blueprint('sintapi', __name__)

# ===============================
# Trae todos los síntomas
# ===============================
@sintapi.route('/sintomas', methods=['GET'])
def getSintomas():
    sintdao = SintomaDao()

    try:
        sintomas = sintdao.getSintomas()

        return jsonify({
            'success': True,
            'data': sintomas,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los síntomas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un síntoma por ID
# ===============================
@sintapi.route('/sintomas/<int:sintoma_id>', methods=['GET'])
def getSintoma(sintoma_id):
    sintdao = SintomaDao()

    try:
        sintoma = sintdao.getSintomaById(sintoma_id)

        if sintoma:
            return jsonify({
                'success': True,
                'data': sintoma,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el síntoma con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener síntoma: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo síntoma
# ===============================
@sintapi.route('/sintomas', methods=['POST'])
def addSintoma():
    data = request.get_json()
    sintdao = SintomaDao()

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
        if not sintdao.validarDescripcion(descripcion):
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

        sintoma_id = sintdao.guardarSintoma(descripcion, estado)
        if sintoma_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': sintoma_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el síntoma (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar síntoma: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un síntoma
# ===============================
@sintapi.route('/sintomas/<int:sintoma_id>', methods=['PUT'])
def updateSintoma(sintoma_id):
    data = request.get_json()
    sintdao = SintomaDao()

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
        if not sintdao.validarDescripcion(descripcion):
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

        if sintdao.updateSintoma(sintoma_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': sintoma_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el síntoma con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar síntoma: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un síntoma
# ===============================
@sintapi.route('/sintomas/<int:sintoma_id>', methods=['DELETE'])
def deleteSintoma(sintoma_id):
    sintdao = SintomaDao()

    try:
        resultado = sintdao.deleteSintoma(sintoma_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Sintoma con ID {sintoma_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el síntoma porque está siendo usado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar síntoma: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
