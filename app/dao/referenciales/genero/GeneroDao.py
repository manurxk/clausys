# Data access object - DAO
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class GeneroDao:

    def getGeneros(self):
        sql = """
        SELECT id_genero, des_genero, est_genero
        FROM generos
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            generos = cur.fetchall()
            return [{'id': g[0], 'descripcion': g[1], 'estado': g[2]} for g in generos]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los géneros: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getGeneroById(self, id_genero):
        sql = """
        SELECT id_genero, des_genero, est_genero
        FROM generos
        WHERE id_genero=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_genero,))
            genero = cur.fetchone()
            if genero:
                return {"id": genero[0], "descripcion": genero[1], "estado": genero[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener género: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def generoExiste(self, descripcion):
        """Verifica si ya existe el género con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM generos WHERE LOWER(des_genero)=LOWER(%s)"
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

    def guardarGenero(self, descripcion, estado=True):
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números y acentos")
            return False
        if self.generoExiste(descripcion):
            app.logger.warning("El género ya existe")
            return False

        sql = """
        INSERT INTO generos(des_genero, est_genero)
        VALUES(%s, %s)
        RETURNING id_genero
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado))
            id_genero = cur.fetchone()[0]
            con.commit()
            return id_genero
        except Exception as e:
            app.logger.error(f"Error al insertar género: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateGenero(self, id_genero, descripcion, estado=True):
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida")
            return False

        sql = """
        UPDATE generos
        SET des_genero=%s, est_genero=%s
        WHERE id_genero=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado, id_genero))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar género: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteGenero(self, id_genero):
        sql = "DELETE FROM generos WHERE id_genero=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_genero,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar género: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
