from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.dia.DiaDao import DiaSemanaDao

diaapi = Blueprint('diaapi', __name__)

# ===============================
# Trae todos los días de la semana
# ===============================
@diaapi.route('/dias', methods=['GET'])
def getDias():
    diadao = DiaSemanaDao()

    try:
        dias = diadao.getDias()
        return jsonify({
            'success': True,
            'data': dias,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener días: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un día por ID
# ===============================
@diaapi.route('/dias/<int:dia_id>', methods=['GET'])
def getDia(dia_id):
    diadao = DiaSemanaDao()

    try:
        dia = diadao.getDiaById(dia_id)

        if dia:
            return jsonify({
                'success': True,
                'data': dia,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el día con el ID proporcionado.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener día: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo día
# ===============================
@diaapi.route('/dias', methods=['POST'])
def addDia():
    data = request.get_json()
    diadao = DiaSemanaDao()

    campos_requeridos = ['descripcion', 'orden', 'estado']

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
        descripcion = data['descripcion'].lower()
        orden = int(data['orden'])
        estado = bool(data['estado'])

        if not diadao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras y acentos.'
            }), 400

        dia_id = diadao.guardarDia(descripcion, orden, estado)
        if dia_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': dia_id,
                    'descripcion': descripcion,
                    'orden': orden,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el día (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar día: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un día
# ===============================
@diaapi.route('/dias/<int:dia_id>', methods=['PUT'])
def updateDia(dia_id):
    data = request.get_json()
    diadao = DiaSemanaDao()

    campos_requeridos = ['descripcion', 'orden', 'estado']

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
        descripcion = data['descripcion'].lower()
        orden = int(data['orden'])
        estado = bool(data['estado'])

        if not diadao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras y acentos.'
            }), 400

        if diadao.updateDia(dia_id, descripcion, orden, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': dia_id,
                    'descripcion': descripcion,
                    'orden': orden,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el día con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar día: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un día
# ===============================
@diaapi.route('/dias/<int:dia_id>', methods=['DELETE'])
def deleteDia(dia_id):
    diadao = DiaSemanaDao()

    try:
        resultado = diadao.deleteDia(dia_id)
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': f'Día con ID {dia_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el día (posiblemente no existe o está en uso).'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar día: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
