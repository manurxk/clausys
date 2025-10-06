from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.cargo.CargoDao import CargoDao

cargoapi = Blueprint('cargoapi', __name__)

# ===============================
# Trae todos los cargos
# ===============================
@cargoapi.route('/cargos', methods=['GET'])
def getCargos():
    cargodao = CargoDao()

    try:
        cargos = cargodao.getCargos()

        return jsonify({
            'success': True,
            'data': cargos,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los cargos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un cargo por ID
# ===============================
@cargoapi.route('/cargos/<int:cargo_id>', methods=['GET'])
def getCargo(cargo_id):
    cargodao = CargoDao()

    try:
        cargo = cargodao.getCargoById(cargo_id)

        if cargo:
            return jsonify({
                'success': True,
                'data': cargo,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el cargo con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener cargo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo cargo
# ===============================
@cargoapi.route('/cargos', methods=['POST'])
def addCargo():
    data = request.get_json()
    cargodao = CargoDao()

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

        if not cargodao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras y acentos.'
            }), 400

        cargo_id = cargodao.guardarCargo(descripcion, estado)
        if cargo_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': cargo_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el cargo (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar cargo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un cargo
# ===============================
@cargoapi.route('/cargos/<int:cargo_id>', methods=['PUT'])
def updateCargo(cargo_id):
    data = request.get_json()
    cargodao = CargoDao()

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

        if not cargodao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras y acentos.'
            }), 400

        if cargodao.updateCargo(cargo_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': cargo_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el cargo con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar cargo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un cargo
# ===============================
@cargoapi.route('/cargos/<int:cargo_id>', methods=['DELETE'])
def deleteCargo(cargo_id):
    cargodao = CargoDao()

    try:
        resultado = cargodao.deleteCargo(cargo_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Cargo con ID {cargo_id} eliminado correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar este cargo porque está siendo usado en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el cargo porque está siendo usado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar cargo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
