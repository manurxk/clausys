from flask import Blueprint, request, jsonify, current_app as app
from app.dao.seguridad.usuario.UsuarioDao import UsuarioDao

usuarioapi = Blueprint('usuarioapi', __name__)

# ============================================
# OBTENER TODOS LOS USUARIOS
# ============================================
@usuarioapi.route('/usuarios', methods=['GET'])
def getUsuarios():
    """Obtiene la lista completa de usuarios"""
    usuariodao = UsuarioDao()
    
    try:
        usuarios = usuariodao.getUsuarios()
        
        return jsonify({
            'success': True,
            'data': usuarios,
            'error': None
        }), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener usuarios: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ============================================
# OBTENER USUARIO POR ID
# ============================================
@usuarioapi.route('/usuarios/<int:id_usuario>', methods=['GET'])
def getUsuario(id_usuario):
    """Obtiene un usuario específico por su ID"""
    usuariodao = UsuarioDao()
    
    try:
        usuario = usuariodao.getUsuarioById(id_usuario)
        
        if usuario:
            return jsonify({
                'success': True,
                'data': usuario,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el usuario con el ID proporcionado.'
            }), 404
    
    except Exception as e:
        app.logger.error(f"Error al obtener usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ============================================
# OBTENER FUNCIONARIOS SIN USUARIO
# ============================================
@usuarioapi.route('/funcionarios/sin-usuario', methods=['GET'])
def getFuncionariosSinUsuario():
    """Obtiene funcionarios que no tienen usuario asignado"""
    usuariodao = UsuarioDao()
    
    try:
        funcionarios = usuariodao.getFuncionariosSinUsuario()
        
        return jsonify({
            'success': True,
            'data': funcionarios,
            'error': None
        }), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener funcionarios sin usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ============================================
# VALIDAR USERNAME DISPONIBLE
# ============================================
@usuarioapi.route('/usuarios/validar-username', methods=['POST'])
def validarUsername():
    """Valida que un username esté disponible"""
    data = request.get_json()
    usuariodao = UsuarioDao()
    
    username = data.get('username')
    id_usuario = data.get('id_usuario')  # Para edición
    
    if not username:
        return jsonify({
            'success': False,
            'error': 'El username es requerido'
        }), 400
    
    try:
        disponible = usuariodao.validarUsernameDisponible(username, id_usuario)
        
        return jsonify({
            'success': True,
            'data': {'disponible': disponible},
            'error': None
        }), 200
    
    except Exception as e:
        app.logger.error(f"Error al validar username: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error al validar el username.'
        }), 500


# ============================================
# CREAR NUEVO USUARIO
# ============================================
@usuarioapi.route('/usuarios', methods=['POST'])
def addUsuario():
    """Crea un nuevo usuario"""
    data = request.get_json()
    usuariodao = UsuarioDao()
    
    # Campos obligatorios
    campos_requeridos = ['username', 'password', 'id_funcionario', 'id_grupo']
    
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio.'
            }), 400
    
    # Validar longitud de contraseña
    if len(data['password']) < 6:
        return jsonify({
            'success': False,
            'error': 'La contraseña debe tener al menos 6 caracteres.'
        }), 400
    
    # Validar confirmación de contraseña
    if data.get('password') != data.get('password_confirmacion'):
        return jsonify({
            'success': False,
            'error': 'Las contraseñas no coinciden.'
        }), 400
    
    try:
        usuario_id = usuariodao.guardarUsuario(
            username=data['username'],
            password=data['password'],
            id_funcionario=data['id_funcionario'],
            id_grupo=data['id_grupo'],
            usu_estado=data.get('usu_estado', True),
            creacion_usuario=data.get('creacion_usuario', 1)
        )
        
        if usuario_id:
            return jsonify({
                'success': True,
                'data': {
                    'id_usuario': usuario_id,
                    'mensaje': 'Usuario creado exitosamente'
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo crear el usuario. Verifique que el username no exista o que el funcionario no tenga usuario asignado.'
            }), 500
    
    except Exception as e:
        app.logger.error(f"Error al crear usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Ocurrió un error interno: {str(e)}'
        }), 500


# ============================================
# ACTUALIZAR USUARIO EXISTENTE
# ============================================
@usuarioapi.route('/usuarios/<int:id_usuario>', methods=['PUT'])
def updateUsuario(id_usuario):
    """Actualiza un usuario existente"""
    data = request.get_json()
    usuariodao = UsuarioDao()
    
    # Verificar que el usuario existe
    usuario_existente = usuariodao.getUsuarioById(id_usuario)
    if not usuario_existente:
        return jsonify({
            'success': False,
            'error': 'No se encontró el usuario con el ID proporcionado.'
        }), 404
    
    # Campos obligatorios
    if not data.get('username') or not data.get('id_grupo'):
        return jsonify({
            'success': False,
            'error': 'Username y grupo son obligatorios.'
        }), 400
    
    # Si hay contraseña, validar
    password = None
    if data.get('password'):
        if len(data['password']) < 6:
            return jsonify({
                'success': False,
                'error': 'La contraseña debe tener al menos 6 caracteres.'
            }), 400
        
        if data.get('password') != data.get('password_confirmacion'):
            return jsonify({
                'success': False,
                'error': 'Las contraseñas no coinciden.'
            }), 400
        
        password = data['password']
    
    try:
        resultado = usuariodao.updateUsuario(
            id_usuario=id_usuario,
            username=data['username'],
            id_grupo=data['id_grupo'],
            usu_estado=data.get('usu_estado', True),
            password=password,
            modificacion_usuario=data.get('modificacion_usuario', 1)
        )
        
        if resultado:
            return jsonify({
                'success': True,
                'data': {
                    'id_usuario': id_usuario,
                    'mensaje': 'Usuario actualizado exitosamente'
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo actualizar el usuario. Verifique que el username no esté en uso.'
            }), 500
    
    except Exception as e:
        app.logger.error(f"Error al actualizar usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Ocurrió un error interno: {str(e)}'
        }), 500


# ============================================
# DESACTIVAR USUARIO (SOFT DELETE)
# ============================================
@usuarioapi.route('/usuarios/<int:id_usuario>/desactivar', methods=['PATCH'])
def desactivarUsuario(id_usuario):
    """Desactiva un usuario (soft delete)"""
    usuariodao = UsuarioDao()
    
    try:
        if usuariodao.desactivarUsuario(id_usuario):
            return jsonify({
                'success': True,
                'mensaje': f'Usuario {id_usuario} desactivado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo desactivar el usuario.'
            }), 500
    
    except Exception as e:
        app.logger.error(f"Error al desactivar usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ============================================
# RESETEAR INTENTOS DE LOGIN
# ============================================
@usuarioapi.route('/usuarios/<int:id_usuario>/resetear-intentos', methods=['PATCH'])
def resetearIntentos(id_usuario):
    """Resetea el contador de intentos fallidos de login"""
    usuariodao = UsuarioDao()
    
    try:
        if usuariodao.resetearIntentos(id_usuario):
            return jsonify({
                'success': True,
                'mensaje': f'Intentos reseteados para usuario {id_usuario}.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo resetear los intentos.'
            }), 500
    
    except Exception as e:
        app.logger.error(f"Error al resetear intentos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500