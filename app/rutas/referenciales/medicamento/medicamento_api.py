from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.medicamento.MedicamentoDao import MedicamentoDao

medapi = Blueprint('medapi', __name__)

# ===============================
# Trae todos los medicamentos
# ===============================
@medapi.route('/medicamentos', methods=['GET'])
def getMedicamentos():
    meddao = MedicamentoDao()

    try:
        medicamentos = meddao.getMedicamentos()

        return jsonify({
            'success': True,
            'data': medicamentos,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los medicamentos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un medicamento por ID
# ===============================
@medapi.route('/medicamentos/<int:medicamento_id>', methods=['GET'])
def getMedicamento(medicamento_id):
    meddao = MedicamentoDao()

    try:
        medicamento = meddao.getMedicamentoById(medicamento_id)

        if medicamento:
            return jsonify({
                'success': True,
                'data': medicamento,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el medicamento con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener medicamento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo medicamento
# ===============================
@medapi.route('/medicamentos', methods=['POST'])
def addMedicamento():
    data = request.get_json()
    meddao = MedicamentoDao()

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
        concentracion = data.get('concentracion', None)
        estado = data.get('estado', 'A')

        # Validar que la descripción contenga solo letras, números, espacios y puntos
        if not meddao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números, acentos, espacios y puntos.'
            }), 400

        # Validar concentración si se proporciona
        if concentracion and not meddao.validarConcentracion(concentracion):
            return jsonify({
                'success': False,
                'error': 'La concentración tiene un formato inválido (ej: 10mg, 20g).'
            }), 400

        # Validar estado
        if estado not in ['A', 'I']:
            return jsonify({
                'success': False,
                'error': 'El estado debe ser "A" (Activo) o "I" (Inactivo).'
            }), 400

        medicamento_id = meddao.guardarMedicamento(descripcion, concentracion, estado)
        if medicamento_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': medicamento_id,
                    'descripcion': descripcion,
                    'concentracion': concentracion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el medicamento (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar medicamento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un medicamento
# ===============================
@medapi.route('/medicamentos/<int:medicamento_id>', methods=['PUT'])
def updateMedicamento(medicamento_id):
    data = request.get_json()
    meddao = MedicamentoDao()

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
        concentracion = data.get('concentracion', None)
        estado = data.get('estado', 'A')

        # Validar que la descripción contenga solo letras, números, espacios y puntos
        if not meddao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números, acentos, espacios y puntos.'
            }), 400

        # Validar concentración si se proporciona
        if concentracion and not meddao.validarConcentracion(concentracion):
            return jsonify({
                'success': False,
                'error': 'La concentración tiene un formato inválido (ej: 10mg, 20g).'
            }), 400

        # Validar estado
        if estado not in ['A', 'I']:
            return jsonify({
                'success': False,
                'error': 'El estado debe ser "A" (Activo) o "I" (Inactivo).'
            }), 400

        if meddao.updateMedicamento(medicamento_id, descripcion, concentracion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': medicamento_id,
                    'descripcion': descripcion,
                    'concentracion': concentracion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el medicamento con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar medicamento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un medicamento
# ===============================
@medapi.route('/medicamentos/<int:medicamento_id>', methods=['DELETE'])
def deleteMedicamento(medicamento_id):
    meddao = MedicamentoDao()

    try:
        resultado = meddao.deleteMedicamento(medicamento_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Medicamento con ID {medicamento_id} eliminado correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar este medicamento porque está siendo usado en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el medicamento porque está siendo usado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar medicamento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500
