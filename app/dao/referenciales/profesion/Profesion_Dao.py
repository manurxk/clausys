import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class ProfesionDao:

    # ============================
    # LISTAR TODAS
    # ============================
    def getProfesiones(self):
        sql = """
        SELECT id_profesion, des_profesion, est_profesion
        FROM profesiones
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            profesiones = cur.fetchall()
            return [{'id': p[0], 'descripcion': p[1], 'estado': p[2]} for p in profesiones]
        except Exception as e:
            app.logger.error(f"Error al obtener todas las profesiones: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    # ============================
    # OBTENER POR ID
    # ============================
    def getProfesionById(self, id_profesion):
        sql = """
        SELECT id_profesion, des_profesion, est_profesion
        FROM profesiones
        WHERE id_profesion=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_profesion,))
            profesion = cur.fetchone()
            if profesion:
                return {"id": profesion[0], "descripcion": profesion[1], "estado": profesion[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener profesión: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================
    def profesionExiste(self, descripcion):
        """Verifica si ya existe la profesión (case-insensitive)."""
        sql = "SELECT 1 FROM profesiones WHERE LOWER(des_profesion)=LOWER(%s)"
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
    def guardarProfesion(self, descripcion, estado=True):
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números y acentos")
            return False
        if self.profesionExiste(descripcion):
            app.logger.warning("La profesión ya existe")
            return False

        sql = """
        INSERT INTO profesiones(des_profesion, est_profesion)
        VALUES(%s, %s)
        RETURNING id_profesion
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado))
            id_profesion = cur.fetchone()[0]
            con.commit()
            return id_profesion
        except Exception as e:
            app.logger.error(f"Error al insertar profesión: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateProfesion(self, id_profesion, descripcion, estado=True):
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida")
            return False

        sql = """
        UPDATE profesiones
        SET des_profesion=%s, est_profesion=%s
        WHERE id_profesion=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado, id_profesion))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar profesión: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteProfesion(self, id_profesion):
        sql = "DELETE FROM profesiones WHERE id_profesion=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_profesion,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar profesión: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
