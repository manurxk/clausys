import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class SintomaDao:

    def getSintomas(self):
        sql = """
        SELECT id_sintoma, des_sintoma, est_sintoma
        FROM sintomas
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            sintomas = cur.fetchall()
            return [{'id': s[0], 'descripcion': s[1], 'estado': s[2]} for s in sintomas]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los síntomas: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getSintomaById(self, id_sintoma):
        sql = """
        SELECT id_sintoma, des_sintoma, est_sintoma
        FROM sintomas
        WHERE id_sintoma=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_sintoma,))
            sintoma = cur.fetchone()
            if sintoma:
                return {"id": sintoma[0], "descripcion": sintoma[1], "estado": sintoma[2]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener síntoma: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def sintomaExiste(self, descripcion):
        """Verifica si ya existe el síntoma con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM sintomas WHERE LOWER(des_sintoma)=LOWER(%s)"
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

    def validarEstado(self, estado):
        """Valida que el estado sea 'A' o 'I'."""
        return estado in ['A', 'I']

    # ============================
    # CRUD
    # ============================

    def guardarSintoma(self, descripcion, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False
        
        if self.sintomaExiste(descripcion):
            app.logger.warning("El síntoma ya existe")
            return False

        if not self.validarEstado(estado):
            app.logger.warning("Estado inválido: debe ser 'A' (Activo) o 'I' (Inactivo)")
            return False

        sql = """
        INSERT INTO sintomas(des_sintoma, est_sintoma, usuario_creacion)
        VALUES(%s, %s, %s)
        RETURNING id_sintoma
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario))
            id_sintoma = cur.fetchone()[0]
            con.commit()
            app.logger.info(f"Sintoma insertado con ID: {id_sintoma}")
            return id_sintoma
        except Exception as e:
            app.logger.error(f"Error al insertar síntoma: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateSintoma(self, id_sintoma, descripcion, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False

        if not self.validarEstado(estado):
            app.logger.warning("Estado inválido")
            return False

        sql = """
        UPDATE sintomas
        SET des_sintoma=%s, est_sintoma=%s, usuario_modificacion=%s, fecha_modificacion=CURRENT_TIMESTAMP
        WHERE id_sintoma=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, usuario, id_sintoma))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Sintoma {id_sintoma} actualizado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar síntoma: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteSintoma(self, id_sintoma):
        sql = "DELETE FROM sintomas WHERE id_sintoma=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_sintoma,))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Sintoma {id_sintoma} eliminado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar síntoma: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
