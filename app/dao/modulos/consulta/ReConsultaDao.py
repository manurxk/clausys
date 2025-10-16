from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime, date

class ConsultaDao:
    
    def getConsultas(self):
        """Obtiene todas las consultas con sus datos completos"""
        consultaSQL = """
            SELECT
                c.id_consulta,
                c.id_cita,
                c.id_paciente,
                c.id_profesional,
                c.consulta_fecha,
                c.consulta_motivo,
                c.consulta_estado,
                c.des_consulta,
                c.consulta_observaciones,
                -- Datos del paciente
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                pp.per_cedula AS paciente_cedula,
                -- Datos del profesional
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS profesional_nombre,
                e.esp_matricula,
                -- Datos de la cita (si existe)
                cit.cita_tipo,
                c.fecha_creacion
            FROM consultas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN especialistas e ON c.id_profesional = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            LEFT JOIN citas cit ON c.id_cita = cit.id_cita
            WHERE c.est_consulta = 'A'
            ORDER BY c.consulta_fecha DESC, c.id_consulta DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(consultaSQL)
            consultas = cur.fetchall()
            
            return [{
                'id_consulta': c[0],
                'id_cita': c[1],
                'id_paciente': c[2],
                'id_profesional': c[3],
                'consulta_fecha': c[4].strftime('%d/%m/%Y %H:%M') if c[4] else None,
                'consulta_motivo': c[5],
                'consulta_estado': c[6],
                'des_consulta': c[7],
                'consulta_observaciones': c[8],
                'historia_clinica': c[9],
                'paciente_nombre': c[10],
                'paciente_cedula': c[11],
                'profesional_nombre': c[12],
                'profesional_matricula': c[13],
                'cita_tipo': c[14],
                'fecha_registro': c[15].strftime('%d/%m/%Y') if c[15] else None
            } for c in consultas]
            
        except Exception as e:
            app.logger.error(f"Error al obtener todas las consultas: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getConsultaById(self, id_consulta):
        """Obtiene una consulta específica por ID con todos sus datos"""
        consultaSQL = """
            SELECT
                c.id_consulta,
                c.id_cita,
                c.id_paciente,
                c.id_profesional,
                c.consulta_fecha,
                c.consulta_motivo,
                c.consulta_estado,
                c.des_consulta,
                c.consulta_observaciones,
                c.est_consulta,
                -- Datos del paciente
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                pp.per_cedula AS paciente_cedula,
                pp.per_telefono AS paciente_telefono,
                -- Datos del profesional
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS profesional_nombre,
                e.esp_matricula,
                -- Datos de la cita
                cit.cita_tipo,
                cit.cita_hora_inicio,
                cit.cita_hora_fin,
                c.fecha_creacion,
                c.usuario_creacion
            FROM consultas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN especialistas e ON c.id_profesional = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            LEFT JOIN citas cit ON c.id_cita = cit.id_cita
            WHERE c.id_consulta = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(consultaSQL, (id_consulta,))
            c = cur.fetchone()
            
            if not c:
                return None
            
            return {
                'id_consulta': c[0],
                'id_cita': c[1],
                'id_paciente': c[2],
                'id_profesional': c[3],
                'consulta_fecha': c[4].strftime('%d/%m/%Y %H:%M') if c[4] else None,
                'consulta_motivo': c[5],
                'consulta_estado': c[6],
                'des_consulta': c[7],
                'consulta_observaciones': c[8],
                'activo': c[9] == 'A',
                'historia_clinica': c[10],
                'paciente_nombre': c[11],
                'paciente_cedula': c[12],
                'paciente_telefono': c[13],
                'profesional_nombre': c[14],
                'profesional_matricula': c[15],
                'cita_tipo': c[16],
                'cita_hora_inicio': c[17].strftime('%H:%M') if c[17] else None,
                'cita_hora_fin': c[18].strftime('%H:%M') if c[18] else None,
                'fecha_registro': c[19].strftime('%d/%m/%Y') if c[19] else None,
                'usuario_creacion': c[20]
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener consulta por ID: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def getConsultaParaEditar(self, id_consulta):
        """Obtiene una consulta con IDs originales para formulario de edición"""
        consultaSQL = """
            SELECT
                c.id_consulta,
                c.id_cita,
                c.id_paciente,
                c.id_profesional,
                c.consulta_fecha,
                c.consulta_motivo,
                c.consulta_estado,
                c.des_consulta,
                c.consulta_observaciones,
                c.est_consulta,
                -- Descripciones para mostrar
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS profesional_nombre,
                cit.cita_tipo
            FROM consultas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN especialistas e ON c.id_profesional = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            LEFT JOIN citas cit ON c.id_cita = cit.id_cita
            WHERE c.id_consulta = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(consultaSQL, (id_consulta,))
            c = cur.fetchone()
            
            if not c:
                return None
            
            consulta = {
                'id_consulta': c[0],
                'id_cita': c[1],
                'id_paciente': c[2],
                'id_profesional': c[3],
                'consulta_fecha': c[4].strftime('%Y-%m-%dT%H:%M') if c[4] else None,
                'consulta_motivo': c[5],
                'consulta_estado': c[6],
                'des_consulta': c[7],
                'consulta_observaciones': c[8],
                'activo': c[9] == 'A',
                # Descripciones
                'historia_clinica': c[10],
                'paciente_nombre': c[11],
                'profesional_nombre': c[12],
                'cita_tipo': c[13]
            }
            
            app.logger.info(f"Consulta cargada para editar: ID {consulta['id_consulta']}")
            
            return consulta
            
        except Exception as e:
            app.logger.error(f"Error al obtener consulta para editar: {str(e)}", exc_info=True)
            return None
        finally:
            cur.close()
            con.close()

    def guardarConsulta(self, id_paciente, id_profesional, consulta_fecha, consulta_motivo,
                        consulta_estado='PENDIENTE', id_cita=None, des_consulta=None,
                        consulta_observaciones=None, usuario_creacion='ADMIN'):
        """
        Guarda una nueva consulta
        
        Args:
            id_paciente: ID del paciente (obligatorio)
            id_profesional: ID del especialista (obligatorio)
            consulta_fecha: Fecha y hora de la consulta (obligatorio)
            consulta_motivo: Motivo de la consulta (obligatorio)
            consulta_estado: PENDIENTE, EN_ATENCION, FINALIZADA (default: PENDIENTE)
            id_cita: ID de la cita relacionada (opcional)
            des_consulta: Descripción detallada (opcional)
            consulta_observaciones: Observaciones adicionales (opcional)
            usuario_creacion: Usuario que crea el registro
        """
        
        # Validaciones básicas
        if not all([id_paciente, id_profesional, consulta_fecha, consulta_motivo]):
            app.logger.error("Faltan campos obligatorios para guardar consulta")
            return None
        
        insertConsultaSQL = """
            INSERT INTO consultas(
                id_cita, id_paciente, id_profesional, des_consulta, est_consulta,
                consulta_fecha, consulta_motivo, consulta_estado, consulta_observaciones,
                usuario_creacion
            )
            VALUES(%s, %s, %s, %s, 'A', %s, %s, %s, %s, %s) 
            RETURNING id_consulta
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            app.logger.info(f"Insertando consulta para paciente ID: {id_paciente}")
            
            cur.execute(insertConsultaSQL, (
                id_cita,
                id_paciente,
                id_profesional,
                des_consulta,
                consulta_fecha,
                consulta_motivo,
                consulta_estado,
                consulta_observaciones,
                usuario_creacion
            ))
            
            consulta_id = cur.fetchone()[0]
            con.commit()
            
            app.logger.info(f"Consulta guardada exitosamente con ID: {consulta_id}")
            return consulta_id

        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al insertar consulta: {str(e)}", exc_info=True)
            return None

        finally:
            cur.close()
            con.close()

    def updateConsulta(self, id_consulta, consulta_fecha, consulta_motivo, consulta_estado,
                      des_consulta=None, consulta_observaciones=None, usuario_modificacion='ADMIN'):
        """
        Actualiza una consulta existente
        Nota: No se permite cambiar paciente ni profesional una vez creada
        """
        
        updateConsultaSQL = """
            UPDATE consultas
            SET consulta_fecha = %s,
                consulta_motivo = %s,
                consulta_estado = %s,
                des_consulta = %s,
                consulta_observaciones = %s,
                usuario_modificacion = %s,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_consulta = %s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            app.logger.info(f"Actualizando consulta ID: {id_consulta}")
            
            cur.execute(updateConsultaSQL, (
                consulta_fecha,
                consulta_motivo,
                consulta_estado,
                des_consulta,
                consulta_observaciones,
                usuario_modificacion,
                id_consulta
            ))

            con.commit()
            app.logger.info(f"Consulta {id_consulta} actualizada exitosamente")
            return True

        except Exception as e:
            app.logger.error(f"Error al actualizar consulta: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteConsulta(self, id_consulta):
        """
        Elimina lógicamente una consulta (cambia est_consulta a 'I')
        Las relaciones con diagnósticos y procedimientos se mantienen por integridad
        """
        deleteConsultaSQL = """
            UPDATE consultas
            SET est_consulta = 'I',
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_consulta = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            app.logger.info(f"Eliminando (lógicamente) consulta ID: {id_consulta}")
            
            cur.execute(deleteConsultaSQL, (id_consulta,))
            
            if cur.rowcount == 0:
                app.logger.warning(f"No se encontró la consulta con ID: {id_consulta}")
                return False
            
            con.commit()
            app.logger.info(f"Consulta {id_consulta} eliminada exitosamente")
            return True

        except Exception as e:
            app.logger.error(f"Error al eliminar consulta: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    def getConsultasPorPaciente(self, id_paciente):
        """Obtiene todas las consultas de un paciente específico"""
        consultaSQL = """
            SELECT
                c.id_consulta,
                c.consulta_fecha,
                c.consulta_motivo,
                c.consulta_estado,
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS profesional_nombre,
                c.fecha_creacion
            FROM consultas c
            JOIN especialistas e ON c.id_profesional = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            WHERE c.id_paciente = %s AND c.est_consulta = 'A'
            ORDER BY c.consulta_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(consultaSQL, (id_paciente,))
            consultas = cur.fetchall()
            
            return [{
                'id_consulta': c[0],
                'fecha': c[1].strftime('%d/%m/%Y %H:%M') if c[1] else None,
                'motivo': c[2],
                'estado': c[3],
                'profesional': c[4],
                'fecha_registro': c[5].strftime('%d/%m/%Y') if c[5] else None
            } for c in consultas]
            
        except Exception as e:
            app.logger.error(f"Error al obtener consultas del paciente: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getConsultasPorProfesional(self, id_profesional):
        """Obtiene todas las consultas de un profesional específico"""
        consultaSQL = """
            SELECT
                c.id_consulta,
                c.consulta_fecha,
                c.consulta_motivo,
                c.consulta_estado,
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                c.fecha_creacion
            FROM consultas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            WHERE c.id_profesional = %s AND c.est_consulta = 'A'
            ORDER BY c.consulta_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(consultaSQL, (id_profesional,))
            consultas = cur.fetchall()
            
            return [{
                'id_consulta': c[0],
                'fecha': c[1].strftime('%d/%m/%Y %H:%M') if c[1] else None,
                'motivo': c[2],
                'estado': c[3],
                'historia_clinica': c[4],
                'paciente': c[5],
                'fecha_registro': c[6].strftime('%d/%m/%Y') if c[6] else None
            } for c in consultas]
            
        except Exception as e:
            app.logger.error(f"Error al obtener consultas del profesional: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getConsultasPorEstado(self, estado):
        """Obtiene consultas filtradas por estado"""
        consultaSQL = """
            SELECT
                c.id_consulta,
                c.consulta_fecha,
                c.consulta_motivo,
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS profesional_nombre
            FROM consultas c
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN especialistas e ON c.id_profesional = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            WHERE c.consulta_estado = %s AND c.est_consulta = 'A'
            ORDER BY c.consulta_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(consultaSQL, (estado,))
            consultas = cur.fetchall()
            
            return [{
                'id_consulta': c[0],
                'fecha': c[1].strftime('%d/%m/%Y %H:%M') if c[1] else None,
                'motivo': c[2],
                'historia_clinica': c[3],
                'paciente': c[4],
                'profesional': c[5]
            } for c in consultas]
            
        except Exception as e:
            app.logger.error(f"Error al obtener consultas por estado: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getConsultaDesdeCita(self, id_cita):
        """Obtiene la consulta asociada a una cita específica"""
        consultaSQL = """
            SELECT id_consulta
            FROM consultas
            WHERE id_cita = %s AND est_consulta = 'A'
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(consultaSQL, (id_cita,))
            result = cur.fetchone()
            
            if result:
                return self.getConsultaById(result[0])
            return None
            
        except Exception as e:
            app.logger.error(f"Error al obtener consulta desde cita: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()