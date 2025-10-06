from flask import current_app as app
from app.conexion.Conexion import Conexion
from werkzeug.security import generate_password_hash, check_password_hash

class UsuarioDao:
    
    def getUsuarios(self):
        """Obtiene todos los usuarios con sus datos relacionados"""
        usuariosSQL = """
            SELECT 
                u.id_usuario,
                u.usu_nick,
                u.usu_estado,
                u.usu_nro_intentos,
                p.per_nombre || ' ' || p.per_apellido AS funcionario,
                c.des_cargo,
                g.des_grupo,
                u.creacion_fecha,
                f.id_funcionario
            FROM usuarios u
            JOIN funcionarios f ON u.id_funcionario = f.id_funcionario
            JOIN personas p ON f.id_persona = p.id_persona
            JOIN cargos c ON f.id_cargo = c.id_cargo
            JOIN grupos g ON u.id_grupo = g.id_grupo
            ORDER BY u.id_usuario DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(usuariosSQL)
            usuarios = cur.fetchall()
            
            return [{
                'id_usuario': u[0],
                'username': u[1],
                'activo': u[2],
                'intentos': u[3],
                'funcionario': u[4],
                'cargo': u[5],
                'grupo': u[6],
                'fecha_creacion': u[7].strftime('%d/%m/%Y') if u[7] else None,
                'id_funcionario': u[8]
            } for u in usuarios]
            
        except Exception as e:
            app.logger.error(f"Error al obtener usuarios: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getUsuarioById(self, id_usuario):
        """Obtiene un usuario específico por ID"""
        usuarioSQL = """
            SELECT 
                u.id_usuario,
                u.usu_nick,
                u.usu_estado,
                u.usu_nro_intentos,
                u.id_funcionario,
                u.id_grupo,
                p.per_nombre || ' ' || p.per_apellido AS funcionario,
                c.des_cargo,
                g.des_grupo
            FROM usuarios u
            JOIN funcionarios f ON u.id_funcionario = f.id_funcionario
            JOIN personas p ON f.id_persona = p.id_persona
            JOIN cargos c ON f.id_cargo = c.id_cargo
            JOIN grupos g ON u.id_grupo = g.id_grupo
            WHERE u.id_usuario = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(usuarioSQL, (id_usuario,))
            u = cur.fetchone()
            
            if not u:
                return None
            
            return {
                'id_usuario': u[0],
                'username': u[1],
                'activo': u[2],
                'intentos': u[3],
                'id_funcionario': u[4],
                'id_grupo': u[5],
                'funcionario': u[6],
                'cargo': u[7],
                'grupo': u[8]
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener usuario por ID: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def getFuncionariosSinUsuario(self):
        """Obtiene funcionarios que NO tienen usuario asignado"""
        funcionariosSQL = """
            SELECT 
                f.id_funcionario,
                p.per_nombre || ' ' || p.per_apellido AS nombre_completo,
                c.des_cargo,
                p.per_cedula
            FROM funcionarios f
            JOIN personas p ON f.id_persona = p.id_persona
            JOIN cargos c ON f.id_cargo = c.id_cargo
            LEFT JOIN usuarios u ON f.id_funcionario = u.id_funcionario
            WHERE f.fun_estado = TRUE 
              AND u.id_usuario IS NULL
            ORDER BY p.per_nombre
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(funcionariosSQL)
            funcionarios = cur.fetchall()
            
            return [{
                'id_funcionario': f[0],
                'nombre_completo': f[1],
                'cargo': f[2],
                'cedula': f[3]
            } for f in funcionarios]
            
        except Exception as e:
            app.logger.error(f"Error al obtener funcionarios sin usuario: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def validarUsernameDisponible(self, username, id_usuario=None):
        """Valida que el username no esté en uso"""
        if id_usuario:
            sql = "SELECT id_usuario FROM usuarios WHERE usu_nick = %s AND id_usuario != %s"
            params = (username, id_usuario)
        else:
            sql = "SELECT id_usuario FROM usuarios WHERE usu_nick = %s"
            params = (username,)
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(sql, params)
            resultado = cur.fetchone()
            return resultado is None
            
        except Exception as e:
            app.logger.error(f"Error al validar username: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def guardarUsuario(self, username, password, id_funcionario, id_grupo, 
                       usu_estado=True, creacion_usuario=1):
        """Crea un nuevo usuario con contraseña encriptada"""
        
        # Validar que el username no exista
        if not self.validarUsernameDisponible(username):
            app.logger.error(f"El username {username} ya existe")
            return None
        
        # Validar que el funcionario no tenga usuario
        checkFuncionarioSQL = """
            SELECT id_usuario FROM usuarios WHERE id_funcionario = %s
        """
        
        insertUsuarioSQL = """
            INSERT INTO usuarios(usu_nick, usu_clave, id_funcionario, id_grupo, 
                               usu_estado, creacion_usuario, creacion_fecha, creacion_hora)
            VALUES(%s, %s, %s, %s, %s, %s, CURRENT_DATE, CURRENT_TIME)
            RETURNING id_usuario
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            # Verificar que el funcionario no tenga usuario
            cur.execute(checkFuncionarioSQL, (id_funcionario,))
            if cur.fetchone():
                app.logger.error(f"El funcionario {id_funcionario} ya tiene un usuario asignado")
                return None
            
            # Encriptar contraseña
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            
            # Insertar usuario
            cur.execute(insertUsuarioSQL, (username, password_hash, id_funcionario, 
                                          id_grupo, usu_estado, creacion_usuario))
            usuario_id = cur.fetchone()[0]
            
            con.commit()
            app.logger.info(f"Usuario {username} creado exitosamente con ID: {usuario_id}")
            return usuario_id
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al guardar usuario: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def updateUsuario(self, id_usuario, username, id_grupo, usu_estado, 
                     password=None, modificacion_usuario=1):
        """Actualiza un usuario existente (NO cambia el funcionario)"""
        
        # Validar username disponible
        if not self.validarUsernameDisponible(username, id_usuario):
            app.logger.error(f"El username {username} ya existe")
            return False
        
        # Si hay contraseña, actualizar todo incluyendo contraseña
        if password:
            updateSQL = """
                UPDATE usuarios
                SET usu_nick = %s, 
                    usu_clave = %s,
                    id_grupo = %s, 
                    usu_estado = %s,
                    modificacion_fecha = CURRENT_DATE,
                    modificacion_hora = CURRENT_TIME,
                    modificacion_usuario = %s
                WHERE id_usuario = %s
            """
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            params = (username, password_hash, id_grupo, usu_estado, modificacion_usuario, id_usuario)
        else:
            # Sin contraseña, solo actualizar los demás campos
            updateSQL = """
                UPDATE usuarios
                SET usu_nick = %s, 
                    id_grupo = %s, 
                    usu_estado = %s,
                    modificacion_fecha = CURRENT_DATE,
                    modificacion_hora = CURRENT_TIME,
                    modificacion_usuario = %s
                WHERE id_usuario = %s
            """
            params = (username, id_grupo, usu_estado, modificacion_usuario, id_usuario)
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(updateSQL, params)
            con.commit()
            app.logger.info(f"Usuario {id_usuario} actualizado exitosamente")
            return True
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al actualizar usuario: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def desactivarUsuario(self, id_usuario):
        """Desactiva un usuario (soft delete)"""
        desactivarSQL = """
            UPDATE usuarios
            SET usu_estado = FALSE,
                modificacion_fecha = CURRENT_DATE,
                modificacion_hora = CURRENT_TIME
            WHERE id_usuario = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(desactivarSQL, (id_usuario,))
            con.commit()
            app.logger.info(f"Usuario {id_usuario} desactivado exitosamente")
            return True
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al desactivar usuario: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def resetearIntentos(self, id_usuario):
        """Resetea el contador de intentos fallidos de login"""
        resetSQL = """
            UPDATE usuarios
            SET usu_nro_intentos = 0,
                modificacion_fecha = CURRENT_DATE,
                modificacion_hora = CURRENT_TIME
            WHERE id_usuario = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(resetSQL, (id_usuario,))
            con.commit()
            app.logger.info(f"Intentos reseteados para usuario {id_usuario}")
            return True
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al resetear intentos: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()