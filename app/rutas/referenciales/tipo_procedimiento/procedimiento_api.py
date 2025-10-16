from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.tipo_procedimiento.ProcedimientoDao import TipoProcedimientoDao

tipo_procedimiento_api = Blueprint('tipo_procedimiento_api', __name__)

# ===============================
# Trae todos los tipos de procedimientos
# ===============================
@tipo_procedimiento_api.route('/tipos_procedimientos', methods=['GET'])
def getTiposProcedimientos():
    tipo_procedimiento_dao = TipoProcedimientoDao()

    try:
        tipos_procedimientos = tipo_procedimiento_dao.getTiposProcedimientos()

        return jsonify({
            'success': True,
            'data': tipos_procedimientos,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los tipos de procedimientos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un tipo de procedimiento por ID
# ===============================
@tipo_procedimiento_api.route('/tipos_procedimientos/<int:tipo_procedimiento_id>', methods=['GET'])
def getTipoProcedimiento(tipo_procedimiento_id):
    tipo_procedimiento_dao = TipoProcedimientoDao()

    try:
        tipo_procedimiento = tipo_procedimiento_dao.getTipoProcedimientoById(tipo_procedimiento_id)

        if tipo_procedimiento:
            return jsonify({
                'success': True,
                'data': tipo_procedimiento,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de procedimiento con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener tipo de procedimiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo tipo de procedimiento
# ===============================
@tipo_procedimiento_api.route('/tipos_procedimientos', methods=['POST'])
def addTipoProcedimiento():
    data = request.get_json()
    tipo_procedimiento_dao = TipoProcedimientoDao()

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
        if not tipo_procedimiento_dao.validarDescripcion(descripcion):
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

        tipo_procedimiento_id = tipo_procedimiento_dao.guardarTipoProcedimiento(descripcion, estado)
        if tipo_procedimiento_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': tipo_procedimiento_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el tipo de procedimiento (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar tipo de procedimiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un tipo de procedimiento
# ===============================
@tipo_procedimiento_api.route('/tipos_procedimientos/<int:tipo_procedimiento_id>', methods=['PUT'])
def updateTipoProcedimiento(tipo_procedimiento_id):
    data = request.get_json()
    tipo_procedimiento_dao = TipoProcedimientoDao()

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
        if not tipo_procedimiento_dao.validarDescripcion(descripcion):
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

        if tipo_procedimiento_dao.updateTipoProcedimiento(tipo_procedimiento_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': tipo_procedimiento_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el tipo de procedimiento con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar tipo de procedimiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un tipo de procedimiento
# ===============================
@tipo_procedimiento_api.route('/tipos_procedimientos/<int:tipo_procedimiento_id>', methods=['DELETE'])
def deleteTipoProcedimiento(tipo_procedimiento_id):
    tipo_procedimiento_dao = TipoProcedimientoDao()

    try:
        resultado = tipo_procedimiento_dao.deleteTipoProcedimiento(tipo_procedimiento_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Tipo de procedimiento con ID {tipo_procedimiento_id} eliminado correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar este tipo de procedimiento porque está siendo usado en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el tipo de procedimiento porque está siendo usado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar tipo de procedimiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
