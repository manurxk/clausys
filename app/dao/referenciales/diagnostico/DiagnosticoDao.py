# Data access object - DAO
import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class DiagnosticoDao:

    def getDiagnosticos(self):
        sql = """
        SELECT id_diagnostico, des_diagnostico, est_diagnostico, diagnostico_codigo_cie10
        FROM diagnosticos
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            diagnosticos = cur.fetchall()
            return [{'id': d[0], 'descripcion': d[1], 'estado': d[2], 'codigo_cie10': d[3]} for d in diagnosticos]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los diagnósticos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getDiagnosticoById(self, id_diagnostico):
        sql = """
        SELECT id_diagnostico, des_diagnostico, est_diagnostico, diagnostico_codigo_cie10
        FROM diagnosticos
        WHERE id_diagnostico=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_diagnostico,))
            diagnostico = cur.fetchone()
            if diagnostico:
                return {"id": diagnostico[0], "descripcion": diagnostico[1], "estado": diagnostico[2], "codigo_cie10": diagnostico[3]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener diagnóstico: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def diagnosticoExiste(self, descripcion):
        """Verifica si ya existe el diagnóstico con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM diagnosticos WHERE LOWER(des_diagnostico)=LOWER(%s)"
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

    def validarCodigoCie10(self, codigo_cie10):
        """Valida el formato del código CIE-10: letra seguida de números y puntos (ej: A15.0, B99.9)."""
        if codigo_cie10 is None or codigo_cie10.strip() == "":
            return True  # Es opcional
        patron = r"^[A-Z]{1}[0-9]{2}(\.[0-9]{1,2})?$"
        return bool(re.match(patron, codigo_cie10.upper()))

    # ============================
    # CRUD
    # ============================

    def guardarDiagnostico(self, descripcion, codigo_cie10=None, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False
        
        if self.diagnosticoExiste(descripcion):
            app.logger.warning("El diagnóstico ya existe")
            return False

        if codigo_cie10 and not self.validarCodigoCie10(codigo_cie10):
            app.logger.warning("Código CIE-10 inválido")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido: debe ser 'A' (Activo) o 'I' (Inactivo)")
            return False

        sql = """
        INSERT INTO diagnosticos(des_diagnostico, est_diagnostico, diagnostico_codigo_cie10, usuario_creacion)
        VALUES(%s, %s, %s, %s)
        RETURNING id_diagnostico
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, codigo_cie10, usuario))
            id_diagnostico = cur.fetchone()[0]
            con.commit()
            app.logger.info(f"Diagnóstico insertado con ID: {id_diagnostico}")
            return id_diagnostico
        except Exception as e:
            app.logger.error(f"Error al insertar diagnóstico: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateDiagnostico(self, id_diagnostico, descripcion, codigo_cie10=None, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False

        if codigo_cie10 and not self.validarCodigoCie10(codigo_cie10):
            app.logger.warning("Código CIE-10 inválido")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido")
            return False

        sql = """
        UPDATE diagnosticos
        SET des_diagnostico=%s, est_diagnostico=%s, diagnostico_codigo_cie10=%s, 
            usuario_modificacion=%s, fecha_modificacion=CURRENT_TIMESTAMP
        WHERE id_diagnostico=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, codigo_cie10, usuario, id_diagnostico))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Diagnóstico {id_diagnostico} actualizado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar diagnóstico: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteDiagnostico(self, id_diagnostico):
        sql = "DELETE FROM diagnosticos WHERE id_diagnostico=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_diagnostico,))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Diagnóstico {id_diagnostico} eliminado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar diagnóstico: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()