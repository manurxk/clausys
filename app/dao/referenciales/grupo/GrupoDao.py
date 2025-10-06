# Data access object - DAO
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class GrupoDao:

    def getGrupos(self):
        sql = """
        SELECT id_grupo, des_grupo, est_grupo
        FROM grupos
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            grupos = cur.fetchall()
            return [{'id': g[0], 'descripcion': g[1], 'estado': g[2]} for g in grupos]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los grupos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getGrupoById(self, id_grupo):
        sql = """
        SELECT id_grupo, des_grupo, est_grupo
        FROM grupos
        WHERE id_grupo=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_grupo,))
            grupo = cur.fetchone()
            if grupo:
                return {"id": grupo[0], "descripcion": grupo[1], "estado": grupo[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener grupo: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def grupoExiste(self, descripcion):
        """Verifica si ya existe el grupo con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM grupos WHERE LOWER(des_grupo)=LOWER(%s)"
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

    def guardarGrupo(self, descripcion, estado=True):
        # Validaciones
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números y acentos")
            return False
        if self.grupoExiste(descripcion):
            app.logger.warning("El grupo ya existe")
            return False

        sql = """
        INSERT INTO grupos(des_grupo, est_grupo)
        VALUES(%s, %s)
        RETURNING id_grupo
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado))
            id_grupo = cur.fetchone()[0]
            con.commit()
            return id_grupo
        except Exception as e:
            app.logger.error(f"Error al insertar grupo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateGrupo(self, id_grupo, descripcion, estado=True):
        # Validaciones
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida")
            return False

        sql = """
        UPDATE grupos
        SET des_grupo=%s, est_grupo=%s
        WHERE id_grupo=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (descripcion, estado, id_grupo))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar grupo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteGrupo(self, id_grupo):
        sql = "DELETE FROM grupos WHERE id_grupo=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_grupo,))
            filas = cur.rowcount
            con.commit()
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar grupo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
