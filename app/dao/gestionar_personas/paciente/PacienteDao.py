from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import date, datetime

class PacienteDao:
    
    def calcular_es_menor(self, fecha_nacimiento):
        """Calcula automáticamente si es menor de edad basado en la fecha de nacimiento"""
        if not fecha_nacimiento:
            return False
        
        # Si es string, convertir a date
        if isinstance(fecha_nacimiento, str):
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        
        return edad < 18
    
    def validar_fecha_nacimiento(self, fecha_nacimiento):
        """Valida que la fecha de nacimiento sea razonable"""
        if not fecha_nacimiento:
            return False, "La fecha de nacimiento es obligatoria"
        
        # Si es string, convertir a date
        if isinstance(fecha_nacimiento, str):
            try:
                fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            except ValueError:
                return False, "Formato de fecha inválido"
        
        hoy = date.today()
        
        # No puede ser fecha futura
        if fecha_nacimiento > hoy:
            return False, "La fecha de nacimiento no puede ser futura"
        
        # No puede ser mayor a 120 años
        edad = hoy.year - fecha_nacimiento.year
        if edad > 120:
            return False, "La fecha de nacimiento no es válida (mayor a 120 años)"
        
        return True, ""
    
    def validar_datos_menor(self, es_menor, nom_madre, nom_padre):
        """Valida que si es menor tenga al menos un tutor"""
        if es_menor:
            if not nom_madre and not nom_padre:
                return False, "Debe proporcionar al menos el nombre de la madre o del padre para pacientes menores"
        return True, ""
    def generar_historia_clinica(self, nombre, apellido, cedula):
        """
        Genera historia clínica con formato: InicialNombre + InicialApellido + Cédula
        Ejemplos: JP1234567, MG9876543
        """
        try:
            # Obtener primera letra del nombre (mayúscula)
            inicial_nombre = nombre.strip()[0].upper() if nombre else 'X'
            
            # Obtener primera letra del apellido (mayúscula)
            inicial_apellido = apellido.strip()[0].upper() if apellido else 'X'
            
            # Limpiar cédula (quitar puntos, guiones, espacios)
            cedula_limpia = ''.join(filter(str.isdigit, str(cedula)))
            
            historia = f"{inicial_nombre}{inicial_apellido}{cedula_limpia}"
            
            app.logger.info(f"Historia clínica generada: {historia} (de {nombre} {apellido})")
            return historia
            
        except Exception as e:
            app.logger.error(f"Error generando historia clínica: {str(e)}")
            # Fallback: usar timestamp
            return f"HC{int(datetime.now().timestamp())}"
        
    def validar_historia_unica(self, historia_clinica, pac_id=None):
        """
        Verifica que la historia clínica no esté duplicada
        pac_id: excluir el propio paciente en UPDATE
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            if pac_id:
                # Para UPDATE: excluir el propio paciente
                cur.execute("""
                    SELECT COUNT(*) FROM pacientes 
                    WHERE pac_historia_clinica = %s AND id_paciente != %s
                """, (historia_clinica, pac_id))
            else:
                # Para INSERT: verificar si existe
                cur.execute("""
                    SELECT COUNT(*) FROM pacientes 
                    WHERE pac_historia_clinica = %s
                """, (historia_clinica,))
            
            count = cur.fetchone()[0]
            return count == 0
            
        except Exception as e:
            app.logger.error(f"Error validando unicidad de historia clínica: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()
            
    def generar_historia_clinica_unica(self, nombre, apellido, cedula):
        """
        Genera historia clínica única, añadiendo sufijo si ya existe
        """
        historia_base = self.generar_historia_clinica(nombre, apellido, cedula)
        historia = historia_base
        sufijo = 1
        
        # Si ya existe, agregar sufijo -2, -3, etc.
        while not self.validar_historia_unica(historia):
            sufijo += 1
            historia = f"{historia_base}-{sufijo}"
            app.logger.warning(f"Historia duplicada, usando sufijo: {historia}")
        
        return historia

    def getPacientes(self):
        """Obtiene todos los pacientes con sus datos completos"""
        pacienteSQL = """
            SELECT
                pac.id_paciente,
                pac.pac_historia_clinica,
                CASE WHEN DATE_PART('year', AGE(p.per_fecha_nacimiento)) < 18 THEN TRUE ELSE FALSE END AS es_menor,
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
            LEFT JOIN ciudades c ON p.id_ciudad = c.id_ciudad
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
                CASE WHEN DATE_PART('year', AGE(p.per_fecha_nacimiento)) < 18 THEN TRUE ELSE FALSE END AS es_menor,
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

    def getPacienteParaEditar(self, pac_id):
        """Obtiene un paciente con IDs y descripciones para edición"""
        pacienteSQL = """
            SELECT
                pac.id_paciente,
                pac.id_persona,
                pac.pac_historia_clinica,
                CASE WHEN DATE_PART('year', AGE(p.per_fecha_nacimiento)) < 18 THEN TRUE ELSE FALSE END AS es_menor,
                pac.pac_observaciones,
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
                g.des_genero,
                ec.des_estado_civil,
                c.des_ciudad,
                cn.des_ciudad AS ciudad_nacimiento_desc,
                ni.des_nivel_instruccion,
                pr.des_profesion,
                pm.pam_nom_madre,
                pm.pam_tel_madre,
                pm.pam_nom_padre,
                pm.pam_tel_padre,
                pm.pam_educacion,
                pm.pam_colegio,
                pm.pam_tel_colegio
            FROM pacientes pac
            JOIN personas p ON pac.id_persona = p.id_persona
            LEFT JOIN generos g ON p.id_genero = g.id_genero
            LEFT JOIN estados_civiles ec ON p.id_estado_civil = ec.id_estado_civil
            LEFT JOIN ciudades c ON p.id_ciudad = c.id_ciudad
            LEFT JOIN ciudades cn ON p.id_ciudad_nacimiento = cn.id_ciudad
            LEFT JOIN niveles_instruccion ni ON p.id_nivel_instruccion = ni.id_nivel_instruccion
            LEFT JOIN profesiones pr ON p.id_profesion = pr.id_profesion
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
            
            paciente = {
                'id_paciente': p[0],
                'id_persona': p[1],
                'historia_clinica': p[2],
                'es_menor': p[3],
                'observaciones': p[4],
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
                'genero': p[18],
                'estado_civil': p[19],
                'ciudad': p[20],
                'ciudad_nacimiento': p[21],
                'nivel_instruccion': p[22],
                'profesion': p[23],
                'nom_madre': p[24],
                'tel_madre': p[25],
                'nom_padre': p[26],
                'tel_padre': p[27],
                'educacion': p[28],
                'colegio': p[29],
                'tel_colegio': p[30]
            }
            
            app.logger.info(f"Paciente cargado para editar: {paciente['nombre']} {paciente['apellido']} - Es menor: {paciente['es_menor']}")
            
            return paciente
            
        except Exception as e:
            app.logger.error(f"Error al obtener paciente para editar: {str(e)}", exc_info=True)
            return None
        finally:
            cur.close()
            con.close()
    def guardarPaciente(self, nombre, apellido, cedula, fecha_nacimiento, 
                        telefono=None,  # ← Ahora con valor por defecto
                        id_genero=None, id_estado_civil=None, correo=None, domicilio=None, 
                        id_ciudad=None, id_ciudad_nacimiento=None, id_nivel_instruccion=None, 
                        id_profesion=None, historia_clinica=None, observaciones=None,
                        nom_madre=None, tel_madre=None, nom_padre=None, tel_padre=None, 
                        educacion=None, colegio=None, tel_colegio=None):
        """
        Guarda un nuevo paciente completo.
        Campos obligatorios: nombre, apellido, cedula, fecha_nacimiento
        """
        
        # ✅ CORRECCIÓN: Solo validar lo esencial
        if not all([nombre, apellido, cedula, fecha_nacimiento]):
            app.logger.error("Faltan campos obligatorios: nombre, apellido, cedula, fecha_nacimiento")
            return None
        
        
    # ✅ El resto del código sigue igual...
        
        # Validar fecha de nacimiento
        valido, mensaje = self.validar_fecha_nacimiento(fecha_nacimiento)
        if not valido:
            app.logger.error(f"Validación de fecha de nacimiento falló: {mensaje}")
            return None
        
        # Generar historia clínica si no viene
        if not historia_clinica or historia_clinica.strip() == "":
            historia_clinica = self.generar_historia_clinica_unica(nombre, apellido, cedula)
            app.logger.info(f"Historia clínica auto-generada: {historia_clinica}")
        else:
            # Si viene manual, validar que sea única
            if not self.validar_historia_unica(historia_clinica):
                app.logger.error(f"Historia clínica duplicada: {historia_clinica}")
                return None
        
        # Calcular automáticamente si es menor
        es_menor = self.calcular_es_menor(fecha_nacimiento)
        app.logger.info(f"Paciente calculado como menor: {es_menor}")
        
        # Validar datos de menor si aplica
        valido, mensaje = self.validar_datos_menor(es_menor, nom_madre, nom_padre)
        if not valido:
            app.logger.error(f"Validación de datos de menor falló: {mensaje}")
            return None
        
        insertPersonaSQL = """
            INSERT INTO personas(per_nombre, per_apellido, per_cedula, per_fecha_nacimiento, 
                            id_genero, id_estado_civil, per_telefono, per_correo, per_domicilio,
                            id_ciudad, id_ciudad_nacimiento, id_nivel_instruccion, id_profesion)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING id_persona
        """
        
        insertPacienteSQL = """
            INSERT INTO pacientes(id_persona, pac_historia_clinica, pac_observaciones)
            VALUES(%s, %s, %s) 
            RETURNING id_paciente
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
            app.logger.info(f"Insertando persona: {nombre} {apellido}")
            cur.execute(insertPersonaSQL, (nombre, apellido, cedula, fecha_nacimiento, id_genero, 
                                        id_estado_civil, telefono, correo, domicilio, id_ciudad, 
                                        id_ciudad_nacimiento, id_nivel_instruccion, id_profesion))
            persona_id = cur.fetchone()[0]
            app.logger.info(f"Persona insertada con ID: {persona_id}")

            # 2. Insertar paciente
            app.logger.info(f"Insertando paciente con historia clínica: {historia_clinica}")
            cur.execute(insertPacienteSQL, (persona_id, historia_clinica, observaciones))
            paciente_id = cur.fetchone()[0]
            app.logger.info(f"Paciente insertado con ID: {paciente_id}")

            # 3. Si es menor (calculado automáticamente), insertar datos del menor
            if es_menor and (nom_madre or nom_padre):
                app.logger.info(f"Es menor de edad - Insertando datos de tutor(es)")
                app.logger.info(f"Madre: {nom_madre}, Padre: {nom_padre}, Colegio: {colegio}")
                
                cur.execute(insertMenorSQL, (paciente_id, nom_madre, tel_madre, nom_padre, 
                                            tel_padre, educacion, colegio, tel_colegio))
                app.logger.info("Datos de menor insertados correctamente")

            con.commit()
            app.logger.info(f"Paciente guardado exitosamente con ID: {paciente_id}")
            return paciente_id

        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al insertar paciente completo: {str(e)}", exc_info=True)
            return None

        finally:
            cur.close()
            con.close()

    def updatePaciente(self, pac_id, nombre, apellido, cedula, fecha_nacimiento, id_genero, 
                    id_estado_civil, telefono, correo, domicilio, id_ciudad, id_ciudad_nacimiento,
                    id_nivel_instruccion, id_profesion, historia_clinica, observaciones=None, 
                    nom_madre=None, tel_madre=None, nom_padre=None, tel_padre=None, 
                    educacion=None, colegio=None, tel_colegio=None):
        """
        Actualiza un paciente completo (persona + paciente + datos_menor)
        El campo es_menor se calcula automáticamente basado en la fecha de nacimiento
        """
        
        # Validar fecha de nacimiento
        valido, mensaje = self.validar_fecha_nacimiento(fecha_nacimiento)
        if not valido:
            app.logger.error(f"Validación de fecha de nacimiento falló: {mensaje}")
            return False
        
        # Calcular automáticamente si es menor
        es_menor = self.calcular_es_menor(fecha_nacimiento)
        app.logger.info(f"Paciente calculado como menor: {es_menor} (fecha nacimiento: {fecha_nacimiento})")
        
        # Validar datos de menor si aplica
        valido, mensaje = self.validar_datos_menor(es_menor, nom_madre, nom_padre)
        if not valido:
            app.logger.error(f"Validación de datos de menor falló: {mensaje}")
            return False
        
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
            SET pac_historia_clinica = %s, pac_observaciones = %s
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
            app.logger.info(f"Actualizando persona del paciente ID: {pac_id}")
            cur.execute(updatePersonaSQL, (nombre, apellido, cedula, fecha_nacimiento, id_genero,
                                        id_estado_civil, telefono, correo, domicilio, id_ciudad,
                                        id_ciudad_nacimiento, id_nivel_instruccion, 
                                        id_profesion, pac_id))

            # 2. Actualizar paciente
            app.logger.info(f"Actualizando datos del paciente ID: {pac_id}")
            cur.execute(updatePacienteSQL, (historia_clinica, observaciones, pac_id))

            # 3. Manejar datos del menor
            cur.execute("SELECT id_paciente_menor FROM pacientes_menores WHERE id_paciente = %s", (pac_id,))
            existe_menor = cur.fetchone()

            if es_menor:
                # Si es menor (calculado) y tiene datos de tutor
                if nom_madre or nom_padre:
                    if existe_menor:
                        # Actualizar datos existentes
                        app.logger.info(f"Actualizando datos de menor existente para paciente ID: {pac_id}")
                        cur.execute(updateMenorSQL, (nom_madre, tel_madre, nom_padre, tel_padre,
                                                    educacion, colegio, tel_colegio, pac_id))
                    else:
                        # Crear nuevos datos de menor
                        app.logger.info(f"Insertando nuevos datos de menor para paciente ID: {pac_id}")
                        cur.execute(insertMenorSQL, (pac_id, nom_madre, tel_madre, nom_padre,
                                                    tel_padre, educacion, colegio, tel_colegio))
            else:
                # Ya no es menor, eliminar datos si existían
                if existe_menor:
                    app.logger.info(f"Paciente ya no es menor - Eliminando datos de tutor para paciente ID: {pac_id}")
                    cur.execute(deleteMenorSQL, (pac_id,))

            con.commit()
            app.logger.info(f"Paciente {pac_id} actualizado exitosamente")
            return True

        except Exception as e:
            app.logger.error(f"Error al actualizar paciente: {str(e)}", exc_info=True)
            con.rollback()
            return False
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
                app.logger.error(f"No se encontró el paciente con ID: {pac_id}")
                return False
            
            persona_id = resultado[0]
            app.logger.info(f"Eliminando paciente ID: {pac_id} (persona ID: {persona_id})")

            # 1. Eliminar de pacientes_menores (si existe) - CASCADE lo hace automático
            cur.execute("DELETE FROM pacientes_menores WHERE id_paciente = %s", (pac_id,))
            app.logger.info(f"Datos de menor eliminados (si existían)")
            
            # 2. Eliminar de pacientes
            cur.execute("DELETE FROM pacientes WHERE id_paciente = %s", (pac_id,))
            app.logger.info(f"Paciente eliminado")
            
            # 3. Eliminar de personas
            cur.execute("DELETE FROM personas WHERE id_persona = %s", (persona_id,))
            app.logger.info(f"Persona eliminada")

            con.commit()
            app.logger.info(f"Paciente {pac_id} eliminado exitosamente")
            return True

        except Exception as e:
            app.logger.error(f"Error al eliminar paciente: {str(e)}", exc_info=True)
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def getPacientesMenores(self):
        """Obtiene solo los pacientes menores de edad (calculado automáticamente)"""
        pacienteSQL = """
            SELECT
                pac.id_paciente,
                pac.pac_historia_clinica,
                p.per_nombre,
                p.per_apellido,
                p.per_cedula,
                p.per_fecha_nacimiento,
                DATE_PART('year', AGE(p.per_fecha_nacimiento)) AS edad,
                pm.pam_nom_madre,
                pm.pam_nom_padre,
                pm.pam_colegio
            FROM pacientes pac
            JOIN personas p ON pac.id_persona = p.id_persona
            LEFT JOIN pacientes_menores pm ON pac.id_paciente = pm.id_paciente
            WHERE DATE_PART('year', AGE(p.per_fecha_nacimiento)) < 18
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
                'edad': int(r[6]) if r[6] else None,
                'nom_madre': r[7],
                'nom_padre': r[8],
                'colegio': r[9]
            } for r in resultados]
            
        except Exception as e:
            app.logger.error(f"Error al obtener pacientes menores: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()