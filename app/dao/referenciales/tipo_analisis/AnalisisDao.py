import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class TipoAnalisisDao:

    def getTiposAnalisis(self):
        sql = """
        SELECT id_tipo_analisis, des_tipo_analisis, est_tipo_analisis
        FROM tipos_analisis
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            tipos_analisis = cur.fetchall()
            return [{'id': t[0], 'descripcion': t[1], 'estado': t[2]} for t in tipos_analisis]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los tipos de análisis: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTipoAnalisisById(self, id_tipo_analisis):
        sql = """
        SELECT id_tipo_analisis, des_tipo_analisis, est_tipo_analisis
        FROM tipos_analisis
        WHERE id_tipo_analisis=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_analisis,))
            tipo_analisis = cur.fetchone()
            if tipo_analisis:
                return {"id": tipo_analisis[0], "descripcion": tipo_analisis[1], "estado": tipo_analisis[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener tipo de análisis: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def tipoAnalisisExiste(self, descripcion):
        """Verifica si ya existe el tipo de análisis con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM tipos_analisis WHERE LOWER(des_tipo_analisis)=LOWER(%s)"
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

    def guardarTipoAnalisis(self, descripcion, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False
        
        if self.tipoAnalisisExiste(descripcion):
            app.logger.warning("El tipo de análisis ya existe")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido: debe ser 'A' (Activo) o 'I' (Inactivo)")
            return False

        sql = """
        INSERT INTO tipos_analisis(des_tipo_analisis, est_tipo_analisis, usuario_creacion)
        VALUES(%s, %s, %s)
        RETURNING id_tipo_analisis
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario))
            id_tipo_analisis = cur.fetchone()[0]
            con.commit()
            app.logger.info(f"Tipo de análisis insertado con ID: {id_tipo_analisis}")
            return id_tipo_analisis
        except Exception as e:
            app.logger.error(f"Error al insertar tipo de análisis: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateTipoAnalisis(self, id_tipo_analisis, descripcion, estado='A'):
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
        UPDATE tipos_analisis
        SET des_tipo_analisis=%s, est_tipo_analisis=%s, usuario_modificacion=%s, fecha_modificacion=CURRENT_TIMESTAMP
        WHERE id_tipo_analisis=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario, id_tipo_analisis))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Tipo de análisis {id_tipo_analisis} actualizado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar tipo de análisis: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteTipoAnalisis(self, id_tipo_analisis):
        sql = "DELETE FROM tipos_analisis WHERE id_tipo_analisis=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_tipo_analisis,))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Tipo de análisis {id_tipo_analisis} eliminado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar tipo de análisis: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
