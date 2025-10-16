import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class TipoProcedimientoDao:

    def getTiposProcedimientos(self):
        sql = """
        SELECT id_tipo_procedimiento, des_tipo_procedimiento, est_tipo_procedimiento
        FROM tipos_procedimientos
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            tipos_procedimientos = cur.fetchall()
            return [{'id': t[0], 'descripcion': t[1], 'estado': t[2]} for t in tipos_procedimientos]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los tipos de procedimientos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTipoProcedimientoById(self, id_tipo_procedimiento):
        sql = """
        SELECT id_tipo_procedimiento, des_tipo_procedimiento, est_tipo_procedimiento
        FROM tipos_procedimientos
        WHERE id_tipo_procedimiento=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_procedimiento,))
            tipo_procedimiento = cur.fetchone()
            if tipo_procedimiento:
                return {"id": tipo_procedimiento[0], "descripcion": tipo_procedimiento[1], "estado": tipo_procedimiento[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener tipo de procedimiento: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def tipoProcedimientoExiste(self, descripcion):
        """Verifica si ya existe el tipo de procedimiento con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM tipos_procedimientos WHERE LOWER(des_tipo_procedimiento)=LOWER(%s)"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion,))
            return cur.fetchone() is not None
        finally:
            cur.close()
            con.close()

    def validarDescripcion(self, descripcion):
        """Permite solo letras, números, acentos, espacios y puntos."""
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 .]+$"
        return bool(re.match(patron, descripcion))

    # ============================
    # CRUD
    # ============================

    def guardarTipoProcedimiento(self, descripcion, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False
        
        if self.tipoProcedimientoExiste(descripcion):
            app.logger.warning("El tipo de procedimiento ya existe")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido: debe ser 'A' (Activo) o 'I' (Inactivo)")
            return False

        sql = """
        INSERT INTO tipos_procedimientos(des_tipo_procedimiento, est_tipo_procedimiento, usuario_creacion)
        VALUES(%s, %s, %s)
        RETURNING id_tipo_procedimiento
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario))
            id_tipo_procedimiento = cur.fetchone()[0]
            con.commit()
            app.logger.info(f"Tipo de procedimiento insertado con ID: {id_tipo_procedimiento}")
            return id_tipo_procedimiento
        except Exception as e:
            app.logger.error(f"Error al insertar tipo de procedimiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateTipoProcedimiento(self, id_tipo_procedimiento, descripcion, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido")
            return False

        sql = """
        UPDATE tipos_procedimientos
        SET des_tipo_procedimiento=%s, est_tipo_procedimiento=%s, 
            usuario_modificacion=%s, fecha_modificacion=CURRENT_TIMESTAMP
        WHERE id_tipo_procedimiento=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario, id_tipo_procedimiento))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Tipo de procedimiento {id_tipo_procedimiento} actualizado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar tipo de procedimiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteTipoProcedimiento(self, id_tipo_procedimiento):
        sql = "DELETE FROM tipos_procedimientos WHERE id_tipo_procedimiento=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_procedimiento,))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Tipo de procedimiento {id_tipo_procedimiento} eliminado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar tipo de procedimiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
