# Data access object - DAO
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class NivelInstruccionDao:

    def getNiveles(self):
        sql = """
        SELECT id_nivel_instruccion, des_nivel_instruccion, est_nivel_instruccion
        FROM niveles_instruccion
        ORDER BY id_nivel_instruccion
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            niveles = cur.fetchall()
            return [
                {
                    'id': n[0],
                    'descripcion': n[1],
                    'estado': n[2]
                }
                for n in niveles
            ]
        except Exception as e:
            app.logger.error(f"Error al obtener niveles de instrucción: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getNivelById(self, id_nivel):
        sql = """
        SELECT id_nivel_instruccion, des_nivel_instruccion, est_nivel_instruccion
        FROM niveles_instruccion
        WHERE id_nivel_instruccion=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_nivel,))
            nivel = cur.fetchone()
            if nivel:
                return {
                    "id": nivel[0],
                    "descripcion": nivel[1],
                    "estado": nivel[2]
                }
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener nivel de instrucción: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def nivelExiste(self, descripcion):
        """Verifica si ya existe el nivel con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM niveles_instruccion WHERE LOWER(des_nivel_instruccion)=LOWER(%s)"
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

    def guardarNivel(self, descripcion, estado=True):
        # Validaciones
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números y acentos")
            return False
        if self.nivelExiste(descripcion):
            app.logger.warning("El nivel de instrucción ya existe")
            return False

        sql = """
        INSERT INTO niveles_instruccion(des_nivel_instruccion, est_nivel_instruccion)
        VALUES(%s, %s)
        RETURNING id_nivel_instruccion
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado))
            id_nivel = cur.fetchone()[0]
            con.commit()
            return id_nivel
        except Exception as e:
            app.logger.error(f"Error al insertar nivel de instrucción: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateNivel(self, id_nivel, descripcion, estado=True):
        # Validaciones
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida")
            return False

        sql = """
        UPDATE niveles_instruccion
        SET des_nivel_instruccion=%s, est_nivel_instruccion=%s
        WHERE id_nivel_instruccion=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado, id_nivel))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar nivel de instrucción: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteNivel(self, id_nivel):
        sql = "DELETE FROM niveles_instruccion WHERE id_nivel_instruccion=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_nivel,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar nivel de instrucción: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
