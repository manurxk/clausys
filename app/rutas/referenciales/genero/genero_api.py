from flask import Blueprint, request, jsonify, current_app as app
from app.dao.referenciales.genero.GeneroDao import GeneroDao

genapi = Blueprint('genapi', __name__)

# ===============================
# Trae todos los géneros
# ===============================
@genapi.route('/generos', methods=['GET'])
def getGeneros():
    gdao = GeneroDao()
    try:
        generos = gdao.getGeneros()
        return jsonify({
            'success': True,
            'data': generos,
            'error': None
        }), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todos los géneros: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Trae un género por ID
# ===============================
@genapi.route('/generos/<int:genero_id>', methods=['GET'])
def getGenero(genero_id):
    gdao = GeneroDao()
    try:
        genero = gdao.getGeneroById(genero_id)
        if genero:
            return jsonify({
                'success': True,
                'data': genero,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el género con el ID proporcionado.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al obtener género: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500

# ===============================
# Agrega un nuevo género
# ===============================
@genapi.route('/generos', methods=['POST'])
def addGenero():
    data = request.get_json()
    gdao = GeneroDao()

    campos_requeridos = ['descripcion', 'estado']
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio.'}), 400
        if campo == 'descripcion' and (data[campo] is None or len(data[campo].strip()) == 0):
            return jsonify({'success': False, 'error': 'La descripción no puede estar vacía.'}), 400

    try:
        descripcion = data['descripcion'].upper()
        estado = bool(data['estado'])

        # Validación: solo letras y espacios
        import re
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras y espacios.'
            }), 400

        genero_id = gdao.guardarGenero(descripcion, estado)
        if genero_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': genero_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar el género (duplicado o inválido).'}), 400
    except Exception as e:
        app.logger.error(f"Error al agregar género: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500

# ===============================
# Actualiza un género
# ===============================
@genapi.route('/generos/<int:genero_id>', methods=['PUT'])
def updateGenero(genero_id):
    data = request.get_json()
    gdao = GeneroDao()

    campos_requeridos = ['descripcion', 'estado']
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio.'}), 400
        if campo == 'descripcion' and (data[campo] is None or len(data[campo].strip()) == 0):
            return jsonify({'success': False, 'error': 'La descripción no puede estar vacía.'}), 400

    try:
        descripcion = data['descripcion'].upper()
        estado = bool(data['estado'])

        # Validación: solo letras y espacios
        import re
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", descripcion):
            return jsonify({
                'success': False,
                'error': 'La descripción solo puede contener letras y espacios.'
            }), 400

        if gdao.updateGenero(genero_id, descripcion, estado):
            return jsonify({
                'success': True,
                'data': {
                    'id': genero_id,
                    'descripcion': descripcion,
                    'estado': estado
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el género con el ID proporcionado o no se pudo actualizar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar género: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500

# ===============================
# Elimina un género
# ===============================
@genapi.route('/generos/<int:genero_id>', methods=['DELETE'])
def deleteGenero(genero_id):
    gdao = GeneroDao()
    try:
        if gdao.deleteGenero(genero_id):
            return jsonify({
                'success': True,
                'mensaje': f'Género con ID {genero_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el género con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar género: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500
