import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class ConsultorioDao:

    # ============================
    # OBTENER
    # ============================

    def getConsultorios(self):
        sql = """
        SELECT id_consultorio, des_consultorio, est_consultorio
        FROM consultorios
        ORDER BY id_consultorio
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            consultorios = cur.fetchall()
            return [{'id': c[0], 'descripcion': c[1], 'estado': c[2]} for c in consultorios]
        except Exception as e:
            app.logger.error(f"Error al obtener consultorios: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getConsultorioById(self, id_consultorio):
        sql = """
        SELECT id_consultorio, des_consultorio, est_consultorio
        FROM consultorios
        WHERE id_consultorio = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_consultorio,))
            c = cur.fetchone()
            if c:
                return {"id": c[0], "descripcion": c[1], "estado": c[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener consultorio: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def consultorioExiste(self, descripcion):
        """Verifica si ya existe el consultorio con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM consultorios WHERE LOWER(des_consultorio) = LOWER(%s)"
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

    def guardarConsultorio(self, descripcion, estado=True, usuario=1):
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números y acentos")
            return False
        if self.consultorioExiste(descripcion):
            app.logger.warning("El consultorio ya existe")
            return False

        sql = """
        INSERT INTO consultorios (des_consultorio, est_consultorio, creacion_usuario)
        VALUES (%s, %s, %s)
        RETURNING id_consultorio
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado, usuario))
            id_consultorio = cur.fetchone()[0]
            con.commit()
            return id_consultorio
        except Exception as e:
            app.logger.error(f"Error al insertar consultorio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateConsultorio(self, id_consultorio, descripcion, estado=True, usuario=1):
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida")
            return False

        sql = """
        UPDATE consultorios
        SET des_consultorio = %s,
            est_consultorio = %s,
            modificacion_fecha = CURRENT_DATE,
            modificacion_hora = CURRENT_TIME,
            modificacion_usuario = %s
        WHERE id_consultorio = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado, usuario, id_consultorio))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar consultorio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteConsultorio(self, id_consultorio):
        sql = "DELETE FROM consultorios WHERE id_consultorio = %s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_consultorio,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar consultorio: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
