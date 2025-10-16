import re
from flask import current_app as app
from app.conexion.Conexion import Conexion

class MedicamentoDao:

    def getMedicamentos(self):
        sql = """
        SELECT id_medicamento, des_medicamento, est_medicamento, medicamento_concentracion
        FROM medicamentos
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            medicamentos = cur.fetchall()
            return [{'id': m[0], 'descripcion': m[1], 'estado': m[2], 'concentracion': m[3]} for m in medicamentos]
        except Exception as e:
            app.logger.error(f"Error al obtener todos los medicamentos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getMedicamentoById(self, id_medicamento):
        sql = """
        SELECT id_medicamento, des_medicamento, est_medicamento, medicamento_concentracion
        FROM medicamentos
        WHERE id_medicamento=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_medicamento,))
            medicamento = cur.fetchone()
            if medicamento:
                return {"id": medicamento[0], "descripcion": medicamento[1], "estado": medicamento[2], "concentracion": medicamento[3]}
            return None
        except Exception as e:
            app.logger.error(f"Error al obtener medicamento: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    # ============================
    # VALIDACIONES
    # ============================

    def medicamentoExiste(self, descripcion):
        """Verifica si ya existe el medicamento con el mismo nombre (case-insensitive)."""
        sql = "SELECT 1 FROM medicamentos WHERE LOWER(des_medicamento)=LOWER(%s)"
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

    def validarConcentracion(self, concentracion):
        """Permite una concentración con formato: número seguido de unidad (ej: 10mg, 20g)."""
        if concentracion is None or concentracion.strip() == "":
            return True  # Es opcional
        patron = r"^[0-9]+(\.[0-9]+)?(mg|g|ml|l|μg)$"
        return bool(re.match(patron, concentracion.lower()))

    # ============================
    # CRUD
    # ============================

    def guardarMedicamento(self, descripcion, concentracion=None, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False
        
        if self.medicamentoExiste(descripcion):
            app.logger.warning("El medicamento ya existe")
            return False

        if concentracion and not self.validarConcentracion(concentracion):
            app.logger.warning("Concentración inválida")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido: debe ser 'A' (Activo) o 'I' (Inactivo)")
            return False

        sql = """
        INSERT INTO medicamentos(des_medicamento, est_medicamento, medicamento_concentracion, usuario_creacion)
        VALUES(%s, %s, %s, %s)
        RETURNING id_medicamento
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, concentracion, usuario))
            id_medicamento = cur.fetchone()[0]
            con.commit()
            app.logger.info(f"Medicamento insertado con ID: {id_medicamento}")
            return id_medicamento
        except Exception as e:
            app.logger.error(f"Error al insertar medicamento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateMedicamento(self, id_medicamento, descripcion, concentracion=None, estado='A'):
        # Validaciones
        if not descripcion or descripcion.strip() == "":
            app.logger.warning("Descripción vacía")
            return False
        
        if not self.validarDescripcion(descripcion):
            app.logger.warning("Descripción inválida: solo letras, números, acentos, espacios y puntos")
            return False

        if concentracion and not self.validarConcentracion(concentracion):
            app.logger.warning("Concentración inválida")
            return False

        if estado not in ['A', 'I']:
            app.logger.warning("Estado inválido")
            return False

        sql = """
        UPDATE medicamentos
        SET des_medicamento=%s, est_medicamento=%s, medicamento_concentracion=%s, 
            usuario_modificacion=%s, fecha_modificacion=CURRENT_TIMESTAMP
        WHERE id_medicamento=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            usuario = app.config.get('USUARIO_ACTUAL', 'SISTEMA')
            cur.execute(sql, (descripcion, estado, concentracion, usuario, id_medicamento))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Medicamento {id_medicamento} actualizado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar medicamento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteMedicamento(self, id_medicamento):
        sql = "DELETE FROM medicamentos WHERE id_medicamento=%s"
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, (id_medicamento,))
            filas = cur.rowcount
            con.commit()
            if filas > 0:
                app.logger.info(f"Medicamento {id_medicamento} eliminado")
            return filas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar medicamento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
