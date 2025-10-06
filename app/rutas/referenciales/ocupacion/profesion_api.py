from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.profesion.Profesion_Dao import ProfesionDao

profapi = Blueprint('profapi', __name__)

# ===============================
# Trae todas las profesiones
# ===============================
@profapi.route('/profesiones', methods=['GET'])
def getProfesiones():
    profdao = ProfesionDao()

    try:
        profesiones = profdao.getProfesiones()

        return jsonify({
            'success': True,
            'data': profesiones,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todas las profesiones: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae una profesión por ID
# ===============================
@profapi.route('/profesiones/<int:profesion_id>', methods=['GET'])
def getProfesion(profesion_id):
    profdao = ProfesionDao()

    try:
        profesion = profdao.getProfesionById(profesion_id)

        if profesion:
            return jsonify({
                'success': True,
                'data': profesion,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la profesión con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener profesión: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega una nueva profesión
# ===============================
@profapi.route('/profesiones', methods=['POST'])
def addProfesion():
    data = request.get_json()
    profdao = ProfesionDao()

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

        if not profdao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras y acentos.'
            }), 400

        profesion_id = profdao.guardarProfesion(descripcion, estado)
        if profesion_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': profesion_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar la profesión (duplicada o inválida).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar profesión: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza una profesión
# ===============================
@profapi.route('/profesiones/<int:profesion_id>', methods=['PUT'])
def updateProfesion(profesion_id):
    data = request.get_json()
    profdao = ProfesionDao()

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

        if not profdao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras y acentos.'
            }), 400

        if profdao.updateProfesion(profesion_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': profesion_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la profesión con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar profesión: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina una profesión
# ===============================
@profapi.route('/profesiones/<int:profesion_id>', methods=['DELETE'])
def deleteProfesion(profesion_id):
    profdao = ProfesionDao()

    try:
        resultado = profdao.deleteProfesion(profesion_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Profesión con ID {profesion_id} eliminada correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar esta profesión porque está siendo usada en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar la profesión porque está siendo usada.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar profesión: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
