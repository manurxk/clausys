import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class TipoTratamientoDao:

    def getTiposTratamientos(self):
        sql = """
        SELECT id_tipo_tratamiento, des_tipo_tratamiento, est_tipo_tratamiento
        FROM tipos_tratamientos
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            tipos_tratamientos = cur.fetchall()
            return [{'id': t[0], 'descripcion': t[1], 'estado': t[2]} for t in tipos_tratamientos]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los tipos de tratamientos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTipoTratamientoById(self, id_tipo_tratamiento):
        sql = """
        SELECT id_tipo_tratamiento, des_tipo_tratamiento, est_tipo_tratamiento
        FROM tipos_tratamientos
        WHERE id_tipo_tratamiento=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_tratamiento,))
            tipo_tratamiento = cur.fetchone()
            if tipo_tratamiento:
                return {"id": tipo_tratamiento[0], "descripcion": tipo_tratamiento[1], "estado": tipo_tratamiento[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener tipo de tratamiento: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def tipoTratamientoExiste(self, descripcion):
        """Verifica si ya existe el tipo de tratamiento con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM tipos_tratamientos WHERE LOWER(des_tipo_tratamiento)=LOWER(%s)"
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

    def guardarTipoTratamiento(self, descripcion, estado='A'):
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False
        
        if self.tipoTratamientoExiste(descripcion):
            app.logger.warning("El tipo de tratamiento ya existe")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido: debe ser 'A' o 'I'")
            return False

        sql = """
        INSERT INTO tipos_tratamientos(des_tipo_tratamiento, est_tipo_tratamiento, usuario_creacion)
        VALUES(%s, %s, %s)
        RETURNING id_tipo_tratamiento
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario))
            id_tipo_tratamiento = cur.fetchone()[0]
            con.commit()
            app.logger.info(f"Tipo de tratamiento insertado con ID: {id_tipo_tratamiento}")
            return id_tipo_tratamiento
        except Exception as e:
            app.logger.error(f"Error al insertar tipo de tratamiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateTipoTratamiento(self, id_tipo_tratamiento, descripcion, estado='A'):
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido")
            return False

        sql = """
        UPDATE tipos_tratamientos
        SET des_tipo_tratamiento=%s, est_tipo_tratamiento=%s, 
            usuario_modificacion=%s, fecha_modificacion=CURRENT_TIMESTAMP
        WHERE id_tipo_tratamiento=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario, id_tipo_tratamiento))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Tipo de tratamiento {id_tipo_tratamiento} actualizado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar tipo de tratamiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteTipoTratamiento(self, id_tipo_tratamiento):
        sql = "DELETE FROM tipos_tratamientos WHERE id_tipo_tratamiento=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_tratamiento,))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Tipo de tratamiento {id_tipo_tratamiento} eliminado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar tipo de tratamiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
