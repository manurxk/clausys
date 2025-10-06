from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.especialidad.EspecialidadDao import EspecialidadDao

espapi = Blueprint('espapi', __name__)

# ===============================
# Trae todas las especialidades
# ===============================
@espapi.route('/especialidades', methods=['GET'])
def getEspecialidades():
    espdao = EspecialidadDao()

    try:
        especialidades = espdao.getEspecialidades()

        return jsonify({
            'success': True,
            'data': especialidades,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todas las especialidades: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae una especialidad por ID
# ===============================
@espapi.route('/especialidades/<int:especialidad_id>', methods=['GET'])
def getEspecialidad(especialidad_id):
    espdao = EspecialidadDao()

    try:
        especialidad = espdao.getEspecialidadById(especialidad_id)

        if especialidad:
            return jsonify({
                'success': True,
                'data': especialidad,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la especialidad con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener especialidad: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega una nueva especialidad
# ===============================
@espapi.route('/especialidades', methods=['POST'])
def addEspecialidad():
    data = request.get_json()
    espdao = EspecialidadDao()

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

        # Validar que la descripción no contenga números
        if not espdao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras y acentos.'
            }), 400

        especialidad_id = espdao.guardarEspecialidad(descripcion, estado)
        if especialidad_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': especialidad_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar la especialidad (duplicada o inválida).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar especialidad: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza una especialidad
# ===============================
@espapi.route('/especialidades/<int:especialidad_id>', methods=['PUT'])
def updateEspecialidad(especialidad_id):
    data = request.get_json()
    espdao = EspecialidadDao()

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

        # Validar que no contenga números
        if not espdao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras y acentos.'
            }), 400

        if espdao.updateEspecialidad(especialidad_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': especialidad_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la especialidad con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar especialidad: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina una especialidad
# ===============================
@espapi.route('/especialidades/<int:especialidad_id>', methods=['DELETE'])
def deleteEspecialidad(especialidad_id):
    espdao = EspecialidadDao()

    try:
        resultado = espdao.deleteEspecialidad(especialidad_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Especialidad con ID {especialidad_id} eliminada correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar esta especialidad porque está siendo usada en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se puedo eliminar la especialdiad porque esta siendo usada.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar especialidad: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
