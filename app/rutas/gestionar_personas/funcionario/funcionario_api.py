from flask import Blueprint, request, jsonify, current_app as app
from app.dao.gestionar_personas.funcionario.FuncionarioDao import FuncionarioDao
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook
import io


funcionarioapi = Blueprint('funcionarioapi', __name__)




# ============================================
# OBTENER TODOS LOS FUNCIONARIOS
# ============================================
@funcionarioapi.route('/funcionarios', methods=['GET'])
def getFuncionarios():
    """Obtiene la lista completa de funcionarios"""
    funcionariodao = FuncionarioDao()
    
    try:
        funcionarios = funcionariodao.getFuncionarios()
        
        return jsonify({
            'success': True,
            'data': funcionarios,
            'error': None
        }), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener todos los funcionarios: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ============================================
# OBTENER SOLO ESPECIALISTAS
# ============================================
@funcionarioapi.route('/funcionarios/especialistas', methods=['GET'])
def getFuncionariosEspecialistas():
    """Obtiene solo los funcionarios que son especialistas"""
    funcionariodao = FuncionarioDao()
    
    try:
        especialistas = funcionariodao.getFuncionariosEspecialistas()
        
        return jsonify({
            'success': True,
            'data': especialistas,
            'error': None
        }), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener especialistas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ============================================
