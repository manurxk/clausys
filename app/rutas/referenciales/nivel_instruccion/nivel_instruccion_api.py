from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.nivel_instruccion.Nivel_InstruccionDao import NivelInstruccionDao

nivapi = Blueprint('nivapi', __name__)

# ===============================
# Trae todos los niveles de instrucción
# ===============================
@nivapi.route('/niveles-instruccion', methods=['GET'])
def getNivelesInstruccion():
    ndao = NivelInstruccionDao()

    try:
        niveles = ndao.getNiveles()
        return jsonify({
            'success': True,
            'data': niveles,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los niveles de instrucción: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Trae un nivel de instrucción por ID
# ===============================
@nivapi.route('/niveles-instruccion/<int:nivel_id>', methods=['GET'])
def getNivelInstruccion(nivel_id):
    ndao = NivelInstruccionDao()

    try:
        nivel = ndao.getNivelById(nivel_id)

        if nivel:
            return jsonify({
                'success': True,
                'data': nivel,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el nivel de instrucción con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener nivel de instrucción: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Agrega un nuevo nivel de instrucción
# ===============================
@nivapi.route('/niveles-instruccion', methods=['POST'])
def addNivelInstruccion():
    data = request.get_json()
    ndao = NivelInstruccionDao()

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

        nivel_id = ndao.guardarNivel(descripcion, estado)
        if nivel_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': nivel_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el nivel de instrucción (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar nivel de instrucción: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Actualiza un nivel de instrucción
# ===============================
@nivapi.route('/niveles-instruccion/<int:nivel_id>', methods=['PUT'])
def updateNivelInstruccion(nivel_id):
    data = request.get_json()
    ndao = NivelInstruccionDao()

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

        if ndao.updateNivel(nivel_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': nivel_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el nivel de instrucción con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar nivel de instrucción: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ===============================
# Elimina un nivel de instrucción
# ===============================
@nivapi.route('/niveles-instruccion/<int:nivel_id>', methods=['DELETE'])
def deleteNivelInstruccion(nivel_id):
    ndao = NivelInstruccionDao()

    try:
        if ndao.deleteNivel(nivel_id):
            return jsonify({
                'success': True,
                'mensaje': f'Nivel de instrucción con ID {nivel_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el nivel de instrucción con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar nivel de instrucción: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
