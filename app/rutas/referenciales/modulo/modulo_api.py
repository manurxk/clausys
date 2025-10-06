from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.modulo.ModuloDao import ModuloDao

modapi = Blueprint('modapi', __name__)

# ===============================
# Trae todos los módulos
# ===============================
@modapi.route('/modulos', methods=['GET'])
def getModulos():
    moddao = ModuloDao()

    try:
        modulos = moddao.getModulos()

        return jsonify({
            'success': True,
            'data': modulos,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los módulos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un módulo por ID
# ===============================
@modapi.route('/modulos/<int:modulo_id>', methods=['GET'])
def getModulo(modulo_id):
    moddao = ModuloDao()

    try:
        modulo = moddao.getModuloById(modulo_id)

        if modulo:
            return jsonify({
                'success': True,
                'data': modulo,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el módulo con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener módulo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo módulo
# ===============================
@modapi.route('/modulos', methods=['POST'])
def addModulo():
    data = request.get_json()
    moddao = ModuloDao()

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

        # Validar descripción
        if not moddao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números y acentos.'
            }), 400

        modulo_id = moddao.guardarModulo(descripcion, estado)
        if modulo_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': modulo_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el módulo (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar módulo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un módulo
# ===============================
@modapi.route('/modulos/<int:modulo_id>', methods=['PUT'])
def updateModulo(modulo_id):
    data = request.get_json()
    moddao = ModuloDao()

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

        # Validar descripción
        if not moddao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números y acentos.'
            }), 400

        if moddao.updateModulo(modulo_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': modulo_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el módulo con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar módulo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un módulo
# ===============================
@modapi.route('/modulos/<int:modulo_id>', methods=['DELETE'])
def deleteModulo(modulo_id):
    moddao = ModuloDao()

    try:
        resultado = moddao.deleteModulo(modulo_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Módulo con ID {modulo_id} eliminado correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar este módulo porque está siendo usado en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el módulo porque está siendo usado o no existe.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar módulo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