# OBTENER FUNCIONARIO POR ID
# ============================================
@funcionarioapi.route('/funcionarios/<int:id_funcionario>', methods=['GET'])
def getFuncionario(id_funcionario):
    """Obtiene un funcionario específico por su ID"""
    funcionariodao = FuncionarioDao()
    
    try:
        funcionario = funcionariodao.getFuncionarioById(id_funcionario)
        
        if funcionario:
            return jsonify({
                'success': True,
                'data': funcionario,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el funcionario con el ID proporcionado.'
            }), 404
    
    except Exception as e:
        app.logger.error(f"Error al obtener el funcionario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ============================================
# OBTENER FUNCIONARIO PARA EDITAR
# ============================================
@funcionarioapi.route('/funcionarios/<int:id_funcionario>/editar', methods=['GET'])
def getFuncionarioParaEditar(id_funcionario):
    """Obtiene funcionario con IDs originales para formulario de edición"""
    funcionariodao = FuncionarioDao()

    try:
        funcionario = funcionariodao.getFuncionarioParaEditar(id_funcionario)

        if funcionario:
            return jsonify({
                'success': True,
                'data': funcionario,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el funcionario.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener funcionario para editar: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno.'
        }), 500


# ============================================
# CREAR NUEVO FUNCIONARIO
# ============================================
@funcionarioapi.route('/funcionarios', methods=['POST'])
def addFuncionario():
    """Crea un nuevo funcionario con todos sus datos"""
    data = request.get_json()
    funcionariodao = FuncionarioDao()

    # Campos obligatorios
    campos_requeridos = [
        'nombre', 'apellido', 'cedula', 'telefono', 'id_cargo'
    ]

    # Validar campos obligatorios
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    # Validar si es especialista
    if funcionariodao.es_cargo_especialista(data['id_cargo']):
        if not data.get('esp_matricula'):
            return jsonify({
                'success': False,
                'error': 'La matrícula es obligatoria para especialistas.'
            }), 400
        
        especialidades = data.get('especialidades', [])
        if not especialidades or len(especialidades) == 0:
            return jsonify({
                'success': False,
                'error': 'Debe seleccionar al menos una especialidad.'
            }), 400

    try:
        funcionario_id = funcionariodao.guardarFuncionario(
            # Datos de persona (obligatorios)
            nombre=data['nombre'],
            apellido=data['apellido'],
            cedula=data['cedula'],
            telefono=data['telefono'],
            fecha_nacimiento=data.get('fecha_nacimiento'),
            
            # Datos de persona (opcionales)
            genero_id=data.get('id_genero'),
            estado_civil_id=data.get('id_estado_civil'),
            correo=data.get('correo'),
            domicilio=data.get('domicilio'),
            ciudad_id=data.get('id_ciudad'),
            ciudad_nacimiento_id=data.get('id_ciudad_nacimiento'),
            nivel_instruccion_id=data.get('id_nivel_instruccion'),
            profesion_id=data.get('id_profesion'),
            
            # Datos de funcionario
            id_cargo=data['id_cargo'],
            fun_estado=data.get('activo', True),
            creacion_usuario=data.get('creacion_usuario', 1),
            
            # Datos de especialista (condicionales)
            esp_matricula=data.get('esp_matricula'),
            especialidades=data.get('especialidades', []),
            esp_color_agenda=data.get('esp_color_agenda', '#3498db')
        )

        if funcionario_id is not None:
            return jsonify({
                'success': True,
                'data': {
                    'id_funcionario': funcionario_id,
                    'mensaje': 'Funcionario creado exitosamente'
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el funcionario. Consulte con el administrador.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al agregar funcionario: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Ocurrió un error interno: {str(e)}'
        }), 500


# ============================================
# ACTUALIZAR FUNCIONARIO EXISTENTE
# ============================================
@funcionarioapi.route('/funcionarios/<int:id_funcionario>', methods=['PUT'])
def updateFuncionario(id_funcionario):
    """Actualiza un funcionario existente con todos sus datos"""
    data = request.get_json()
    funcionariodao = FuncionarioDao()
    app.logger.info(f"Datos recibidos para actualizar: {data}")

    # Verificar que el funcionario existe
    funcionario_existente = funcionariodao.getFuncionarioById(id_funcionario)
    if not funcionario_existente:
        return jsonify({
            'success': False,
            'error': 'No se encontró el funcionario con el ID proporcionado.'
        }), 404

    # Campos obligatorios
    campos_requeridos = [
        'nombre', 'apellido', 'cedula', 'telefono', 'id_cargo'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    # Validar si es especialista
    if funcionariodao.es_cargo_especialista(data['id_cargo']):
        if not data.get('esp_matricula'):
            return jsonify({
                'success': False,
                'error': 'La matrícula es obligatoria para especialistas.'
            }), 400
        
        especialidades = data.get('especialidades', [])
        if not especialidades or len(especialidades) == 0:
            return jsonify({
                'success': False,
                'error': 'Debe seleccionar al menos una especialidad.'
            }), 400

    try:
        resultado = funcionariodao.updateFuncionario(
            id_funcionario=id_funcionario,
            
            # Datos de persona
            nombre=data['nombre'],
            apellido=data['apellido'],
            cedula=data['cedula'],
            fecha_nacimiento=data.get('fecha_nacimiento'),
            genero_id=data.get('id_genero'),
            estado_civil_id=data.get('id_estado_civil'),
            telefono=data['telefono'],
            correo=data.get('correo'),
            domicilio=data.get('domicilio'),
            ciudad_id=data.get('id_ciudad'),
            ciudad_nacimiento_id=data.get('id_ciudad_nacimiento'),
            nivel_instruccion_id=data.get('id_nivel_instruccion'),
            profesion_id=data.get('id_profesion'),
            
            # Datos de funcionario
            id_cargo=data['id_cargo'],
            fun_estado=data.get('activo', True),
            
            # Datos de especialista
            esp_matricula=data.get('esp_matricula'),
            especialidades=data.get('especialidades', []),
            esp_color_agenda=data.get('esp_color_agenda', '#3498db')
        )

        if resultado:
            return jsonify({
                'success': True,
                'data': {
                    'id_funcionario': id_funcionario,
                    'mensaje': 'Funcionario actualizado exitosamente'
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo actualizar el funcionario.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al actualizar funcionario: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Ocurrió un error interno: {str(e)}'
        }), 500


# ============================================
# ELIMINAR FUNCIONARIO
# ============================================
@funcionarioapi.route('/funcionarios/<int:id_funcionario>', methods=['DELETE'])
def deleteFuncionario(id_funcionario):
    """Elimina un funcionario y todos sus datos asociados"""
    funcionariodao = FuncionarioDao()

    try:
        if funcionariodao.deleteFuncionario(id_funcionario):
            return jsonify({
                'success': True,
                'mensaje': f'Funcionario con ID {id_funcionario} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el funcionario con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar funcionario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500