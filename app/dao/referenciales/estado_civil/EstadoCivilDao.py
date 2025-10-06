# Data Access Object - DAO para estados civiles
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class EstadoCivilDao:

    def getEstadosCiviles(self):
        sql = """
        SELECT id_estado_civil, des_estado_civil, est_estado_civil
        FROM estados_civiles
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            estados = cur.fetchall()
            return [{'id': e[0], 'descripcion': e[1], 'estado': e[2]} for e in estados]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los estados civiles: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getEstadoCivilById(self, id_estado_civil):
        sql = """
        SELECT id_estado_civil, des_estado_civil, est_estado_civil
        FROM estados_civiles
        WHERE id_estado_civil=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_estado_civil,))
            estado = cur.fetchone()
            if estado:
                return {"id": estado[0], "descripcion": estado[1], "estado": estado[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener estado civil: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def estadoCivilExiste(self, descripcion):
        """Verifica si ya existe un estado civil con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM estados_civiles WHERE LOWER(des_estado_civil)=LOWER(%s)"
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
        """Permite solo letras con acentos y espacios (sin números ni símbolos)."""
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$"
        return bool(re.match(patron, descripcion))

    # ============================
    # CRUD
    # ============================

    def guardarEstadoCivil(self, descripcion, estado=True):
        # Validaciones
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras y acentos")
            return False
        if self.estadoCivilExiste(descripcion):
            app.logger.warning("El estado civil ya existe")
            return False

        sql = """
        INSERT INTO estados_civiles(des_estado_civil, est_estado_civil)
        VALUES(%s, %s)
        RETURNING id_estado_civil
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado))
            id_estado_civil = cur.fetchone()[0]
            con.commit()
            return id_estado_civil
        except Exception as e:
            app.logger.error(f"Error al insertar estado civil: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateEstadoCivil(self, id_estado_civil, descripcion, estado=True):
        # Validaciones
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida")
            return False

        sql = """
        UPDATE estados_civiles
        SET des_estado_civil=%s, est_estado_civil=%s
        WHERE id_estado_civil=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado, id_estado_civil))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar estado civil: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteEstadoCivil(self, id_estado_civil):
        sql = "DELETE FROM estados_civiles WHERE id_estado_civil=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_estado_civil,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar estado civil: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
