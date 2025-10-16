from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime, date

class RegistroProcedimientoDao:
    
    def getRegistrosProcedimientos(self):
        """Obtiene todos los registros de procedimientos con sus datos completos"""
        procedimientoSQL = """
            SELECT
                rp.id_registro_procedimiento,
                rp.id_consulta,
                rp.id_paciente,
                rp.id_tipo_procedimiento,
                rp.des_registro_procedimiento,
                rp.registro_fecha,
                rp.registro_duracion,
                rp.registro_resultado,
                rp.registro_observaciones,
                -- Datos de la consulta
                c.consulta_fecha,
                c.consulta_motivo,
                -- Datos del paciente
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                -- Datos del tipo de procedimiento
                tp.des_tipo_procedimiento,
                -- Datos del profesional
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS profesional_nombre,
                e.esp_matricula,
                rp.fecha_creacion
            FROM registro_procedimientos rp
            JOIN consultas c ON rp.id_consulta = c.id_consulta
            JOIN pacientes p ON rp.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN tipos_procedimientos tp ON rp.id_tipo_procedimiento = tp.id_tipo_procedimiento
            JOIN especialistas e ON c.id_profesional = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            WHERE rp.est_registro_procedimiento = 'A'
            ORDER BY rp.registro_fecha DESC, rp.id_registro_procedimiento DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(procedimientoSQL)
            procedimientos = cur.fetchall()
            
            return [{
                'id_registro_procedimiento': p[0],
                'id_consulta': p[1],
                'id_paciente': p[2],
                'id_tipo_procedimiento': p[3],
                'des_registro_procedimiento': p[4],
                'registro_fecha': p[5].strftime('%d/%m/%Y %H:%M') if p[5] else None,
                'registro_duracion': p[6],
                'registro_resultado': p[7],
                'registro_observaciones': p[8],
                'consulta_fecha': p[9].strftime('%d/%m/%Y %H:%M') if p[9] else None,
                'consulta_motivo': p[10],
                'historia_clinica': p[11],
                'paciente_nombre': p[12],
                'tipo_procedimiento': p[13],
                'profesional_nombre': p[14],
                'profesional_matricula': p[15],
                'fecha_registro': p[16].strftime('%d/%m/%Y') if p[16] else None
            } for p in procedimientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener todos los procedimientos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getRegistroProcedimientoById(self, id_registro_procedimiento):
        """Obtiene un registro de procedimiento específico por ID"""
        procedimientoSQL = """
            SELECT
                rp.id_registro_procedimiento,
                rp.id_consulta,
                rp.id_paciente,
                rp.id_tipo_procedimiento,
                rp.des_registro_procedimiento,
                rp.registro_fecha,
                rp.registro_duracion,
                rp.registro_resultado,
                rp.registro_observaciones,
                rp.est_registro_procedimiento,
                -- Datos de la consulta
                c.consulta_fecha,
                c.consulta_motivo,
                -- Datos del paciente
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                pp.per_cedula AS paciente_cedula,
                -- Datos del tipo de procedimiento
                tp.des_tipo_procedimiento,
                -- Datos del profesional
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS profesional_nombre,
                e.esp_matricula,
                rp.fecha_creacion,
                rp.usuario_creacion
            FROM registro_procedimientos rp
            JOIN consultas c ON rp.id_consulta = c.id_consulta
            JOIN pacientes p ON rp.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN tipos_procedimientos tp ON rp.id_tipo_procedimiento = tp.id_tipo_procedimiento
            JOIN especialistas e ON c.id_profesional = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            WHERE rp.id_registro_procedimiento = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(procedimientoSQL, (id_registro_procedimiento,))
            p = cur.fetchone()
            
            if not p:
                return None
            
            return {
                'id_registro_procedimiento': p[0],
                'id_consulta': p[1],
                'id_paciente': p[2],
                'id_tipo_procedimiento': p[3],
                'des_registro_procedimiento': p[4],
                'registro_fecha': p[5].strftime('%d/%m/%Y %H:%M') if p[5] else None,
                'registro_duracion': p[6],
                'registro_resultado': p[7],
                'registro_observaciones': p[8],
                'activo': p[9] == 'A',
                'consulta_fecha': p[10].strftime('%d/%m/%Y %H:%M') if p[10] else None,
                'consulta_motivo': p[11],
                'historia_clinica': p[12],
                'paciente_nombre': p[13],
                'paciente_cedula': p[14],
                'tipo_procedimiento': p[15],
                'profesional_nombre': p[16],
                'profesional_matricula': p[17],
                'fecha_registro': p[18].strftime('%d/%m/%Y') if p[18] else None,
                'usuario_creacion': p[19]
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener procedimiento por ID: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def getRegistroProcedimientoParaEditar(self, id_registro_procedimiento):
        """Obtiene un registro de procedimiento con IDs originales para edición"""
        procedimientoSQL = """
            SELECT
                rp.id_registro_procedimiento,
                rp.id_consulta,
                rp.id_paciente,
                rp.id_tipo_procedimiento,
                rp.des_registro_procedimiento,
                rp.registro_fecha,
                rp.registro_duracion,
                rp.registro_resultado,
                rp.registro_observaciones,
                rp.est_registro_procedimiento,
                -- Descripciones
                c.consulta_motivo,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                p.pac_historia_clinica,
                tp.des_tipo_procedimiento
            FROM registro_procedimientos rp
            JOIN consultas c ON rp.id_consulta = c.id_consulta
            JOIN pacientes p ON rp.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN tipos_procedimientos tp ON rp.id_tipo_procedimiento = tp.id_tipo_procedimiento
            WHERE rp.id_registro_procedimiento = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(procedimientoSQL, (id_registro_procedimiento,))
            p = cur.fetchone()
            
            if not p:
                return None
            
            registro = {
                'id_registro_procedimiento': p[0],
                'id_consulta': p[1],
                'id_paciente': p[2],
                'id_tipo_procedimiento': p[3],
                'des_registro_procedimiento': p[4],
                'registro_fecha': p[5].strftime('%Y-%m-%dT%H:%M') if p[5] else None,
                'registro_duracion': p[6],
                'registro_resultado': p[7],
                'registro_observaciones': p[8],
                'activo': p[9] == 'A',
                # Descripciones
                'consulta_motivo': p[10],
                'paciente_nombre': p[11],
                'historia_clinica': p[12],
                'tipo_procedimiento': p[13]
            }
            
            app.logger.info(f"Procedimiento cargado para editar: ID {registro['id_registro_procedimiento']}")
            
            return registro
            
        except Exception as e:
            app.logger.error(f"Error al obtener procedimiento para editar: {str(e)}", exc_info=True)
            return None
        finally:
            cur.close()
            con.close()

    def guardarRegistroProcedimiento(self, id_consulta, id_paciente, id_tipo_procedimiento,
                                     des_registro_procedimiento, registro_fecha,
                                     registro_duracion=None, registro_resultado=None,
                                     registro_observaciones=None, usuario_creacion='ADMIN'):
        """
        Guarda un nuevo registro de procedimiento médico
        
        Args:
            id_consulta: ID de la consulta (obligatorio)
            id_paciente: ID del paciente (obligatorio)
            id_tipo_procedimiento: ID del tipo de procedimiento del catálogo (obligatorio)
            des_registro_procedimiento: Descripción del procedimiento realizado (obligatorio)
            registro_fecha: Fecha y hora del procedimiento (obligatorio)
            registro_duracion: Duración en minutos (opcional)
            registro_resultado: Resultado del procedimiento (opcional)
            registro_observaciones: Observaciones adicionales (opcional)
            usuario_creacion: Usuario que crea el registro
        """
        
        # Validaciones básicas
        if not all([id_consulta, id_paciente, id_tipo_procedimiento, des_registro_procedimiento, registro_fecha]):
            app.logger.error("Faltan campos obligatorios para guardar procedimiento")
            return None
        
        insertProcedimientoSQL = """
            INSERT INTO registro_procedimientos(
                id_consulta, id_paciente, id_tipo_procedimiento,
                des_registro_procedimiento, est_registro_procedimiento,
                registro_fecha, registro_duracion, registro_resultado,
                registro_observaciones, usuario_creacion
            )
            VALUES(%s, %s, %s, %s, 'A', %s, %s, %s, %s, %s) 
            RETURNING id_registro_procedimiento
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            app.logger.info(f"Insertando procedimiento para consulta ID: {id_consulta}")
            
            cur.execute(insertProcedimientoSQL, (
                id_consulta,
                id_paciente,
                id_tipo_procedimiento,
                des_registro_procedimiento,
                registro_fecha,
                registro_duracion,
                registro_resultado,
                registro_observaciones,
                usuario_creacion
            ))
            
            procedimiento_id = cur.fetchone()[0]
            con.commit()
            
            app.logger.info(f"Procedimiento guardado exitosamente con ID: {procedimiento_id}")
            return procedimiento_id

        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al insertar procedimiento: {str(e)}", exc_info=True)
            return None

        finally:
            cur.close()
            con.close()

    def updateRegistroProcedimiento(self, id_registro_procedimiento, des_registro_procedimiento,
                                    registro_fecha, registro_duracion=None, registro_resultado=None,
                                    registro_observaciones=None, usuario_modificacion='ADMIN'):
        """
        Actualiza un registro de procedimiento existente
        Nota: No se permite cambiar la consulta, paciente ni el tipo de procedimiento
        """
        
        updateProcedimientoSQL = """
            UPDATE registro_procedimientos
            SET des_registro_procedimiento = %s,
                registro_fecha = %s,
                registro_duracion = %s,
                registro_resultado = %s,
                registro_observaciones = %s,
                usuario_modificacion = %s,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_registro_procedimiento = %s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            app.logger.info(f"Actualizando procedimiento ID: {id_registro_procedimiento}")
            
            cur.execute(updateProcedimientoSQL, (
                des_registro_procedimiento,
                registro_fecha,
                registro_duracion,
                registro_resultado,
                registro_observaciones,
                usuario_modificacion,
                id_registro_procedimiento
            ))

            con.commit()
            app.logger.info(f"Procedimiento {id_registro_procedimiento} actualizado exitosamente")
            return True

        except Exception as e:
            app.logger.error(f"Error al actualizar procedimiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteRegistroProcedimiento(self, id_registro_procedimiento):
        """
        Elimina lógicamente un registro de procedimiento (cambia est_registro_procedimiento a 'I')
        """
        deleteProcedimientoSQL = """
            UPDATE registro_procedimientos
            SET est_registro_procedimiento = 'I',
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_registro_procedimiento = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            app.logger.info(f"Eliminando (lógicamente) procedimiento ID: {id_registro_procedimiento}")
            
            cur.execute(deleteProcedimientoSQL, (id_registro_procedimiento,))
            
            if cur.rowcount == 0:
                app.logger.warning(f"No se encontró el procedimiento con ID: {id_registro_procedimiento}")
                return False
            
            con.commit()
            app.logger.info(f"Procedimiento {id_registro_procedimiento} eliminado exitosamente")
            return True

        except Exception as e:
            app.logger.error(f"Error al eliminar procedimiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    def getProcedimientosPorConsulta(self, id_consulta):
        """Obtiene todos los procedimientos registrados en una consulta"""
        procedimientoSQL = """
            SELECT
                rp.id_registro_procedimiento,
                tp.des_tipo_procedimiento,
                rp.registro_fecha,
                rp.registro_duracion,
                rp.registro_resultado,
                rp.des_registro_procedimiento
            FROM registro_procedimientos rp
            JOIN tipos_procedimientos tp ON rp.id_tipo_procedimiento = tp.id_tipo_procedimiento
            WHERE rp.id_consulta = %s AND rp.est_registro_procedimiento = 'A'
            ORDER BY rp.registro_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(procedimientoSQL, (id_consulta,))
            procedimientos = cur.fetchall()
            
            return [{
                'id_registro_procedimiento': p[0],
                'tipo_procedimiento': p[1],
                'fecha': p[2].strftime('%d/%m/%Y %H:%M') if p[2] else None,
                'duracion': p[3],
                'resultado': p[4],
                'descripcion': p[5]
            } for p in procedimientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener procedimientos de la consulta: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getProcedimientosPorPaciente(self, id_paciente):
        """Obtiene todos los procedimientos de un paciente (historial)"""
        procedimientoSQL = """
            SELECT
                rp.id_registro_procedimiento,
                tp.des_tipo_procedimiento,
                rp.registro_fecha,
                rp.registro_duracion,
                rp.registro_resultado,
                c.consulta_fecha,
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS profesional_nombre
            FROM registro_procedimientos rp
            JOIN tipos_procedimientos tp ON rp.id_tipo_procedimiento = tp.id_tipo_procedimiento
            JOIN consultas c ON rp.id_consulta = c.id_consulta
            JOIN especialistas e ON c.id_profesional = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            WHERE rp.id_paciente = %s AND rp.est_registro_procedimiento = 'A'
            ORDER BY rp.registro_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(procedimientoSQL, (id_paciente,))
            procedimientos = cur.fetchall()
            
            return [{
                'id_registro_procedimiento': p[0],
                'tipo_procedimiento': p[1],
                'fecha_procedimiento': p[2].strftime('%d/%m/%Y %H:%M') if p[2] else None,
                'duracion': p[3],
                'resultado': p[4],
                'fecha_consulta': p[5].strftime('%d/%m/%Y') if p[5] else None,
                'profesional': p[6]
            } for p in procedimientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener procedimientos del paciente: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getProcedimientosPorTipo(self, id_tipo_procedimiento):
        """Obtiene registros de un tipo específico de procedimiento"""
        procedimientoSQL = """
            SELECT
                rp.id_registro_procedimiento,
                rp.registro_fecha,
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                rp.registro_duracion,
                rp.registro_resultado
            FROM registro_procedimientos rp
            JOIN pacientes p ON rp.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            WHERE rp.id_tipo_procedimiento = %s AND rp.est_registro_procedimiento = 'A'
            ORDER BY rp.registro_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(procedimientoSQL, (id_tipo_procedimiento,))
            procedimientos = cur.fetchall()
            
            return [{
                'id_registro_procedimiento': p[0],
                'fecha': p[1].strftime('%d/%m/%Y %H:%M') if p[1] else None,
                'historia_clinica': p[2],
                'paciente': p[3],
                'duracion': p[4],
                'resultado': p[5]
            } for p in procedimientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener procedimientos por tipo: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getProcedimientosPorProfesional(self, id_profesional):
        """Obtiene todos los procedimientos realizados por un profesional"""
        procedimientoSQL = """
            SELECT
                rp.id_registro_procedimiento,
                tp.des_tipo_procedimiento,
                rp.registro_fecha,
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                rp.registro_duracion,
                rp.registro_resultado
            FROM registro_procedimientos rp
            JOIN tipos_procedimientos tp ON rp.id_tipo_procedimiento = tp.id_tipo_procedimiento
            JOIN consultas c ON rp.id_consulta = c.id_consulta
            JOIN pacientes p ON rp.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            WHERE c.id_profesional = %s AND rp.est_registro_procedimiento = 'A'
            ORDER BY rp.registro_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(procedimientoSQL, (id_profesional,))
            procedimientos = cur.fetchall()
            
            return [{
                'id_registro_procedimiento': p[0],
                'tipo_procedimiento': p[1],
                'fecha': p[2].strftime('%d/%m/%Y %H:%M') if p[2] else None,
                'historia_clinica': p[3],
                'paciente': p[4],
                'duracion': p[5],
                'resultado': p[6]
            } for p in procedimientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener procedimientos del profesional: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()