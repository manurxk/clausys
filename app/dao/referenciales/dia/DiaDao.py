# Data Access Object - DAO
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class DiaSemanaDao:

    # ============================
    # OBTENER REGISTROS
    # ============================

    def getDias(self):
        sql = """
        SELECT id_dia_semana, des_dia_semana, dia_orden, est_dia_semana
        FROM dias_semana
        ORDER BY dia_orden
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            dias = cur.fetchall()
            return [
                {
                    'id': d[0],
                    'descripcion': d[1],
                    'orden': d[2],
                    'estado': d[3]
                } for d in dias
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener días: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getDiaById(self, id_dia_semana):
        sql = """
        SELECT id_dia_semana, des_dia_semana, dia_orden, est_dia_semana
        FROM dias_semana
        WHERE id_dia_semana=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_dia_semana,))
            dia = cur.fetchone()
            if dia:
                return {
                    'id': dia[0],
                    'descripcion': dia[1],
                    'orden': dia[2],
                    'estado': dia[3]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener día: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def diaExiste(self, descripcion):
        sql = "SELECT 1 FROM dias_semana WHERE LOWER(des_dia_semana)=LOWER(%s)"
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
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$"
        return bool(re.match(patron, descripcion))

    # ============================
    # CRUD
    # ============================

    def guardarDia(self, descripcion, orden, estado=True):
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras y acentos")
            return False
        if self.diaExiste(descripcion):
            app.logger.warning("El día ya existe")
            return False

        sql = """
        INSERT INTO dias_semana(des_dia_semana, dia_orden, est_dia_semana)
        VALUES(%s, %s, %s)
        RETURNING id_dia_semana
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, orden, estado))
            id_dia = cur.fetchone()[0]
            con.commit()
            return id_dia
        except Exception as e:
            app.logger.error(f"Error al insertar día: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateDia(self, id_dia_semana, descripcion, orden, estado=True):
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida")
            return False

        sql = """
        UPDATE dias_semana
        SET des_dia_semana=%s, dia_orden=%s, est_dia_semana=%s
        WHERE id_dia_semana=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, orden, estado, id_dia_semana))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar día: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteDia(self, id_dia_semana):
        sql = "DELETE FROM dias_semana WHERE id_dia_semana=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_dia_semana,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar día: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
