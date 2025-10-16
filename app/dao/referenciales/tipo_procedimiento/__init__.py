import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class EspecialidadDao:

    # ============================
    # GET todas
    # ============================
    def getEspecialidades(self):
        sql = """
        SELECT id_especialidad, des_especialidad, est_especialidad
        FROM especialidades
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            especialidades = cur.fetchall()
            return [
                {
                    'id': e[0],
                    'nombre': e[1],
                    'estado': e[2]
                } for e in especialidades
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener todas las especialidades: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    # ============================
    # GET por ID
    # ============================
    def getEspecialidadById(self, id_especialidad):
        sql = """
        SELECT id_especialidad, des_especialidad, est_especialidad
        FROM especialidades
        WHERE id_especialidad=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_especialidad,))
            e = cur.fetchone()
            if e:
                return {
                    'id': e[0],
                    'nombre': e[1],
                    'estado': e[2]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener especialidad: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================
    def especialidadExiste(self, nombre):
        sql = "SELECT 1 FROM especialidades WHERE LOWER(des_especialidad)=LOWER(%s)"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre,))
            return cur.fetchone() is not None
        finally:
            cur.close()
            con.close()

    def validarTexto(self, texto):
        """Solo letras, números, acentos y espacios."""
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 ]+$"
        return bool(re.match(patron, texto))

    # ============================
    # INSERT
    # ============================
    def guardarEspecialidad(self, nombre, estado=True):
        if not self.validarTexto(nombre):
            app.logger.warning("Nombre inválido: solo letras, números y acentos")
            return False
        if self.especialidadExiste(nombre):
            app.logger.warning("La especialidad ya existe")
            return False

        sql = """
        INSERT INTO especialidades(des_especialidad, est_especialidad)
        VALUES(%s, %s)
        RETURNING id_especialidad
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre, estado))
            id_especialidad = cur.fetchone()[0]
            con.commit()
            return id_especialidad
        except Exception as e:
            app.logger.error(f"Error al insertar especialidad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    # ============================
    # UPDATE
    # ============================
    def updateEspecialidad(self, id_especialidad, nombre, estado=True):
        if not self.validarTexto(nombre):
            app.logger.warning("Nombre inválido")
            return False

        sql = """
        UPDATE especialidades
        SET des_especialidad=%s, est_especialidad=%s
        WHERE id_especialidad=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (nombre, estado, id_especialidad))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar especialidad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    # ============================
    # DELETE
    # ============================
    def deleteEspecialidad(self, id_especialidad):
        sql = "DELETE FROM especialidades WHERE id_especialidad=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_especialidad,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar especialidad: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
