from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.grupo.GrupoDao import GrupoDao

grupoapi = Blueprint('grupoapi', __name__)

# ===============================
# Trae todos los grupos
# ===============================
@grupoapi.route('/grupos', methods=['GET'])
def getGrupos():
    grupodao = GrupoDao()

    try:
        grupos = grupodao.getGrupos()

        return jsonify({
            'success': True,
            'data': grupos,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los grupos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un grupo por ID
# ===============================
@grupoapi.route('/grupos/<int:grupo_id>', methods=['GET'])
def getGrupo(grupo_id):
    grupodao = GrupoDao()

    try:
        grupo = grupodao.getGrupoById(grupo_id)

        if grupo:
            return jsonify({
                'success': True,
                'data': grupo,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el grupo con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener grupo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo grupo
# ===============================
@grupoapi.route('/grupos', methods=['POST'])
def addGrupo():
    data = request.get_json()
    grupodao = GrupoDao()

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

        if not grupodao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números y acentos.'
            }), 400

        grupo_id = grupodao.guardarGrupo(descripcion, estado)
        if grupo_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': grupo_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el grupo (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar grupo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un grupo
# ===============================
@grupoapi.route('/grupos/<int:grupo_id>', methods=['PUT'])
def updateGrupo(grupo_id):
    data = request.get_json()
    grupodao = GrupoDao()

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

        if not grupodao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números y acentos.'
            }), 400

        if grupodao.updateGrupo(grupo_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': grupo_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el grupo con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar grupo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un grupo
# ===============================
@grupoapi.route('/grupos/<int:grupo_id>', methods=['DELETE'])
def deleteGrupo(grupo_id):
    grupodao = GrupoDao()

    try:
        resultado = grupodao.deleteGrupo(grupo_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Grupo con ID {grupo_id} eliminado correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar este grupo porque está siendo usado en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el grupo.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar grupo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
