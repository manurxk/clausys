import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class SignoDao:

    def getSignos(self):
        sql = """
        SELECT id_signo, des_signo, est_signo
        FROM signos
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            signos = cur.fetchall()
            return [{'id': s[0], 'descripcion': s[1], 'estado': s[2]} for s in signos]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los signos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getSignoById(self, id_signo):
        sql = """
        SELECT id_signo, des_signo, est_signo
        FROM signos
        WHERE id_signo=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_signo,))
            signo = cur.fetchone()
            if signo:
                return {"id": signo[0], "descripcion": signo[1], "estado": signo[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener signo: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def signoExiste(self, descripcion):
        """Verifica si ya existe el signo con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM signos WHERE LOWER(des_signo)=LOWER(%s)"
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
        """Permite solo letras, números, acentos, espacios y puntos."""
        patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 .]+$"
        return bool(re.match(patron, descripcion))

    # ============================
    # CRUD
    # ============================

    def guardarSigno(self, descripcion, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False
        
        if self.signoExiste(descripcion):
            app.logger.warning("El signo ya existe")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido: debe ser 'A' (Activo) o 'I' (Inactivo)")
            return False

        sql = """
        INSERT INTO signos(des_signo, est_signo, usuario_creacion)
        VALUES(%s, %s, %s)
        RETURNING id_signo
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario))
            id_signo = cur.fetchone()[0]
            con.commit()
            app.logger.info(f"Signo insertado con ID: {id_signo}")
            return id_signo
        except Exception as e:
            app.logger.error(f"Error al insertar signo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateSigno(self, id_signo, descripcion, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido")
            return False

        sql = """
        UPDATE signos
        SET des_signo=%s, est_signo=%s, usuario_modificacion=%s, fecha_modificacion=CURRENT_TIMESTAMP
        WHERE id_signo=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario, id_signo))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Signo {id_signo} actualizado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar signo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteSigno(self, id_signo):
        sql = "DELETE FROM signos WHERE id_signo=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_signo,))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Signo {id_signo} eliminado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar signo: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
