import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class TipoEstudioDao:

    def getTiposEstudios(self):
        sql = """
        SELECT id_tipo_estudio, des_tipo_estudio, est_tipo_estudio
        FROM tipos_estudios
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            tipos_estudios = cur.fetchall()
            return [{'id': t[0], 'descripcion': t[1], 'estado': t[2]} for t in tipos_estudios]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los tipos de estudios: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTipoEstudioById(self, id_tipo_estudio):
        sql = """
        SELECT id_tipo_estudio, des_tipo_estudio, est_tipo_estudio
        FROM tipos_estudios
        WHERE id_tipo_estudio=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_estudio,))
            tipo_estudio = cur.fetchone()
            if tipo_estudio:
                return {"id": tipo_estudio[0], "descripcion": tipo_estudio[1], "estado": tipo_estudio[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener tipo de estudio: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def tipoEstudioExiste(self, descripcion):
        """Verifica si ya existe el tipo de estudio con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM tipos_estudios WHERE LOWER(des_tipo_estudio)=LOWER(%s)"
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

    def guardarTipoEstudio(self, descripcion, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False
        
        if self.tipoEstudioExiste(descripcion):
            app.logger.warning("El tipo de estudio ya existe")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido: debe ser 'A' (Activo) o 'I' (Inactivo)")
            return False

        sql = """
        INSERT INTO tipos_estudios(des_tipo_estudio, est_tipo_estudio, usuario_creacion)
        VALUES(%s, %s, %s)
        RETURNING id_tipo_estudio
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario))
            id_tipo_estudio = cur.fetchone()[0]
            con.commit()
            app.logger.info(f"Tipo de estudio insertado con ID: {id_tipo_estudio}")
            return id_tipo_estudio
        except Exception as e:
            app.logger.error(f"Error al insertar tipo de estudio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateTipoEstudio(self, id_tipo_estudio, descripcion, estado='A'):
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
        UPDATE tipos_estudios
        SET des_tipo_estudio=%s, est_tipo_estudio=%s, 
            usuario_modificacion=%s, fecha_modificacion=CURRENT_TIMESTAMP
        WHERE id_tipo_estudio=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario, id_tipo_estudio))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Tipo de estudio {id_tipo_estudio} actualizado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar tipo de estudio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteTipoEstudio(self, id_tipo_estudio):
        sql = "DELETE FROM tipos_estudios WHERE id_tipo_estudio=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_estudio,))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Tipo de estudio {id_tipo_estudio} eliminado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar tipo de estudio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
