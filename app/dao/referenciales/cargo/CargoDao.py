# Data access object - DAO
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class CargoDao:

    def getCargos(self):
        sql = """
        SELECT id_cargo, des_cargo, est_cargo
        FROM cargos
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            cargos = cur.fetchall()
            return [{'id': c[0], 'descripcion': c[1], 'estado': c[2]} for c in cargos]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los cargos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getCargoById(self, id_cargo):
        sql = """
        SELECT id_cargo, des_cargo, est_cargo
        FROM cargos
        WHERE id_cargo=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_cargo,))
            cargo = cur.fetchone()
            if cargo:
                return {"id": cargo[0], "descripcion": cargo[1], "estado": cargo[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener cargo: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def cargoExiste(self, descripcion):
        """Verifica si ya existe el cargo con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM cargos WHERE LOWER(des_cargo)=LOWER(%s)"
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

    def guardarCargo(self, descripcion, estado=True):
        # Validaciones
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números y acentos")
            return False
        if self.cargoExiste(descripcion):
            app.logger.warning("El cargo ya existe")
            return False

        sql = """
        INSERT INTO cargos(des_cargo, est_cargo)
        VALUES(%s, %s)
        RETURNING id_cargo
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado))
            id_cargo = cur.fetchone()[0]
            con.commit()
            return id_cargo
        except Exception as e:
            app.logger.error(f"Error al insertar cargo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateCargo(self, id_cargo, descripcion, estado=True):
        # Validaciones
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida")
            return False

        sql = """
        UPDATE cargos
        SET des_cargo=%s, est_cargo=%s
        WHERE id_cargo=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado, id_cargo))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar cargo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteCargo(self, id_cargo):
        sql = "DELETE FROM cargos WHERE id_cargo=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_cargo,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar cargo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
