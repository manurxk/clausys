from flask import current_app as app
from app.conexion.Conexion import Conexion

class MedicoDao:

    def getMedicos(self):
        medicoSQL = """
      SELECT
        m.id_medico, p.nombre, p.apellido, m.matricula
            FROM medicos m, personas p
            where m.id_persona=p.id_persona
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(medicoSQL)
            medicos = cur.fetchall()

            # Transformar los datos en una lista de diccionarios con los nuevos campos
            return [{'id_medico': medico[0], 'nombre': medico[1], 'apellido': medico[2],'matricula': medico[3]} for medico in medicos]

        except Exception as e:
            app.logger.error(f"Error al obtener todos los medicos: {str(e)}")
            return []

        finally:
            cur.close()
            con.close()

    def getMedicoById(self, id_medico):
        medicoSQL = """
         SELECT
            m.id_medico, p.nombre, p.apellido, m.matricula, p.id_persona
            FROM medicos m, personas p
            Where m.id_persona=p.id_persona and m.id_medico=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(medicoSQL, (id_medico,))
            medicoEncontrado = cur.fetchone()
            if medicoEncontrado:
                return {
                    "id_medico": medicoEncontrado[0],
                    "nombre": medicoEncontrado[1],
                    "apellido": medicoEncontrado[2],
                    "matricula": medicoEncontrado[3],
                    "id_persona": medicoEncontrado[4]
                }
            else:
                return None
        except Exception as e:
            app.logger.error(f"Error al obtener medico por ID: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def guardarMedico(self, id_persona,matricula):
        insertMedicoSQL = """
        INSERT INTO medicos(matricula, id_persona) VALUES(%s, %s) RETURNING id_medico
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(insertMedicoSQL, (matricula, id_persona))
            medico_id = cur.fetchone()[0]
            con.commit()
            return medico_id

        except Exception as e:
            app.logger.error(f"Error al insertar medico: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def updateMedico(self, id_medico, id_persona, matricula):
        updateMedicoSQL = """
        UPDATE medicos
        SET  matricula=%s, id_persona=%s
        WHERE id_medico=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(updateMedicoSQL, (matricula, id_persona, id_medico))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0

        except Exception as e:
            app.logger.error(f"Error al actualizar medico: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()

    def deleteMedico(self, id_medico):
        deleteMedicoSQL = """
        DELETE FROM medicos
        WHERE id_medico=%s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(deleteMedicoSQL, (id_medico,))
            rows_affected = cur.rowcount
            con.commit()

            return rows_affected > 0

        except Exception as e:
            app.logger.error(f"Error al eliminar medico: {str(e)}")
            con.rollback()
            return False

        finally:
            cur.close()
            con.close()
