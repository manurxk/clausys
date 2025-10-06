from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.estado_civil.EstadoCivilDao import EstadoCivilDao

ecapi = Blueprint('ecapi', __name__)

# ===============================
# Trae todos los estados civiles
# ===============================
@ecapi.route('/estados-civiles', methods=['GET'])
def getEstadosCiviles():
    ecdao = EstadoCivilDao()

    try:
        estados = ecdao.getEstadosCiviles()
        return jsonify({
            'success': True,
            'data': estados,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los estados civiles: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un estado civil por ID
# ===============================
@ecapi.route('/estados-civiles/<int:estado_id>', methods=['GET'])
def getEstadoCivil(estado_id):
    ecdao = EstadoCivilDao()

    try:
        estado = ecdao.getEstadoCivilById(estado_id)

        if estado:
            return jsonify({
                'success': True,
                'data': estado,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el estado civil con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener estado civil: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo estado civil
# ===============================
@ecapi.route('/estados-civiles', methods=['POST'])
def addEstadoCivil():
    data = request.get_json()
    ecdao = EstadoCivilDao()

    # Validar que el JSON tenga los campos necesarios
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
        estado = bool(data['estado'])

        estado_id = ecdao.guardarEstadoCivil(descripcion, estado)
        if estado_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': estado_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el estado civil (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar estado civil: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un estado civil
# ===============================
@ecapi.route('/estados-civiles/<int:estado_id>', methods=['PUT'])
def updateEstadoCivil(estado_id):
    data = request.get_json()
    ecdao = EstadoCivilDao()

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
        estado = bool(data['estado'])

        if ecdao.updateEstadoCivil(estado_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': estado_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el estado civil con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar estado civil: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un estado civil
# ===============================
@ecapi.route('/estados-civiles/<int:estado_id>', methods=['DELETE'])
def deleteEstadoCivil(estado_id):
    ecdao = EstadoCivilDao()

    try:
        if ecdao.deleteEstadoCivil(estado_id):
            return jsonify({
                'success': True,
                'mensaje': f'Estado civil con ID {estado_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el estado civil con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar estado civil: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
