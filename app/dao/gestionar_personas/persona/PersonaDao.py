from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import date

class PersonaDao:

    def getPersonas(self):
        personaSQL = """
            SELECT
                p.id_persona, p.nombre, p.apellido, p.cedula, p.fecha_nacimiento, g.descripcion, e.descripcion, 
                p.telefono_emergencia, c.descripcion, pa.fecha_registro, m.matricula, m.id_medico
            FROM personas p
            JOIN generos g ON p.id_genero = g.id_genero
            JOIN estado_civiles e ON p.id_estado_civil = e.id_estado_civil
            JOIN ciudades c ON p.id_ciudad = c.id_ciudad
            JOIN pacientes pa ON p.id_persona = pa.id_persona
            LEFT JOIN medicos m ON p.id_persona = m.id_persona
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(personaSQL)
            personas = cur.fetchall()

            return [{
                'id': persona[0],
                'nombre': persona[1],
                'apellido': persona[2],
                'cedula': persona[3],
                'fecha_nacimiento': persona[4].strftime('%d/%m/%Y') if persona[4] else None,
                'genero': persona[5],
                'estado_civil': persona[6],
                'telefono_emergencia': persona[7],
                'ciudad': persona[8],
                'fecha_registro': persona[9].strftime('%d/%m/%Y') if persona[9] else None,
                'matricula': persona[10],
                'id_medico': persona[11]
            } for persona in personas]

        except Exception as e:
            app.logger.error(f"Error al obtener todas las personas: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getPersonasById(self, id_persona):
        personaSQL = """
            SELECT
                p.id_persona, p.nombre, p.apellido, p.cedula, p.fecha_nacimiento, g.descripcion, e.descripcion,
                p.telefono_emergencia, c.descripcion, g.id_genero, e.id_estado_civil, c.id_ciudad, pa.fecha_registro,
                m.matricula, m.id_medico
            FROM personas p
            JOIN generos g ON p.id_genero = g.id_genero
            JOIN estado_civiles e ON p.id_estado_civil = e.id_estado_civil
            JOIN ciudades c ON p.id_ciudad = c.id_ciudad
            JOIN pacientes pa ON p.id_persona = pa.id_persona
            LEFT JOIN medicos m ON p.id_persona = m.id_persona
            WHERE p.id_persona = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(personaSQL, (id_persona,))
            personaEncontrada = cur.fetchone()
            if personaEncontrada:
                return {
                    "id": personaEncontrada[0],
                    "nombre": personaEncontrada[1],
                    "apellido": personaEncontrada[2],
                    "cedula": personaEncontrada[3],
                    "fecha_nacimiento": personaEncontrada[4],
                    "genero": personaEncontrada[5],
                    "estado_civil": personaEncontrada[6],
                    "telefono_emergencia": personaEncontrada[7],
                    "ciudad": personaEncontrada[8],
                    "id_genero": personaEncontrada[9],
                    "id_estado_civil": personaEncontrada[10],
                    "id_ciudad": personaEncontrada[11],
                    "fecha_registro": personaEncontrada[12],
                    "matricula": personaEncontrada[13],
                    "id_medico": personaEncontrada[14]
                }
            else:
                return None
        except Exception as e:
            app.logger.error(f"Error al obtener persona por ID: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def guardarPersona(self, nombre, apellido, cedula, fecha_nacimiento, id_genero, id_estado_civil, telefono_emergencia, id_ciudad, fecha_registro=None, matricula=None):
        insertPersonaSQL = """
            INSERT INTO personas(nombre, apellido, cedula, fecha_nacimiento, id_genero, id_estado_civil, telefono_emergencia, id_ciudad)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_persona
        """
        insertPacienteSQL = """
            INSERT INTO pacientes(id_persona, fecha_registro)
            VALUES(%s, %s)
        """
        insertMedicoSQL = """
            INSERT INTO medicos(id_persona, matricula)
            VALUES(%s, %s)
        """
        if fecha_registro is None:
            fecha_registro = date.today()  # Fecha actual si no se pasa

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(insertPersonaSQL, (nombre, apellido, cedula, fecha_nacimiento, id_genero, id_estado_civil, telefono_emergencia, id_ciudad))
            persona_id = cur.fetchone()[0]

            cur.execute(insertPacienteSQL, (persona_id, fecha_registro))

            # Si envían matricula, insertamos médico
            if matricula:
                cur.execute(insertMedicoSQL, (persona_id, matricula))

            con.commit()
            return persona_id
        except Exception as e:
            app.logger.error(f"Error al insertar persona, paciente o médico: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updatePersona(self, id_persona, nombre, apellido, cedula, fecha_nacimiento, id_genero, id_estado_civil, telefono_emergencia, id_ciudad, matricula=None):
        updatePersonaSQL = """
            UPDATE personas
            SET nombre = %s, apellido = %s, cedula = %s, fecha_nacimiento = %s, id_genero = %s, id_estado_civil = %s, telefono_emergencia = %s, id_ciudad = %s
            WHERE id_persona = %s
        """
        updateMedicoSQL = """
            UPDATE medicos
            SET matricula = %s
            WHERE id_persona = %s
        """
        insertMedicoSQL = """
            INSERT INTO medicos(id_persona, matricula)
            VALUES(%s, %s)
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            # Actualizar persona
            cur.execute(updatePersonaSQL, (nombre, apellido, cedula, fecha_nacimiento, id_genero, id_estado_civil, telefono_emergencia, id_ciudad, id_persona))

            # Actualizar o insertar médico
            cur.execute("SELECT id_medico FROM medicos WHERE id_persona = %s", (id_persona,))
            existe_medico = cur.fetchone()
            if matricula:
                if existe_medico:
                    cur.execute(updateMedicoSQL, (matricula, id_persona))
                else:
                    cur.execute(insertMedicoSQL, (id_persona, matricula))
            else:
                # Si matricula es None o vacía, podrías eliminar médico o ignorar (opcional)
                pass

            con.commit()
            return True
        except Exception as e:
            app.logger.error(f"Error al actualizar persona o médico: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def updateFechaRegistroPaciente(self, id_persona, fecha_registro):
        updatePacienteSQL = """
            UPDATE pacientes
            SET fecha_registro = %s
            WHERE id_persona = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(updatePacienteSQL, (fecha_registro, id_persona))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al actualizar fecha de registro del paciente: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()





    def getPersonasConMatricula(self):
        sql = """
            SELECT
                p.id_persona, p.nombre, p.apellido, p.cedula, p.fecha_nacimiento, g.descripcion AS genero, e.descripcion AS estado_civil, 
                p.telefono_emergencia, c.descripcion AS ciudad, pa.fecha_registro, m.matricula
            FROM personas p
            JOIN generos g ON p.id_genero = g.id_genero
            JOIN estado_civiles e ON p.id_estado_civil = e.id_estado_civil
            JOIN ciudades c ON p.id_ciudad = c.id_ciudad
            JOIN pacientes pa ON p.id_persona = pa.id_persona
            JOIN medicos m ON p.id_persona = m.id_persona -- INNER JOIN para sólo con matricula
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql)
            resultados = cur.fetchall()
            return [{
                'id': r[0], 'nombre': r[1], 'apellido': r[2], 'cedula': r[3], 'fecha_nacimiento': r[4].strftime('%d/%m/%Y') if r[4] else None,
                'genero': r[5], 'estado_civil': r[6], 'telefono_emergencia': r[7], 'ciudad': r[8],
                'fecha_registro': r[9].strftime('%d/%m/%Y') if r[9] else None, 'matricula': r[10]
            } for r in resultados]
        except Exception as e:
            app.logger.error(f"Error al obtener personas con matrícula: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    # --- Método para traer personas con fecha_registro en rango (o fecha_registro no null) ---
    def getPersonasPorFechaIngreso(self, fecha_inicio=None, fecha_fin=None):
        sql = """
            SELECT
                p.id_persona, p.nombre, p.apellido, p.cedula, p.fecha_nacimiento, g.descripcion AS genero, e.descripcion AS estado_civil, 
                p.telefono_emergencia, c.descripcion AS ciudad, pa.fecha_registro, m.matricula
            FROM personas p
            JOIN generos g ON p.id_genero = g.id_genero
            JOIN estado_civiles e ON p.id_estado_civil = e.id_estado_civil
            JOIN ciudades c ON p.id_ciudad = c.id_ciudad
            JOIN pacientes pa ON p.id_persona = pa.id_persona
            LEFT JOIN medicos m ON p.id_persona = m.id_persona
            WHERE pa.fecha_registro IS NOT NULL
        """

        params = []
        if fecha_inicio and fecha_fin:
            sql += " AND pa.fecha_registro BETWEEN %s AND %s"
            params = [fecha_inicio, fecha_fin]

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(sql, params)
            resultados = cur.fetchall()
            return [{
                'id': r[0], 'nombre': r[1], 'apellido': r[2], 'cedula': r[3], 'fecha_nacimiento': r[4].strftime('%d/%m/%Y') if r[4] else None,
                'genero': r[5], 'estado_civil': r[6], 'telefono_emergencia': r[7], 'ciudad': r[8],
                'fecha_registro': r[9].strftime('%d/%m/%Y') if r[9] else None, 'matricula': r[10]
            } for r in resultados]
        except Exception as e:
            app.logger.error(f"Error al obtener personas por fecha de ingreso: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()















    def deletePersona(self, id_persona):
        # Si tienes ON DELETE CASCADE en medicos y pacientes para persona, solo borrás persona
        deletePersonaSQL = """
            DELETE FROM personas
            WHERE id_persona = %s
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            cur.execute(deletePersonaSQL, (id_persona,))
            filas_afectadas = cur.rowcount
            con.commit()
            return filas_afectadas > 0
        except Exception as e:
            app.logger.error(f"Error al eliminar persona: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
