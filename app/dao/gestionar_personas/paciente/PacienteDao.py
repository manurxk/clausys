from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import date

class PacienteDao:

    def getPacientes(self):
        """Obtiene todos los pacientes con sus datos completos"""
        pacienteSQL = """
            SELECT
                pac.id_paciente,
                pac.pac_historia_clinica,
                pac.pac_es_menor,
                p.per_nombre,
                p.per_apellido,
                p.per_cedula,
                p.per_fecha_nacimiento,
                DATE_PART('year', AGE(p.per_fecha_nacimiento)) AS edad,
                p.per_telefono,
                g.des_genero AS genero,
                c.des_ciudad AS ciudad,
                p.per_fecha_inscripcion
            FROM pacientes pac
            JOIN personas p ON pac.id_persona = p.id_persona
            LEFT JOIN generos g ON p.id_genero = g.id_genero AND g.est_genero = TRUE
            LEFT JOIN ciudades c ON p.id_ciudad = c.id_ciudad AND c.est_ciudad = TRUE
            ORDER BY pac.id_paciente DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(pacienteSQL)
            pacientes = cur.fetchall()
            
            return [{
                'id_paciente': p[0],
                'historia_clinica': p[1],
                'es_menor': p[2],
                'nombre': p[3],
                'apellido': p[4],
                'cedula': p[5],
                'fecha_nacimiento': p[6].strftime('%d/%m/%Y') if p[6] else None,
                'edad': int(p[7]) if p[7] else None,
                'telefono': p[8],
                'genero': p[9],
                'ciudad': p[10],
                'fecha_registro': p[11].strftime('%d/%m/%Y') if p[11] else None
            } for p in pacientes]
            
        except Exception as e:
            app.logger.error(f"Error al obtener todos los pacientes: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()


    def getPacienteById(self, pac_id):
        """Obtiene un paciente específico por ID con todos sus datos"""
        pacienteSQL = """
            SELECT
                pac.id_paciente,
                pac.pac_historia_clinica,
                pac.pac_es_menor,
                pac.pac_observaciones,
                p.per_nombre,
                p.per_apellido,
                p.per_cedula,
                p.per_fecha_nacimiento,
                DATE_PART('year', AGE(p.per_fecha_nacimiento)) AS edad,
                p.per_telefono,
                p.per_correo,
                p.per_domicilio,
                g.des_genero AS genero,
                ec.des_estado_civil AS estado_civil,
                c.des_ciudad AS ciudad,
                cn.des_ciudad AS ciudad_nacimiento,
                ni.des_nivel_instruccion AS nivel_instruccion,
                pr.des_profesion AS profesion,
                p.per_fecha_inscripcion,
                pm.pam_nom_madre,
                pm.pam_tel_madre,
                pm.pam_nom_padre,
                pm.pam_tel_padre,
                pm.pam_colegio,
                pm.pam_tel_colegio
            FROM pacientes pac
            JOIN personas p ON pac.id_persona = p.id_persona
            LEFT JOIN generos g ON p.id_genero = g.id_genero AND g.est_genero = TRUE
            LEFT JOIN estados_civiles ec ON p.id_estado_civil = ec.id_estado_civil AND ec.est_estado_civil = TRUE
            LEFT JOIN ciudades c ON p.id_ciudad = c.id_ciudad AND c.est_ciudad = TRUE
            LEFT JOIN ciudades cn ON p.id_ciudad_nacimiento = cn.id_ciudad AND cn.est_ciudad = TRUE
            LEFT JOIN niveles_instruccion ni ON p.id_nivel_instruccion = ni.id_nivel_instruccion AND ni.est_nivel_instruccion = TRUE
            LEFT JOIN profesiones pr ON p.id_profesion = pr.id_profesion AND pr.est_profesion = TRUE
            LEFT JOIN pacientes_menores pm ON pac.id_paciente = pm.id_paciente
            WHERE pac.id_paciente = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(pacienteSQL, (pac_id,))
            p = cur.fetchone()
            
            if not p:
                return None
            
            return {
                'id_paciente': p[0],
                'historia_clinica': p[1],
                'es_menor': p[2],
                'observaciones': p[3],
                'nombre': p[4],
                'apellido': p[5],
                'cedula': p[6],
                'fecha_nacimiento': p[7].strftime('%d/%m/%Y') if p[7] else None,
                'edad': int(p[8]) if p[8] else None,
                'telefono': p[9],
                'correo': p[10],
                'domicilio': p[11],
                'genero': p[12],
                'estado_civil': p[13],
                'ciudad': p[14],
                'ciudad_nacimiento': p[15],
                'nivel_instruccion': p[16],
                'profesion': p[17],
                'fecha_registro': p[18].strftime('%d/%m/%Y') if p[18] else None,
                'nom_madre': p[19],
                'tel_madre': p[20],
                'nom_padre': p[21],
                'tel_padre': p[22],
                'colegio': p[23],
                'tel_colegio': p[24]
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener paciente por ID: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

            
    def guardarPaciente(self, nombre, apellido, cedula, fecha_nacimiento, id_genero, estado_civil_id, 
                    telefono, correo, domicilio, id_ciudad, ciudad_nacimiento_id, nivel_instruccion_id, 
                    profesion_ocupacion_id, historia_clinica, es_menor, observaciones=None,
                    nom_madre=None, tel_madre=None, nom_padre=None, tel_padre=None, 
                    educacion=None, colegio=None, tel_colegio=None):
        """
        Guarda un nuevo paciente completo (persona + paciente + datos_menor si aplica)
        """
        insertPersonaSQL = """
            INSERT INTO personas(per_nombre, per_apellido, per_cedula, per_fecha_nacimiento, 
                            id_genero, id_estado_civil, per_telefono, per_correo, per_domicilio,
                            id_ciudad, id_ciudad_nacimiento, id_nivel_instruccion, id_profesion)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_persona
        """
        insertPacienteSQL = """
            INSERT INTO pacientes(id_persona, pac_historia_clinica, pac_es_menor, pac_observaciones)
            VALUES(%s, %s, %s, %s) RETURNING id_paciente
        """
        insertMenorSQL = """
            INSERT INTO pacientes_menores(id_paciente, pam_nom_madre, pam_tel_madre, pam_nom_padre, 
                                        pam_tel_padre, pam_educacion, pam_colegio, pam_tel_colegio)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            # 1. Insertar persona
            cur.execute(insertPersonaSQL, (nombre, apellido, cedula, fecha_nacimiento, id_genero, 
                                        estado_civil_id, telefono, correo, domicilio, id_ciudad, 
                                        ciudad_nacimiento_id, nivel_instruccion_id, profesion_ocupacion_id))
            persona_id = cur.fetchone()[0]

            # 2. Insertar paciente
            cur.execute(insertPacienteSQL, (persona_id, historia_clinica, es_menor, observaciones))
            paciente_id = cur.fetchone()[0]

            # 3. Si es menor, insertar datos del menor
            if es_menor and (nom_madre or nom_padre):
                cur.execute(insertMenorSQL, (paciente_id, nom_madre, tel_madre, nom_padre, 
                                            tel_padre, educacion, colegio, tel_colegio))

            con.commit()
            return paciente_id

        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al insertar paciente completo: {str(e)}")
            return None

        finally:
            cur.close()
            con.close()

    def updatePaciente(self, pac_id, nombre, apellido, cedula, fecha_nacimiento, id_genero, 
                    estado_civil_id, telefono, correo, domicilio, id_ciudad, ciudad_nacimiento_id,
                    nivel_instruccion_id, profesion_ocupacion_id, historia_clinica, es_menor, 
                    observaciones=None, nom_madre=None, tel_madre=None, nom_padre=None, 
                    tel_padre=None, educacion=None, colegio=None, tel_colegio=None):
        """Actualiza un paciente completo (persona + paciente + datos_menor)"""
        
        updatePersonaSQL = """
            UPDATE personas
            SET per_nombre = %s, per_apellido = %s, per_cedula = %s, per_fecha_nacimiento = %s,
                id_genero = %s, id_estado_civil = %s, per_telefono = %s, per_correo = %s,
                per_domicilio = %s, id_ciudad = %s, id_ciudad_nacimiento = %s,
                id_nivel_instruccion = %s, id_profesion = %s
            WHERE id_persona = (SELECT id_persona FROM pacientes WHERE id_paciente = %s)
        """
        
        updatePacienteSQL = """
            UPDATE pacientes
            SET pac_historia_clinica = %s, pac_es_menor = %s, pac_observaciones = %s
            WHERE id_paciente = %s
        """
        
        updateMenorSQL = """
            UPDATE pacientes_menores
            SET pam_nom_madre = %s, pam_tel_madre = %s, pam_nom_padre = %s, pam_tel_padre = %s,
                pam_educacion = %s, pam_colegio = %s, pam_tel_colegio = %s
            WHERE id_paciente = %s
        """
        
        insertMenorSQL = """
            INSERT INTO pacientes_menores(id_paciente, pam_nom_madre, pam_tel_madre, pam_nom_padre,
                                        pam_tel_padre, pam_educacion, pam_colegio, pam_tel_colegio)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        deleteMenorSQL = """
            DELETE FROM pacientes_menores WHERE id_paciente = %s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            # 1. Actualizar persona
            cur.execute(updatePersonaSQL, (nombre, apellido, cedula, fecha_nacimiento, id_genero,
                                        estado_civil_id, telefono, correo, domicilio, id_ciudad,
                                        ciudad_nacimiento_id, nivel_instruccion_id, 
                                        profesion_ocupacion_id, pac_id))

            # 2. Actualizar paciente
            cur.execute(updatePacienteSQL, (historia_clinica, es_menor, observaciones, pac_id))

            # 3. Manejar datos del menor
            cur.execute("SELECT id_paciente_menor FROM pacientes_menores WHERE id_paciente = %s", (pac_id,))
            existe_menor = cur.fetchone()

            if es_menor:
                if nom_madre or nom_padre:
                    if existe_menor:
                        cur.execute(updateMenorSQL, (nom_madre, tel_madre, nom_padre, tel_padre,
                                                    educacion, colegio, tel_colegio, pac_id))
                    else:
                        cur.execute(insertMenorSQL, (pac_id, nom_madre, tel_madre, nom_padre,
                                                    tel_padre, educacion, colegio, tel_colegio))
            else:
                if existe_menor:
                    cur.execute(deleteMenorSQL, (pac_id,))

            con.commit()
            return True

        except Exception as e:
            app.logger.error(f"Error al actualizar paciente: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()


    def getPacienteParaEditar(self, pac_id):
        """Obtiene un paciente con IDs originales para cargar en formulario de edición"""
        pacienteSQL = """
            SELECT
                pac.id_paciente,
                pac.pac_historia_clinica,
                pac.pac_es_menor,
                pac.pac_observaciones,
                p.id_persona,
                p.per_nombre,
                p.per_apellido,
                p.per_cedula,
                p.per_fecha_nacimiento,
                p.per_telefono,
                p.per_correo,
                p.per_domicilio,
                p.id_genero,
                p.id_estado_civil,
                p.id_ciudad,
                p.id_ciudad_nacimiento,
                p.id_nivel_instruccion,
                p.id_profesion,
                pm.pam_nom_madre,
                pm.pam_tel_madre,
                pm.pam_nom_padre,
                pm.pam_tel_padre,
                pm.pam_educacion,
                pm.pam_colegio,
                pm.pam_tel_colegio
            FROM pacientes pac
            JOIN personas p ON pac.id_persona = p.id_persona
            LEFT JOIN pacientes_menores pm ON pac.id_paciente = pm.id_paciente
            WHERE pac.id_paciente = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(pacienteSQL, (pac_id,))
            p = cur.fetchone()
            
            if not p:
                return None
            
            return {
                'id_paciente': p[0],
                'historia_clinica': p[1],
                'es_menor': p[2],
                'observaciones': p[3],
                'id_persona': p[4],
                'nombre': p[5],
                'apellido': p[6],
                'cedula': p[7],
                'fecha_nacimiento': p[8].strftime('%Y-%m-%d') if p[8] else None,
                'telefono': p[9],
                'correo': p[10],
                'domicilio': p[11],
                'id_genero': p[12],
                'id_estado_civil': p[13],
                'id_ciudad': p[14],
                'id_ciudad_nacimiento': p[15],
                'id_nivel_instruccion': p[16],
                'id_profesion': p[17],
                'nom_madre': p[18],
                'tel_madre': p[19],
                'nom_padre': p[20],
                'tel_padre': p[21],
                'educacion': p[22],
                'colegio': p[23],
                'tel_colegio': p[24]
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener paciente para editar: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()


    def deletePaciente(self, pac_id):
        """
        Elimina un paciente completo (en cascada: pacientes_menores -> pacientes -> personas)
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            # Obtener el id_persona antes de eliminar
            cur.execute("SELECT id_persona FROM pacientes WHERE id_paciente = %s", (pac_id,))
            resultado = cur.fetchone()
            
            if not resultado:
                return False
            
            persona_id = resultado[0]

            # 1. Eliminar de pacientes_menores (si existe) - se elimina automáticamente por CASCADE
            # 2. Eliminar de pacientes
            cur.execute("DELETE FROM pacientes WHERE id_paciente = %s", (pac_id,))
            
            # 3. Eliminar de personas
            cur.execute("DELETE FROM personas WHERE id_persona = %s", (persona_id,))

            con.commit()
            return True

        except Exception as e:
            app.logger.error(f"Error al eliminar paciente: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()


    def getPacientesMenores(self):
        """Obtiene solo los pacientes menores de edad"""
        pacienteSQL = """
            SELECT
                pac.id_paciente,
                pac.pac_historia_clinica,
                p.per_nombre,
                p.per_apellido,
                p.per_cedula,
                p.per_fecha_nacimiento,
                pm.pam_nom_madre,
                pm.pam_nom_padre,
                pm.pam_colegio
            FROM pacientes pac
            JOIN personas p ON pac.id_persona = p.id_persona
            LEFT JOIN pacientes_menores pm ON pac.id_paciente = pm.id_paciente
            WHERE pac.pac_es_menor = TRUE
            ORDER BY p.per_nombre
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            cur.execute(pacienteSQL)
            resultados = cur.fetchall()
            return [{
                'id_paciente': r[0],
                'historia_clinica': r[1],
                'nombre': r[2],
                'apellido': r[3],
                'cedula': r[4],
                'fecha_nacimiento': r[5].strftime('%d/%m/%Y') if r[5] else None,
                'nom_madre': r[6],
                'nom_padre': r[7],
                'colegio': r[8]
            } for r in resultados]
        except Exception as e:
            app.logger.error(f"Error al obtener pacientes menores: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()