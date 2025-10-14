from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime, date

class CitaDao:
    
    # =====================================================
    # MÉTODOS PARA MODALES DE BÚSQUEDA
    # =====================================================
    
    def getPacientes(self):
        """
        Obtiene lista de pacientes para el modal de búsqueda
        Endpoint: GET /api/v1/pacientes
        """
        pacientesSQL = """
            SELECT
                p.id_paciente,
                p.pac_historia_clinica,
                CONCAT(per.per_nombre, ' ', per.per_apellido) AS nombre_completo,
                per.per_cedula,
                per.per_telefono,
                per.per_fecha_nacimiento
            FROM pacientes p
            JOIN personas per ON p.id_persona = per.id_persona
            WHERE p.pac_estado = TRUE
            ORDER BY per.per_nombre
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(pacientesSQL)
            pacientes = cur.fetchall()
            
            return [{
                'id_paciente': p[0],
                'historia_clinica': p[1],
                'nombre_completo': p[2],
                'cedula': p[3],
                'telefono': p[4],
                'fecha_nacimiento': p[5].strftime('%d/%m/%Y') if p[5] else None
            } for p in pacientes]
            
        except Exception as e:
            app.logger.error(f"Error al obtener pacientes: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getEspecialistas(self):
        """
        Obtiene lista de especialistas activos
        Endpoint: GET /api/v1/especialistas
        """
        especialistasSQL = """
            SELECT
                e.id_especialista,
                CONCAT(p.per_nombre, ' ', p.per_apellido) AS nombre_completo,
                e.esp_matricula,
                e.esp_color_agenda
            FROM especialistas e
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas p ON f.id_persona = p.id_persona
            WHERE f.fun_estado = TRUE
            ORDER BY p.per_nombre
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(especialistasSQL)
            especialistas = cur.fetchall()
            
            return [{
                'id_especialista': e[0],
                'nombre_completo': e[1],
                'matricula': e[2],
                'color_agenda': e[3]
            } for e in especialistas]
            
        except Exception as e:
            app.logger.error(f"Error al obtener especialistas: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getEspecialidades(self):
        """
        Obtiene lista de especialidades activas
        Endpoint: GET /api/v1/especialidades
        """
        especialidadesSQL = """
            SELECT
                id_especialidad,
                des_especialidad
            FROM especialidades
            WHERE est_especialidad = TRUE
            ORDER BY des_especialidad
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(especialidadesSQL)
            especialidades = cur.fetchall()
            
            return [{
                'id_especialidad': e[0],
                'des_especialidad': e[1]
            } for e in especialidades]
            
        except Exception as e:
            app.logger.error(f"Error al obtener especialidades: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getEstadosCitas(self):
        """
        Obtiene lista de estados de citas
        Endpoint: GET /api/v1/estados-citas
        """
        estadosSQL = """
            SELECT
                id_estado_cita,
                est_cita_nombre,
                est_cita_descripcion,
                est_cita_color
            FROM estados_citas
            WHERE est_cita_activo = TRUE
            ORDER BY id_estado_cita
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(estadosSQL)
            estados = cur.fetchall()
            
            return [{
                'id_estado_cita': e[0],
                'nombre': e[1],
                'descripcion': e[2],
                'color': e[3]
            } for e in estados]
            
        except Exception as e:
            app.logger.error(f"Error al obtener estados de citas: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    # =====================================================
    # CONSULTA DE CUPOS DISPONIBLES
    # =====================================================
    
    def getCuposDisponiblesPorEspecialidad(self, id_especialidad, fecha_inicio, fecha_fin):
        """
        Obtiene cupos disponibles para una especialidad en un rango de fechas
        Usa la función de PostgreSQL obtener_cupos_por_especialidad
        """
        cuposSQL = """
            SELECT * FROM obtener_cupos_por_especialidad(%s, %s, %s)
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(cuposSQL, (id_especialidad, fecha_inicio, fecha_fin))
            cupos = cur.fetchall()
            
            return [{
                'id_especialista': c[0],
                'especialista_nombre': c[1],
                'especialista_color': c[2],
                'dia_semana': c[3],
                'fecha_especifica': c[4].strftime('%Y-%m-%d') if c[4] else None,
                'hora_inicio': str(c[5]),
                'hora_fin': str(c[6]),
                'turno': c[7],
                'cupos_totales': c[8],
                'cupos_ocupados': c[9],
                'cupos_disponibles': c[10],
                'id_agenda_horario': c[11]
            } for c in cupos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener cupos por especialidad: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getCuposDisponiblesPorEspecialista(self, id_especialista, fecha_inicio, fecha_fin):
        """
        Obtiene cupos disponibles para un especialista en un rango de fechas
        Usa la función de PostgreSQL obtener_cupos_por_especialista
        """
        cuposSQL = """
            SELECT * FROM obtener_cupos_por_especialista(%s, %s, %s)
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(cuposSQL, (id_especialista, fecha_inicio, fecha_fin))
            cupos = cur.fetchall()
            
            return [{
                'dia_semana': c[0],
                'fecha_especifica': c[1].strftime('%Y-%m-%d') if c[1] else None,
                'hora_inicio': str(c[2]),
                'hora_fin': str(c[3]),
                'turno': c[4],
                'cupos_totales': c[5],
                'cupos_ocupados': c[6],
                'cupos_disponibles': c[7],
                'id_agenda_horario': c[8]
            } for c in cupos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener cupos por especialista: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    # =====================================================
    # MÉTODOS CRUD COMPLETOS
    # =====================================================
    
    def getAllCitas(self):
        """Obtiene todas las citas activas"""
        citasSQL = """
            SELECT
                c.id_cita,
                c.id_paciente,
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                pp.per_telefono,
                c.id_especialista,
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS especialista_nombre,
                e.esp_color_agenda,
                c.id_especialidad,
                esp.des_especialidad,
                c.cita_fecha,
                c.cita_hora_inicio,
                c.cita_hora_fin,
                c.cita_tipo,
                c.cita_motivo,
                c.cita_observaciones,
                c.cita_numero_sesion,
                c.id_estado_cita,
                ec.est_cita_nombre,
                ec.est_cita_color,
                c.cita_fecha_confirmacion,
                c.cita_creacion_fecha
            FROM citas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN especialistas e ON c.id_especialista = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            JOIN especialidades esp ON c.id_especialidad = esp.id_especialidad
            JOIN estados_citas ec ON c.id_estado_cita = ec.id_estado_cita
            WHERE c.cita_activo = TRUE
            ORDER BY c.cita_fecha DESC, c.cita_hora_inicio DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(citasSQL)
            citas = cur.fetchall()
            
            return [{
                'id_cita': c[0],
                'id_paciente': c[1],
                'historia_clinica': c[2],
                'paciente_nombre': c[3],
                'paciente_telefono': c[4],
                'id_especialista': c[5],
                'especialista_nombre': c[6],
                'especialista_color': c[7],
                'id_especialidad': c[8],
                'especialidad': c[9],
                'cita_fecha': c[10].strftime('%d/%m/%Y') if c[10] else None,
                'cita_hora_inicio': c[11].strftime('%H:%M') if c[11] else None,
                'cita_hora_fin': c[12].strftime('%H:%M') if c[12] else None,
                'cita_tipo': c[13],
                'cita_motivo': c[14],
                'cita_observaciones': c[15],
                'cita_numero_sesion': c[16],
                'id_estado_cita': c[17],
                'estado_nombre': c[18],
                'estado_color': c[19],
                'fecha_confirmacion': c[20].strftime('%d/%m/%Y %H:%M') if c[20] else None,
                'fecha_creacion': c[21].strftime('%d/%m/%Y') if c[21] else None
            } for c in citas]
            
        except Exception as e:
            app.logger.error(f"Error al obtener todas las citas: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getCitaById(self, id_cita):
        """Obtiene una cita específica por ID"""
        citaSQL = """
            SELECT
                c.id_cita,
                c.id_paciente,
                c.id_especialista,
                c.id_especialidad,
                c.id_agenda_horario,
                c.cita_fecha,
                c.cita_hora_inicio,
                c.cita_hora_fin,
                c.cita_tipo,
                c.cita_motivo,
                c.cita_observaciones,
                c.cita_numero_sesion,
                c.id_estado_cita,
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS especialista_nombre,
                esp.des_especialidad,
                ec.est_cita_nombre,
                ec.est_cita_color,
                c.cita_fecha_confirmacion
            FROM citas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN especialistas e ON c.id_especialista = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            JOIN especialidades esp ON c.id_especialidad = esp.id_especialidad
            JOIN estados_citas ec ON c.id_estado_cita = ec.id_estado_cita
            WHERE c.id_cita = %s AND c.cita_activo = TRUE
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(citaSQL, (id_cita,))
            c = cur.fetchone()
            
            if not c:
                return None
            
            return {
                'id_cita': c[0],
                'id_paciente': c[1],
                'id_especialista': c[2],
                'id_especialidad': c[3],
                'id_agenda_horario': c[4],
                'cita_fecha': c[5].strftime('%Y-%m-%d') if c[5] else None,
                'cita_hora_inicio': c[6].strftime('%H:%M') if c[6] else None,
                'cita_hora_fin': c[7].strftime('%H:%M') if c[7] else None,
                'cita_tipo': c[8],
                'cita_motivo': c[9],
                'cita_observaciones': c[10],
                'cita_numero_sesion': c[11],
                'id_estado_cita': c[12],
                'historia_clinica': c[13],
                'paciente_nombre': c[14],
                'especialista_nombre': c[15],
                'especialidad': c[16],
                'estado_nombre': c[17],
                'estado_color': c[18],
                'fecha_confirmacion': c[19].strftime('%d/%m/%Y %H:%M') if c[19] else None
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener cita por ID: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()
    
    def getCitaParaEditar(self, id_cita):
        """Obtiene cita con IDs originales para edición"""
        citaSQL = """
            SELECT
                c.id_cita,
                c.id_paciente,
                c.id_especialista,
                c.id_especialidad,
                c.id_agenda_horario,
                c.cita_fecha,
                c.cita_hora_inicio,
                c.cita_hora_fin,
                c.cita_tipo,
                c.cita_motivo,
                c.cita_observaciones,
                c.cita_numero_sesion,
                c.id_estado_cita,
                -- Descripciones para mostrar
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS especialista_nombre,
                esp.des_especialidad,
                ec.est_cita_nombre
            FROM citas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN especialistas e ON c.id_especialista = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            JOIN especialidades esp ON c.id_especialidad = esp.id_especialidad
            JOIN estados_citas ec ON c.id_estado_cita = ec.id_estado_cita
            WHERE c.id_cita = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(citaSQL, (id_cita,))
            c = cur.fetchone()
            
            if not c:
                return None
            
            return {
                'id_cita': c[0],
                'id_paciente': c[1],
                'id_especialista': c[2],
                'id_especialidad': c[3],
                'id_agenda_horario': c[4],
                'cita_fecha': c[5].strftime('%Y-%m-%d') if c[5] else None,
                'cita_hora_inicio': c[6].strftime('%H:%M') if c[6] else None,
                'cita_hora_fin': c[7].strftime('%H:%M') if c[7] else None,
                'cita_tipo': c[8],
                'cita_motivo': c[9],
                'cita_observaciones': c[10],
                'cita_numero_sesion': c[11],
                'id_estado_cita': c[12],
                # Descripciones
                'historia_clinica': c[13],
                'paciente_nombre': c[14],
                'especialista_nombre': c[15],
                'especialidad': c[16],
                'estado_nombre': c[17]
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener cita para editar: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()
    
    def guardarCita(self, id_paciente, id_agenda_horario, id_especialista, id_especialidad,
                    cita_fecha, cita_hora_inicio, cita_hora_fin, cita_tipo, cita_motivo,
                    cita_creacion_usuario, id_estado_cita=1, cita_observaciones=None,
                    cita_numero_sesion=None):
        """Guarda una nueva cita"""
        
        insertCitaSQL = """
            INSERT INTO citas(
                id_paciente, id_agenda_horario, id_especialista, id_especialidad,
                cita_fecha, cita_hora_inicio, cita_hora_fin, cita_tipo,
                cita_motivo, cita_observaciones, cita_numero_sesion,
                id_estado_cita, cita_creacion_usuario
            )
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_cita
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            app.logger.info(f"Guardando cita tipo {cita_tipo} para paciente ID: {id_paciente}")
            
            cur.execute(insertCitaSQL, (
                id_paciente, id_agenda_horario, id_especialista, id_especialidad,
                cita_fecha, cita_hora_inicio, cita_hora_fin, cita_tipo,
                cita_motivo, cita_observaciones, cita_numero_sesion,
                id_estado_cita, cita_creacion_usuario
            ))
            
            cita_id = cur.fetchone()[0]
            con.commit()
            
            app.logger.info(f"Cita guardada exitosamente con ID: {cita_id}")
            return cita_id
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al guardar cita: {str(e)}", exc_info=True)
            return None
        finally:
            cur.close()
            con.close()
    
    def updateCita(self, id_cita, cita_fecha, cita_hora_inicio, cita_hora_fin,
                   cita_tipo, cita_motivo, cita_observaciones, cita_numero_sesion,
                   id_estado_cita, modificacion_usuario=1):
        """Actualiza una cita existente"""
        
        updateCitaSQL = """
            UPDATE citas
            SET cita_fecha = %s,
                cita_hora_inicio = %s,
                cita_hora_fin = %s,
                cita_tipo = %s,
                cita_motivo = %s,
                cita_observaciones = %s,
                cita_numero_sesion = %s,
                id_estado_cita = %s,
                cita_modificacion_fecha = CURRENT_TIMESTAMP,
                cita_modificacion_usuario = %s
            WHERE id_cita = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(updateCitaSQL, (
                cita_fecha, cita_hora_inicio, cita_hora_fin,
                cita_tipo, cita_motivo, cita_observaciones, cita_numero_sesion,
                id_estado_cita, modificacion_usuario, id_cita
            ))
            
            con.commit()
            app.logger.info(f"Cita {id_cita} actualizada exitosamente")
            return True
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al actualizar cita: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()
    
    def deleteCita(self, id_cita):
        """Elimina lógicamente una cita"""
        deleteCitaSQL = """
            UPDATE citas
            SET cita_activo = FALSE,
                cita_modificacion_fecha = CURRENT_TIMESTAMP
            WHERE id_cita = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(deleteCitaSQL, (id_cita,))
            
            if cur.rowcount == 0:
                return False
            
            con.commit()
            app.logger.info(f"Cita {id_cita} eliminada exitosamente")
            return True
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al eliminar cita: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()
    
    # =====================================================
    # MÉTODOS DE CAMBIO DE ESTADO
    # =====================================================
    
    def cambiarEstadoCita(self, id_cita, id_estado_cita, usuario_id=1):
        """Cambia el estado de una cita"""
        updateSQL = """
            UPDATE citas
            SET id_estado_cita = %s,
                cita_modificacion_fecha = CURRENT_TIMESTAMP,
                cita_modificacion_usuario = %s
            WHERE id_cita = %s AND cita_activo = TRUE
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(updateSQL, (id_estado_cita, usuario_id, id_cita))
            con.commit()
            
            app.logger.info(f"Estado de cita {id_cita} cambiado a {id_estado_cita}")
            return True
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al cambiar estado de cita: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()
    
    def confirmarCita(self, id_cita, usuario_id=1):
        """Confirma una cita (estado CONFIRMADA)"""
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute("SELECT id_estado_cita FROM estados_citas WHERE est_cita_nombre = 'CONFIRMADA'")
            estado = cur.fetchone()
            if estado:
                return self.cambiarEstadoCita(id_cita, estado[0], usuario_id)
            return False
        except Exception as e:
            app.logger.error(f"Error al confirmar cita: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()
    
    def cancelarCita(self, id_cita, usuario_id=1):
        """Cancela una cita (estado CANCELADA)"""
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute("SELECT id_estado_cita FROM estados_citas WHERE est_cita_nombre = 'CANCELADA'")
            estado = cur.fetchone()
            if estado:
                return self.cambiarEstadoCita(id_cita, estado[0], usuario_id)
            return False
        except Exception as e:
            app.logger.error(f"Error al cancelar cita: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()
    
    # =====================================================
    # FILTROS ADICIONALES
    # =====================================================
    
    def getCitasByPaciente(self, id_paciente):
        """Obtiene todas las citas de un paciente"""
        citasSQL = """
            SELECT
                c.id_cita,
                c.cita_fecha,
                c.cita_hora_inicio,
                c.cita_tipo,
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS especialista_nombre,
                esp.des_especialidad,
                ec.est_cita_nombre,
                ec.est_cita_color
            FROM citas c
            JOIN especialistas e ON c.id_especialista = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            JOIN especialidades esp ON c.id_especialidad = esp.id_especialidad
            JOIN estados_citas ec ON c.id_estado_cita = ec.id_estado_cita
            WHERE c.id_paciente = %s AND c.cita_activo = TRUE
            ORDER BY c.cita_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(citasSQL, (id_paciente,))
            citas = cur.fetchall()
            
            return [{
                'id_cita': c[0],
                'fecha': c[1].strftime('%d/%m/%Y') if c[1] else None,
                'hora': c[2].strftime('%H:%M') if c[2] else None,
                'tipo': c[3],
                'especialista': c[4],
                'especialidad': c[5],
                'estado': c[6],
                'estado_color': c[7]
            } for c in citas]
            
        except Exception as e:
            app.logger.error(f"Error al obtener citas del paciente: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getCitasByEspecialista(self, id_especialista):
        """Obtiene todas las citas de un especialista"""
        citasSQL = """
            SELECT
                c.id_cita,
                c.cita_fecha,
                c.cita_hora_inicio,
                c.cita_tipo,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                p.pac_historia_clinica,
                ec.est_cita_nombre,
                ec.est_cita_color
            FROM citas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN estados_citas ec ON c.id_estado_cita = ec.id_estado_cita
            WHERE c.id_especialista = %s AND c.cita_activo = TRUE
            ORDER BY c.cita_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(citasSQL, (id_especialista,))
            citas = cur.fetchall()
            
            return [{
                'id_cita': c[0],
                'fecha': c[1].strftime('%d/%m/%Y') if c[1] else None,
                'hora': c[2].strftime('%H:%M') if c[2] else None,
                'tipo': c[3],
                'paciente': c[4],
                'historia_clinica': c[5],
                'estado': c[6],
                'estado_color': c[7]
            } for c in citas]
            
        except Exception as e:
            app.logger.error(f"Error al obtener citas del especialista: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getCitasByFecha(self, fecha_inicio, fecha_fin):
        """Obtiene citas en un rango de fechas"""
        citasSQL = """
            SELECT
                c.id_cita,
                c.cita_fecha,
                c.cita_hora_inicio,
                c.cita_tipo,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS especialista_nombre,
                esp.des_especialidad,
                ec.est_cita_nombre,
                ec.est_cita_color
            FROM citas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN especialistas e ON c.id_especialista = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            JOIN especialidades esp ON c.id_especialidad = esp.id_especialidad
            JOIN estados_citas ec ON c.id_estado_cita = ec.id_estado_cita
            WHERE c.cita_fecha BETWEEN %s AND %s
                AND c.cita_activo = TRUE
            ORDER BY c.cita_fecha, c.cita_hora_inicio
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(citasSQL, (fecha_inicio, fecha_fin))
            citas = cur.fetchall()
            
            return [{
                'id_cita': c[0],
                'fecha': c[1].strftime('%d/%m/%Y') if c[1] else None,
                'hora': c[2].strftime('%H:%M') if c[2] else None,
                'tipo': c[3],
                'paciente': c[4],
                'especialista': c[5],
                'especialidad': c[6],
                'estado': c[7],
                'estado_color': c[8]
            } for c in citas]
            
        except Exception as e:
            app.logger.error(f"Error al obtener citas por fecha: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()