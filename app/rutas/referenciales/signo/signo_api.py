from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.signo.SignoDao import SignoDao

signoapi = Blueprint('signoapi', __name__)

# ===============================
# Trae todos los signos
# ===============================
@signoapi.route('/signos', methods=['GET'])
def getSignos():
    signo_dao = SignoDao()

    try:
        signos = signo_dao.getSignos()

        return jsonify({
            'success': True,
            'data': signos,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los signos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un signo por ID
# ===============================
@signoapi.route('/signos/<int:signo_id>', methods=['GET'])
def getSigno(signo_id):
    signo_dao = SignoDao()

    try:
        signo = signo_dao.getSignoById(signo_id)

        if signo:
            return jsonify({
                'success': True,
                'data': signo,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el signo con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener signo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo signo
# ===============================
@signoapi.route('/signos', methods=['POST'])
def addSigno():
    data = request.get_json()
    signo_dao = SignoDao()

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
        if not signo_dao.validarDescripcion(descripcion):
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

        signo_id = signo_dao.guardarSigno(descripcion, estado)
        if signo_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': signo_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el signo (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar signo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un signo
# ===============================
@signoapi.route('/signos/<int:signo_id>', methods=['PUT'])
def updateSigno(signo_id):
    data = request.get_json()
    signo_dao = SignoDao()

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
        if not signo_dao.validarDescripcion(descripcion):
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

        if signo_dao.updateSigno(signo_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': signo_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el signo con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar signo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un signo
# ===============================
@signoapi.route('/signos/<int:signo_id>', methods=['DELETE'])
def deleteSigno(signo_id):
    signo_dao = SignoDao()

    try:
        resultado = signo_dao.deleteSigno(signo_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Signo con ID {signo_id} eliminado correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar este signo porque está siendo usado en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el signo porque está siendo usado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar signo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
