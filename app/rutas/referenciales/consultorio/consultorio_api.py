from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.consultorio.ConsultorioDao import ConsultorioDao

consapi = Blueprint('consapi', __name__)

# ===============================
# Trae todos los consultorios
# ===============================
@consapi.route('/consultorios', methods=['GET'])
def getConsultorios():
    consdao = ConsultorioDao()
    try:
        consultorios = consdao.getConsultorios()
        return jsonify({
            'success': True,
            'data': consultorios,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los consultorios: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un consultorio por ID
# ===============================
@consapi.route('/consultorios/<int:consultorio_id>', methods=['GET'])
def getConsultorio(consultorio_id):
    consdao = ConsultorioDao()
    try:
        consultorio = consdao.getConsultorioById(consultorio_id)
        if consultorio:
            return jsonify({
                'success': True,
                'data': consultorio,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el consultorio con el ID proporcionado.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener consultorio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo consultorio
# ===============================
@consapi.route('/consultorios', methods=['POST'])
def addConsultorio():
    data = request.get_json()
    consdao = ConsultorioDao()

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

        if not consdao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números y acentos.'
            }), 400

        consultorio_id = consdao.guardarConsultorio(descripcion, estado)
        if consultorio_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': consultorio_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el consultorio (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar consultorio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un consultorio
# ===============================
@consapi.route('/consultorios/<int:consultorio_id>', methods=['PUT'])
def updateConsultorio(consultorio_id):
    data = request.get_json()
    consdao = ConsultorioDao()

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

        if not consdao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números y acentos.'
            }), 400

        if consdao.updateConsultorio(consultorio_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': consultorio_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el consultorio con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar consultorio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un consultorio
# ===============================
@consapi.route('/consultorios/<int:consultorio_id>', methods=['DELETE'])
def deleteConsultorio(consultorio_id):
    consdao = ConsultorioDao()

    try:
        resultado = consdao.deleteConsultorio(consultorio_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Consultorio con ID {consultorio_id} eliminado correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar este consultorio porque está siendo usado en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el consultorio.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar consultorio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
