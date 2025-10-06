from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import date

class FuncionarioDao:
    
    # IDs de cargos que requieren datos de especialista
    CARGOS_ESPECIALISTAS = [3]  # Ajustar según tus IDs reales
    
    def es_cargo_especialista(self, id_cargo):
        """Verifica si un cargo requiere datos de especialista"""
        return id_cargo in self.CARGOS_ESPECIALISTAS

    def getFuncionarios(self):
        """Obtiene todos los funcionarios con sus datos completos"""
        funcionarioSQL = """
            SELECT
                f.id_funcionario,
                p.per_nombre,
                p.per_apellido,
                p.per_cedula,
                p.per_fecha_nacimiento,
                DATE_PART('year', AGE(p.per_fecha_nacimiento)) AS edad,
                p.per_telefono,
                g.des_genero AS genero,
                c.des_ciudad AS ciudad,
                car.des_cargo AS cargo,
                f.fun_estado,
                e.esp_matricula,
                STRING_AGG(DISTINCT esp.des_especialidad, ', ') AS especialidades,
                CASE WHEN e.id_especialista IS NOT NULL THEN TRUE ELSE FALSE END AS es_especialista,
                p.per_fecha_inscripcion
            FROM funcionarios f
            JOIN personas p ON f.id_persona = p.id_persona
            JOIN cargos car ON f.id_cargo = car.id_cargo
            LEFT JOIN generos g ON p.id_genero = g.id_genero AND g.est_genero = TRUE
            LEFT JOIN ciudades c ON p.id_ciudad = c.id_ciudad AND c.est_ciudad = TRUE
            LEFT JOIN especialistas e ON f.id_funcionario = e.id_funcionario
            LEFT JOIN especialista_especialidades ee ON e.id_especialista = ee.id_especialista
            LEFT JOIN especialidades esp ON ee.id_especialidad = esp.id_especialidad AND esp.est_especialidad = TRUE
            GROUP BY f.id_funcionario, p.per_nombre, p.per_apellido, p.per_cedula, 
                     p.per_fecha_nacimiento, p.per_telefono, g.des_genero, c.des_ciudad, 
                     car.des_cargo, f.fun_estado, e.esp_matricula, e.id_especialista, 
                     p.per_fecha_inscripcion
            ORDER BY f.id_funcionario DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(funcionarioSQL)
            funcionarios = cur.fetchall()
            
            return [{
                'id_funcionario': f[0],
                'nombre': f[1],
                'apellido': f[2],
                'cedula': f[3],
                'fecha_nacimiento': f[4].strftime('%d/%m/%Y') if f[4] else None,
                'edad': int(f[5]) if f[5] else None,
                'telefono': f[6],
                'genero': f[7],
                'ciudad': f[8],
                'cargo': f[9],
                'activo': f[10],
                'matricula': f[11],
                'especialidades': f[12],
                'es_especialista': f[13],
                'fecha_registro': f[14].strftime('%d/%m/%Y') if f[14] else None
            } for f in funcionarios]
            
        except Exception as e:
            app.logger.error(f"Error al obtener todos los funcionarios: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getFuncionarioById(self, id_funcionario):
        """Obtiene un funcionario específico por ID con todos sus datos"""
        funcionarioSQL = """
            SELECT
                f.id_funcionario,
                f.fun_estado,
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
                car.des_cargo AS cargo,
                p.per_fecha_inscripcion,
                e.esp_matricula,
                e.esp_color_agenda,
                STRING_AGG(esp.des_especialidad, ', ') AS especialidades
            FROM funcionarios f
            JOIN personas p ON f.id_persona = p.id_persona
            JOIN cargos car ON f.id_cargo = car.id_cargo
            LEFT JOIN generos g ON p.id_genero = g.id_genero AND g.est_genero = TRUE
            LEFT JOIN estados_civiles ec ON p.id_estado_civil = ec.id_estado_civil AND ec.est_estado_civil = TRUE
            LEFT JOIN ciudades c ON p.id_ciudad = c.id_ciudad AND c.est_ciudad = TRUE
            LEFT JOIN ciudades cn ON p.id_ciudad_nacimiento = cn.id_ciudad AND cn.est_ciudad = TRUE
            LEFT JOIN niveles_instruccion ni ON p.id_nivel_instruccion = ni.id_nivel_instruccion AND ni.est_nivel_instruccion = TRUE
            LEFT JOIN profesiones pr ON p.id_profesion = pr.id_profesion AND pr.est_profesion = TRUE
            LEFT JOIN especialistas e ON f.id_funcionario = e.id_funcionario
            LEFT JOIN especialista_especialidades ee ON e.id_especialista = ee.id_especialista
            LEFT JOIN especialidades esp ON ee.id_especialidad = esp.id_especialidad AND esp.est_especialidad = TRUE
            WHERE f.id_funcionario = %s
            GROUP BY f.id_funcionario, f.fun_estado, p.per_nombre, p.per_apellido, p.per_cedula,
                     p.per_fecha_nacimiento, p.per_telefono, p.per_correo, p.per_domicilio,
                     g.des_genero, ec.des_estado_civil, c.des_ciudad, cn.des_ciudad,
                     ni.des_nivel_instruccion, pr.des_profesion, car.des_cargo,
                     p.per_fecha_inscripcion, e.esp_matricula, e.esp_color_agenda
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(funcionarioSQL, (id_funcionario,))
            f = cur.fetchone()
            
            if not f:
                return None
            
            return {
                'id_funcionario': f[0],
                'activo': f[1],
                'nombre': f[2],
                'apellido': f[3],
                'cedula': f[4],
                'fecha_nacimiento': f[5].strftime('%d/%m/%Y') if f[5] else None,
                'edad': int(f[6]) if f[6] else None,
                'telefono': f[7],
                'correo': f[8],
                'domicilio': f[9],
                'genero': f[10],
                'estado_civil': f[11],
                'ciudad': f[12],
                'ciudad_nacimiento': f[13],
                'nivel_instruccion': f[14],
                'profesion': f[15],
                'cargo': f[16],
                'fecha_registro': f[17].strftime('%d/%m/%Y') if f[17] else None,
                'matricula': f[18],
                'color_agenda': f[19],
                'especialidades': f[20]
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener funcionario por ID: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def getFuncionarioParaEditar(self, id_funcionario):
        """Obtiene un funcionario con IDs y descripciones para edición"""
        funcionarioSQL = """
            SELECT
                f.id_funcionario,
                f.id_persona,
                f.id_cargo,
                f.fun_estado,
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
                e.id_especialista,
                e.esp_matricula,
                e.esp_color_agenda,
                g.des_genero,
                ec.des_estado_civil,
                c.des_ciudad,
                cn.des_ciudad,
                ni.des_nivel_instruccion,
                pr.des_profesion,
                car.des_cargo
            FROM funcionarios f
            JOIN personas p ON f.id_persona = p.id_persona
            JOIN cargos car ON f.id_cargo = car.id_cargo
            LEFT JOIN generos g ON p.id_genero = g.id_genero
            LEFT JOIN estados_civiles ec ON p.id_estado_civil = ec.id_estado_civil
            LEFT JOIN ciudades c ON p.id_ciudad = c.id_ciudad
            LEFT JOIN ciudades cn ON p.id_ciudad_nacimiento = cn.id_ciudad
            LEFT JOIN niveles_instruccion ni ON p.id_nivel_instruccion = ni.id_nivel_instruccion
            LEFT JOIN profesiones pr ON p.id_profesion = pr.id_profesion
            LEFT JOIN especialistas e ON f.id_funcionario = e.id_funcionario
            WHERE f.id_funcionario = %s
        """
        
        especialidadesSQL = """
            SELECT ee.id_especialidad
            FROM especialista_especialidades ee
            JOIN especialistas e ON ee.id_especialista = e.id_especialista
            WHERE e.id_funcionario = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(funcionarioSQL, (id_funcionario,))
            f = cur.fetchone()
            
            if not f:
                return None
            
            funcionario = {
                'id_funcionario': f[0],
                'id_persona': f[1],
                'id_cargo': f[2],
                'activo': f[3],
                'nombre': f[4],
                'apellido': f[5],
                'cedula': f[6],
                'fecha_nacimiento': f[7].strftime('%Y-%m-%d') if f[7] else None,
                'telefono': f[8],
                'correo': f[9],
                'domicilio': f[10],
                'id_genero': f[11],
                'id_estado_civil': f[12],
                'id_ciudad': f[13],
                'id_ciudad_nacimiento': f[14],
                'id_nivel_instruccion': f[15],
                'id_profesion': f[16],
                'id_especialista': f[17],
                'matricula': f[18],
                'color_agenda': f[19],
                # Descripciones para mostrar en el formulario
                'genero': f[20],
                'estado_civil': f[21],
                'ciudad': f[22],
                'ciudad_nacimiento': f[23],
                'nivel_instruccion': f[24],
                'profesion': f[25],
                'cargo': f[26],
                'especialidades': []
            }
            
            # Obtener IDs de especialidades
            cur.execute(especialidadesSQL, (id_funcionario,))
            especialidades = cur.fetchall()
            funcionario['especialidades'] = [e[0] for e in especialidades]
            
            app.logger.info(f"Funcionario cargado para editar: {funcionario['nombre']} - Especialidades: {funcionario['especialidades']}")
            
            return funcionario
            
        except Exception as e:
            app.logger.error(f"Error al obtener funcionario para editar: {str(e)}", exc_info=True)
            return None
        finally:
            cur.close()
            con.close()

    def guardarFuncionario(self, nombre, apellido, cedula, fecha_nacimiento, genero_id, estado_civil_id, 
                      telefono, correo, domicilio, ciudad_id, ciudad_nacimiento_id, nivel_instruccion_id, 
                      profesion_id, id_cargo, fun_estado=True, creacion_usuario=1,
                      esp_matricula=None, especialidades=None, esp_color_agenda='#3498db'):
        """
        Guarda un nuevo funcionario completo (persona + funcionario + especialista si aplica)
        
        Args:
            especialidades: lista de IDs de especialidades [1, 2, 8]
        """
        
        # Validar si es especialista
        if self.es_cargo_especialista(id_cargo):
            if not esp_matricula:
                app.logger.error("Matrícula es obligatoria para especialistas")
                return None
            if not especialidades or len(especialidades) == 0:
                app.logger.error("Debe seleccionar al menos una especialidad")
                return None
        
        insertPersonaSQL = """
            INSERT INTO personas(per_nombre, per_apellido, per_cedula, per_fecha_nacimiento, 
                            id_genero, id_estado_civil, per_telefono, per_correo, per_domicilio,
                            id_ciudad, id_ciudad_nacimiento, id_nivel_instruccion, id_profesion)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING id_persona
        """
        
        insertFuncionarioSQL = """
            INSERT INTO funcionarios(id_persona, id_cargo, fun_estado, creacion_usuario)
            VALUES(%s, %s, %s, %s) 
            RETURNING id_funcionario
        """
        
        insertEspecialistaSQL = """
            INSERT INTO especialistas(id_funcionario, esp_matricula, esp_color_agenda)
            VALUES(%s, %s, %s) 
            RETURNING id_especialista
        """
        
        insertEspecialidadSQL = """
            INSERT INTO especialista_especialidades(id_especialista, id_especialidad)
            VALUES(%s, %s)
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            # 1. Insertar persona
            app.logger.info(f"Insertando persona: {nombre} {apellido}")
            cur.execute(insertPersonaSQL, (nombre, apellido, cedula, fecha_nacimiento, genero_id, 
                                        estado_civil_id, telefono, correo, domicilio, ciudad_id, 
                                        ciudad_nacimiento_id, nivel_instruccion_id, profesion_id))
            persona_id = cur.fetchone()[0]
            app.logger.info(f"Persona insertada con ID: {persona_id}")

            # 2. Insertar funcionario
            app.logger.info(f"Insertando funcionario con cargo ID: {id_cargo}")
            cur.execute(insertFuncionarioSQL, (persona_id, id_cargo, fun_estado, creacion_usuario))
            funcionario_id = cur.fetchone()[0]
            app.logger.info(f"Funcionario insertado con ID: {funcionario_id}")

            # 3. Si es especialista, insertar en especialistas
            if self.es_cargo_especialista(id_cargo) and esp_matricula:
                app.logger.info(f"Es especialista - Insertando datos de especialista")
                app.logger.info(f"Matrícula: {esp_matricula}, Color: {esp_color_agenda}")
                
                cur.execute(insertEspecialistaSQL, (funcionario_id, esp_matricula, esp_color_agenda))
                result = cur.fetchone()
                
                if not result:
                    raise Exception("No se pudo obtener el ID del especialista insertado")
                
                especialista_id = result[0]
                app.logger.info(f"Especialista insertado con ID: {especialista_id}")
                
                # 4. Insertar especialidades (múltiples)
                if especialidades:
                    app.logger.info(f"Insertando {len(especialidades)} especialidades: {especialidades}")
                    for id_especialidad in especialidades:
                        app.logger.info(f"Insertando relación - especialista_id: {especialista_id}, especialidad_id: {id_especialidad}")
                        cur.execute(insertEspecialidadSQL, (especialista_id, id_especialidad))
                    app.logger.info("Todas las especialidades insertadas correctamente")

            con.commit()
            app.logger.info(f"Funcionario guardado exitosamente con ID: {funcionario_id}")
            return funcionario_id

        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al insertar funcionario completo: {str(e)}", exc_info=True)
            return None

        finally:
            cur.close()
            con.close()

    def updateFuncionario(self, id_funcionario, nombre, apellido, cedula, fecha_nacimiento, genero_id, 
                        estado_civil_id, telefono, correo, domicilio, ciudad_id, ciudad_nacimiento_id,
                        nivel_instruccion_id, profesion_id, id_cargo, fun_estado,
                        esp_matricula=None, especialidades=None, esp_color_agenda='#3498db'):
        """Actualiza un funcionario completo (persona + funcionario + especialista + especialidades)"""
        
        # Validar si es especialista
        if self.es_cargo_especialista(id_cargo):
            if not esp_matricula:
                app.logger.error("Matrícula es obligatoria para especialistas")
                return False
            if not especialidades or len(especialidades) == 0:
                app.logger.error("Debe seleccionar al menos una especialidad")
                return False
        
        updatePersonaSQL = """
            UPDATE personas
            SET per_nombre = %s, per_apellido = %s, per_cedula = %s, per_fecha_nacimiento = %s,
                id_genero = %s, id_estado_civil = %s, per_telefono = %s, per_correo = %s,
                per_domicilio = %s, id_ciudad = %s, id_ciudad_nacimiento = %s,
                id_nivel_instruccion = %s, id_profesion = %s
            WHERE id_persona = (SELECT id_persona FROM funcionarios WHERE id_funcionario = %s)
        """
        
        updateFuncionarioSQL = """
            UPDATE funcionarios
            SET id_cargo = %s, fun_estado = %s, modificacion_fecha = CURRENT_DATE, 
                modificacion_hora = CURRENT_TIME
            WHERE id_funcionario = %s
        """
        
        updateEspecialistaSQL = """
            UPDATE especialistas
            SET esp_matricula = %s, esp_color_agenda = %s
            WHERE id_funcionario = %s
        """
        
        insertEspecialistaSQL = """
            INSERT INTO especialistas(id_funcionario, esp_matricula, esp_color_agenda)
            VALUES(%s, %s, %s) 
            RETURNING id_especialista
        """
        
        deleteEspecialidadesSQL = """
            DELETE FROM especialista_especialidades 
            WHERE id_especialista = (SELECT id_especialista FROM especialistas WHERE id_funcionario = %s)
        """
        
        insertEspecialidadSQL = """
            INSERT INTO especialista_especialidades(id_especialista, id_especialidad)
            VALUES(%s, %s)
        """
        
        deleteEspecialistaSQL = """
            DELETE FROM especialistas WHERE id_funcionario = %s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            # 1. Actualizar persona
            cur.execute(updatePersonaSQL, (nombre, apellido, cedula, fecha_nacimiento, genero_id,
                                        estado_civil_id, telefono, correo, domicilio, ciudad_id,
                                        ciudad_nacimiento_id, nivel_instruccion_id, 
                                        profesion_id, id_funcionario))

            # 2. Actualizar funcionario
            cur.execute(updateFuncionarioSQL, (id_cargo, fun_estado, id_funcionario))

            # 3. Manejar datos de especialista
            cur.execute("SELECT id_especialista FROM especialistas WHERE id_funcionario = %s", (id_funcionario,))
            existe_especialista = cur.fetchone()

            if self.es_cargo_especialista(id_cargo):
                # Si debe ser especialista
                if esp_matricula:
                    if existe_especialista:
                        # Actualizar especialista existente
                        cur.execute(updateEspecialistaSQL, (esp_matricula, esp_color_agenda, id_funcionario))
                        id_especialista = existe_especialista[0]
                    else:
                        # Crear nuevo especialista
                        cur.execute(insertEspecialistaSQL, (id_funcionario, esp_matricula, esp_color_agenda))
                        id_especialista = cur.fetchone()[0]
                    
                    # Actualizar especialidades: eliminar viejas e insertar nuevas
                    cur.execute(deleteEspecialidadesSQL, (id_funcionario,))
                    
                    if especialidades:
                        for id_especialidad in especialidades:
                            # ✅ CORRECCIÓN: Solo 2 parámetros, no 3
                            cur.execute(insertEspecialidadSQL, (id_especialista, id_especialidad))
            else:
                # Si ya no es especialista, eliminar datos
                if existe_especialista:
                    cur.execute(deleteEspecialidadesSQL, (id_funcionario,))
                    cur.execute(deleteEspecialistaSQL, (id_funcionario,))

            con.commit()
            app.logger.info(f"Funcionario {id_funcionario} actualizado exitosamente")
            return True

        except Exception as e:
            app.logger.error(f"Error al actualizar funcionario: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteFuncionario(self, id_funcionario):
        """
        Elimina un funcionario completo (en cascada: especialista_especialidades -> especialistas -> funcionarios -> personas)
        """
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            # Obtener el id_persona antes de eliminar
            cur.execute("SELECT id_persona FROM funcionarios WHERE id_funcionario = %s", (id_funcionario,))
            resultado = cur.fetchone()
            
            if not resultado:
                return False
            
            persona_id = resultado[0]

            # Las especialidades se eliminan automáticamente por CASCADE
            # 1. Eliminar especialista (si existe) - CASCADE eliminará especialista_especialidades
            cur.execute("DELETE FROM especialistas WHERE id_funcionario = %s", (id_funcionario,))
            
            # 2. Eliminar funcionario
            cur.execute("DELETE FROM funcionarios WHERE id_funcionario = %s", (id_funcionario,))
            
            # 3. Eliminar persona
            cur.execute("DELETE FROM personas WHERE id_persona = %s", (persona_id,))

            con.commit()
            return True

        except Exception as e:
            app.logger.error(f"Error al eliminar funcionario: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def getFuncionariosEspecialistas(self):
        """Obtiene solo los funcionarios que son especialistas"""
        funcionarioSQL = """
            SELECT
                f.id_funcionario,
                p.per_nombre,
                p.per_apellido,
                p.per_cedula,
                p.per_telefono,
                e.esp_matricula,
                e.esp_color_agenda,
                STRING_AGG(esp.des_especialidad, ', ') AS especialidades
            FROM funcionarios f
            JOIN personas p ON f.id_persona = p.id_persona
            JOIN especialistas e ON f.id_funcionario = e.id_funcionario
            LEFT JOIN especialista_especialidades ee ON e.id_especialista = ee.id_especialista
            LEFT JOIN especialidades esp ON ee.id_especialidad = esp.id_especialidad AND esp.est_especialidad = TRUE
            WHERE f.fun_estado = TRUE
            GROUP BY f.id_funcionario, p.per_nombre, p.per_apellido, p.per_cedula, 
                     p.per_telefono, e.esp_matricula, e.esp_color_agenda
            ORDER BY p.per_nombre
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(funcionarioSQL)
            resultados = cur.fetchall()
            return [{
                'id_funcionario': r[0],
                'nombre': r[1],
                'apellido': r[2],
                'cedula': r[3],
                'telefono': r[4],
                'matricula': r[5],
                'color_agenda': r[6],
                'especialidades': r[7]
            } for r in resultados]
        except Exception as e:
            app.logger.error(f"Error al obtener funcionarios especialistas: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()