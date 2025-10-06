# Data access object - DAO
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class ModuloDao:

    def getModulos(self):
        sql = """
        SELECT id_modulo, des_modulo, est_modulo
        FROM modulos
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            modulos = cur.fetchall()
            return [{'id': m[0], 'descripcion': m[1], 'estado': m[2]} for m in modulos]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los módulos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getModuloById(self, id_modulo):
        sql = """
        SELECT id_modulo, des_modulo, est_modulo
        FROM modulos
        WHERE id_modulo=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_modulo,))
            modulo = cur.fetchone()
            if modulo:
                return {"id": modulo[0], "descripcion": modulo[1], "estado": modulo[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener módulo: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def moduloExiste(self, descripcion):
        """Verifica si ya existe el módulo con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM modulos WHERE LOWER(des_modulo)=LOWER(%s)"
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
        """Permite solo letras, números, acentos y espacios."""
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]+$"
        return bool(re.match(patron, descripcion))

    # ============================
    # CRUD
    # ============================

    def guardarModulo(self, descripcion, estado=True):
        # Validaciones
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números y acentos")
            return False
        if self.moduloExiste(descripcion):
            app.logger.warning("El módulo ya existe")
            return False

        sql = """
        INSERT INTO modulos(des_modulo, est_modulo)
        VALUES(%s, %s)
        RETURNING id_modulo
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado))
            id_modulo = cur.fetchone()[0]
            con.commit()
            return id_modulo
        except Exception as e:
            app.logger.error(f"Error al insertar módulo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateModulo(self, id_modulo, descripcion, estado=True):
        # Validaciones
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida")
            return False

        sql = """
        UPDATE modulos
        SET des_modulo=%s, est_modulo=%s
        WHERE id_modulo=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado, id_modulo))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar módulo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteModulo(self, id_modulo):
        sql = "DELETE FROM modulos WHERE id_modulo=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_modulo,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar módulo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
