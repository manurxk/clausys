from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.diagnostico.DiagnosticoDao import DiagnosticoDao

diagapi = Blueprint('diagapi', __name__)

# ===============================
# Trae todos los diagnósticos
# ===============================
@diagapi.route('/diagnosticos', methods=['GET'])
def getDiagnosticos():
    diagdao = DiagnosticoDao()

    try:
        diagnosticos = diagdao.getDiagnosticos()

        return jsonify({
            'success': True,
            'data': diagnosticos,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener todos los diagnósticos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un diagnóstico por ID
# ===============================
@diagapi.route('/diagnosticos/<int:diagnostico_id>', methods=['GET'])
def getDiagnostico(diagnostico_id):
    diagdao = DiagnosticoDao()

    try:
        diagnostico = diagdao.getDiagnosticoById(diagnostico_id)

        if diagnostico:
            return jsonify({
                'success': True,
                'data': diagnostico,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el diagnóstico con el ID proporcionado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener diagnóstico: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo diagnóstico
# ===============================
@diagapi.route('/diagnosticos', methods=['POST'])
def addDiagnostico():
    data = request.get_json()
    diagdao = DiagnosticoDao()

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
        codigo_cie10 = data.get('codigo_cie10', None)
        estado = data.get('estado', 'A')

        # Validar que la descripción contenga solo letras, números, espacios y puntos
        if not diagdao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números, acentos, espacios y puntos.'
            }), 400

        # Validar código CIE-10 si se proporciona
        if codigo_cie10 and not diagdao.validarCodigoCie10(codigo_cie10):
            return jsonify({
                'success': False,
                'error': 'El código CIE-10 tiene un formato inválido (ej: A15.0, B99.9).'
            }), 400

        # Validar estado
        if estado not in ['A', 'I']:
            return jsonify({
                'success': False,
                'error': 'El estado debe ser "A" (Activo) o "I" (Inactivo).'
            }), 400

        diagnostico_id = diagdao.guardarDiagnostico(descripcion, codigo_cie10, estado)
        if diagnostico_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': diagnostico_id,
                    'descripcion': descripcion,
                    'codigo_cie10': codigo_cie10,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el diagnóstico (duplicado o inválido).'
            }), 400
    except Exception as e:
        app.logger.error(f"Error al agregar diagnóstico: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Actualiza un diagnóstico
# ===============================
@diagapi.route('/diagnosticos/<int:diagnostico_id>', methods=['PUT'])
def updateDiagnostico(diagnostico_id):
    data = request.get_json()
    diagdao = DiagnosticoDao()

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
        codigo_cie10 = data.get('codigo_cie10', None)
        estado = data.get('estado', 'A')

        # Validar que la descripción contenga solo letras, números, espacios y puntos
        if not diagdao.validarDescripcion(descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras, números, acentos, espacios y puntos.'
            }), 400

        # Validar código CIE-10 si se proporciona
        if codigo_cie10 and not diagdao.validarCodigoCie10(codigo_cie10):
            return jsonify({
                'success': False,
                'error': 'El código CIE-10 tiene un formato inválido (ej: A15.0, B99.9).'
            }), 400

        # Validar estado
        if estado not in ['A', 'I']:
            return jsonify({
                'success': False,
                'error': 'El estado debe ser "A" (Activo) o "I" (Inactivo).'
            }), 400

        if diagdao.updateDiagnostico(diagnostico_id, descripcion, codigo_cie10, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': diagnostico_id,
                    'descripcion': descripcion,
                    'codigo_cie10': codigo_cie10,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el diagnóstico con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar diagnóstico: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Elimina un diagnóstico
# ===============================
@diagapi.route('/diagnosticos/<int:diagnostico_id>', methods=['DELETE'])
def deleteDiagnostico(diagnostico_id):
    diagdao = DiagnosticoDao()

    try:
        resultado = diagdao.deleteDiagnostico(diagnostico_id)
        if resultado is True:
            return jsonify({
                'success': True,
                'mensaje': f'Diagnóstico con ID {diagnostico_id} eliminado correctamente.',
                'error': None
            }), 200
        elif resultado == "en_uso":
            return jsonify({
                'success': False,
                'error': 'No se puede eliminar este diagnóstico porque está siendo usado en otra tabla.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo eliminar el diagnóstico porque está siendo usado.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar diagnóstico: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500