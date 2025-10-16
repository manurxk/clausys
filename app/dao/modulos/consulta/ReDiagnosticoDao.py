from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime, date

class RegistroDiagnosticoDao:
    
    def getRegistrosDiagnosticos(self):
        """Obtiene todos los registros de diagnósticos con sus datos completos"""
        diagnosticoSQL = """
            SELECT
                rd.id_registro_diagnostico,
                rd.id_consulta,
                rd.id_diagnostico,
                rd.des_registro_diagnostico,
                rd.registro_tipo,
                rd.registro_gravedad,
                rd.registro_fecha,
                rd.registro_observaciones,
                -- Datos de la consulta
                c.consulta_fecha,
                c.consulta_motivo,
                -- Datos del paciente
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                -- Datos del diagnóstico
                d.des_diagnostico,
                d.diagnostico_codigo_cie10,
                -- Datos del profesional
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS profesional_nombre,
                rd.fecha_creacion
            FROM registro_diagnosticos rd
            JOIN consultas c ON rd.id_consulta = c.id_consulta
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN diagnosticos d ON rd.id_diagnostico = d.id_diagnostico
            JOIN especialistas e ON c.id_profesional = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            WHERE rd.est_registro_diagnostico = 'A'
            ORDER BY rd.registro_fecha DESC, rd.id_registro_diagnostico DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(diagnosticoSQL)
            diagnosticos = cur.fetchall()
            
            return [{
                'id_registro_diagnostico': d[0],
                'id_consulta': d[1],
                'id_diagnostico': d[2],
                'des_registro_diagnostico': d[3],
                'registro_tipo': d[4],
                'registro_gravedad': d[5],
                'registro_fecha': d[6].strftime('%d/%m/%Y') if d[6] else None,
                'registro_observaciones': d[7],
                'consulta_fecha': d[8].strftime('%d/%m/%Y %H:%M') if d[8] else None,
                'consulta_motivo': d[9],
                'historia_clinica': d[10],
                'paciente_nombre': d[11],
                'diagnostico': d[12],
                'codigo_cie10': d[13],
                'profesional_nombre': d[14],
                'fecha_registro': d[15].strftime('%d/%m/%Y') if d[15] else None
            } for d in diagnosticos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener todos los diagnósticos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getRegistroDiagnosticoById(self, id_registro_diagnostico):
        """Obtiene un registro de diagnóstico específico por ID"""
        diagnosticoSQL = """
            SELECT
                rd.id_registro_diagnostico,
                rd.id_consulta,
                rd.id_diagnostico,
                rd.des_registro_diagnostico,
                rd.registro_tipo,
                rd.registro_gravedad,
                rd.registro_fecha,
                rd.registro_observaciones,
                rd.est_registro_diagnostico,
                -- Datos de la consulta
                c.consulta_fecha,
                c.consulta_motivo,
                c.id_paciente,
                -- Datos del paciente
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                pp.per_cedula AS paciente_cedula,
                -- Datos del diagnóstico
                d.des_diagnostico,
                d.diagnostico_codigo_cie10,
                -- Datos del profesional
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS profesional_nombre,
                rd.fecha_creacion,
                rd.usuario_creacion
            FROM registro_diagnosticos rd
            JOIN consultas c ON rd.id_consulta = c.id_consulta
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN diagnosticos d ON rd.id_diagnostico = d.id_diagnostico
            JOIN especialistas e ON c.id_profesional = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            WHERE rd.id_registro_diagnostico = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(diagnosticoSQL, (id_registro_diagnostico,))
            d = cur.fetchone()
            
            if not d:
                return None
            
            return {
                'id_registro_diagnostico': d[0],
                'id_consulta': d[1],
                'id_diagnostico': d[2],
                'des_registro_diagnostico': d[3],
                'registro_tipo': d[4],
                'registro_gravedad': d[5],
                'registro_fecha': d[6].strftime('%d/%m/%Y') if d[6] else None,
                'registro_observaciones': d[7],
                'activo': d[8] == 'A',
                'consulta_fecha': d[9].strftime('%d/%m/%Y %H:%M') if d[9] else None,
                'consulta_motivo': d[10],
                'id_paciente': d[11],
                'historia_clinica': d[12],
                'paciente_nombre': d[13],
                'paciente_cedula': d[14],
                'diagnostico': d[15],
                'codigo_cie10': d[16],
                'profesional_nombre': d[17],
                'fecha_registro': d[18].strftime('%d/%m/%Y') if d[18] else None,
                'usuario_creacion': d[19]
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener diagnóstico por ID: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def getRegistroDiagnosticoParaEditar(self, id_registro_diagnostico):
        """Obtiene un registro de diagnóstico con IDs originales para edición"""
        diagnosticoSQL = """
            SELECT
                rd.id_registro_diagnostico,
                rd.id_consulta,
                rd.id_diagnostico,
                rd.des_registro_diagnostico,
                rd.registro_tipo,
                rd.registro_gravedad,
                rd.registro_fecha,
                rd.registro_observaciones,
                rd.est_registro_diagnostico,
                -- Descripciones
                c.consulta_motivo,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                d.des_diagnostico,
                d.diagnostico_codigo_cie10
            FROM registro_diagnosticos rd
            JOIN consultas c ON rd.id_consulta = c.id_consulta
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            JOIN diagnosticos d ON rd.id_diagnostico = d.id_diagnostico
            WHERE rd.id_registro_diagnostico = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(diagnosticoSQL, (id_registro_diagnostico,))
            d = cur.fetchone()
            
            if not d:
                return None
            
            registro = {
                'id_registro_diagnostico': d[0],
                'id_consulta': d[1],
                'id_diagnostico': d[2],
                'des_registro_diagnostico': d[3],
                'registro_tipo': d[4],
                'registro_gravedad': d[5],
                'registro_fecha': d[6].strftime('%Y-%m-%d') if d[6] else None,
                'registro_observaciones': d[7],
                'activo': d[8] == 'A',
                # Descripciones
                'consulta_motivo': d[9],
                'paciente_nombre': d[10],
                'diagnostico': d[11],
                'codigo_cie10': d[12]
            }
            
            app.logger.info(f"Diagnóstico cargado para editar: ID {registro['id_registro_diagnostico']}")
            
            return registro
            
        except Exception as e:
            app.logger.error(f"Error al obtener diagnóstico para editar: {str(e)}", exc_info=True)
            return None
        finally:
            cur.close()
            con.close()

    def guardarRegistroDiagnostico(self, id_consulta, id_diagnostico, registro_fecha,
                                   registro_tipo='PRESUNTIVO', registro_gravedad=None,
                                   des_registro_diagnostico=None, registro_observaciones=None,
                                   usuario_creacion='ADMIN'):
        """
        Guarda un nuevo registro de diagnóstico
        
        Args:
            id_consulta: ID de la consulta (obligatorio)
            id_diagnostico: ID del diagnóstico del catálogo (obligatorio)
            registro_fecha: Fecha del diagnóstico (obligatorio)
            registro_tipo: PRESUNTIVO, DEFINITIVO, DIFERENCIAL (default: PRESUNTIVO)
            registro_gravedad: LEVE, MODERADO, GRAVE (opcional)
            des_registro_diagnostico: Descripción específica (opcional)
            registro_observaciones: Observaciones adicionales (opcional)
            usuario_creacion: Usuario que crea el registro
        """
        
        # Validaciones básicas
        if not all([id_consulta, id_diagnostico, registro_fecha]):
            app.logger.error("Faltan campos obligatorios para guardar diagnóstico")
            return None
        
        insertDiagnosticoSQL = """
            INSERT INTO registro_diagnosticos(
                id_consulta, id_diagnostico, des_registro_diagnostico,
                est_registro_diagnostico, registro_tipo, registro_gravedad,
                registro_fecha, registro_observaciones, usuario_creacion
            )
            VALUES(%s, %s, %s, 'A', %s, %s, %s, %s, %s) 
            RETURNING id_registro_diagnostico
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            app.logger.info(f"Insertando diagnóstico para consulta ID: {id_consulta}")
            
            cur.execute(insertDiagnosticoSQL, (
                id_consulta,
                id_diagnostico,
                des_registro_diagnostico,
                registro_tipo,
                registro_gravedad,
                registro_fecha,
                registro_observaciones,
                usuario_creacion
            ))
            
            diagnostico_id = cur.fetchone()[0]
            con.commit()
            
            app.logger.info(f"Diagnóstico guardado exitosamente con ID: {diagnostico_id}")
            return diagnostico_id

        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al insertar diagnóstico: {str(e)}", exc_info=True)
            return None

        finally:
            cur.close()
            con.close()

    def updateRegistroDiagnostico(self, id_registro_diagnostico, registro_tipo, registro_gravedad,
                                  registro_fecha, des_registro_diagnostico=None,
                                  registro_observaciones=None, usuario_modificacion='ADMIN'):
        """
        Actualiza un registro de diagnóstico existente
        Nota: No se permite cambiar la consulta ni el diagnóstico base
        """
        
        updateDiagnosticoSQL = """
            UPDATE registro_diagnosticos
            SET registro_tipo = %s,
                registro_gravedad = %s,
                registro_fecha = %s,
                des_registro_diagnostico = %s,
                registro_observaciones = %s,
                usuario_modificacion = %s,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_registro_diagnostico = %s
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            app.logger.info(f"Actualizando diagnóstico ID: {id_registro_diagnostico}")
            
            cur.execute(updateDiagnosticoSQL, (
                registro_tipo,
                registro_gravedad,
                registro_fecha,
                des_registro_diagnostico,
                registro_observaciones,
                usuario_modificacion,
                id_registro_diagnostico
            ))

            con.commit()
            app.logger.info(f"Diagnóstico {id_registro_diagnostico} actualizado exitosamente")
            return True

        except Exception as e:
            app.logger.error(f"Error al actualizar diagnóstico: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteRegistroDiagnostico(self, id_registro_diagnostico):
        """
        Elimina lógicamente un registro de diagnóstico (cambia est_registro_diagnostico a 'I')
        """
        deleteDiagnosticoSQL = """
            UPDATE registro_diagnosticos
            SET est_registro_diagnostico = 'I',
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_registro_diagnostico = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            app.logger.info(f"Eliminando (lógicamente) diagnóstico ID: {id_registro_diagnostico}")
            
            cur.execute(deleteDiagnosticoSQL, (id_registro_diagnostico,))
            
            if cur.rowcount == 0:
                app.logger.warning(f"No se encontró el diagnóstico con ID: {id_registro_diagnostico}")
                return False
            
            con.commit()
            app.logger.info(f"Diagnóstico {id_registro_diagnostico} eliminado exitosamente")
            return True

        except Exception as e:
            app.logger.error(f"Error al eliminar diagnóstico: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    def getDiagnosticosPorConsulta(self, id_consulta):
        """Obtiene todos los diagnósticos registrados en una consulta"""
        diagnosticoSQL = """
            SELECT
                rd.id_registro_diagnostico,
                d.des_diagnostico,
                d.diagnostico_codigo_cie10,
                rd.registro_tipo,
                rd.registro_gravedad,
                rd.registro_fecha,
                rd.des_registro_diagnostico
            FROM registro_diagnosticos rd
            JOIN diagnosticos d ON rd.id_diagnostico = d.id_diagnostico
            WHERE rd.id_consulta = %s AND rd.est_registro_diagnostico = 'A'
            ORDER BY rd.registro_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(diagnosticoSQL, (id_consulta,))
            diagnosticos = cur.fetchall()
            
            return [{
                'id_registro_diagnostico': d[0],
                'diagnostico': d[1],
                'codigo_cie10': d[2],
                'tipo': d[3],
                'gravedad': d[4],
                'fecha': d[5].strftime('%d/%m/%Y') if d[5] else None,
                'descripcion': d[6]
            } for d in diagnosticos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener diagnósticos de la consulta: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getDiagnosticosPorPaciente(self, id_paciente):
        """Obtiene todos los diagnósticos de un paciente (historial)"""
        diagnosticoSQL = """
            SELECT
                rd.id_registro_diagnostico,
                d.des_diagnostico,
                d.diagnostico_codigo_cie10,
                rd.registro_tipo,
                rd.registro_gravedad,
                rd.registro_fecha,
                c.consulta_fecha,
                CONCAT(pe.per_nombre, ' ', pe.per_apellido) AS profesional_nombre
            FROM registro_diagnosticos rd
            JOIN diagnosticos d ON rd.id_diagnostico = d.id_diagnostico
            JOIN consultas c ON rd.id_consulta = c.id_consulta
            JOIN especialistas e ON c.id_profesional = e.id_especialista
            JOIN funcionarios f ON e.id_funcionario = f.id_funcionario
            JOIN personas pe ON f.id_persona = pe.id_persona
            WHERE c.id_paciente = %s AND rd.est_registro_diagnostico = 'A'
            ORDER BY rd.registro_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(diagnosticoSQL, (id_paciente,))
            diagnosticos = cur.fetchall()
            
            return [{
                'id_registro_diagnostico': d[0],
                'diagnostico': d[1],
                'codigo_cie10': d[2],
                'tipo': d[3],
                'gravedad': d[4],
                'fecha_diagnostico': d[5].strftime('%d/%m/%Y') if d[5] else None,
                'fecha_consulta': d[6].strftime('%d/%m/%Y') if d[6] else None,
                'profesional': d[7]
            } for d in diagnosticos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener diagnósticos del paciente: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getDiagnosticosPorCodigo(self, codigo_cie10):
        """Obtiene registros de un diagnóstico específico por código CIE-10"""
        diagnosticoSQL = """
            SELECT
                rd.id_registro_diagnostico,
                rd.registro_fecha,
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                rd.registro_tipo,
                rd.registro_gravedad
            FROM registro_diagnosticos rd
            JOIN diagnosticos d ON rd.id_diagnostico = d.id_diagnostico
            JOIN consultas c ON rd.id_consulta = c.id_consulta
            JOIN pacientes p ON c.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            WHERE d.diagnostico_codigo_cie10 = %s AND rd.est_registro_diagnostico = 'A'
            ORDER BY rd.registro_fecha DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(diagnosticoSQL, (codigo_cie10,))
            diagnosticos = cur.fetchall()
            
            return [{
                'id_registro_diagnostico': d[0],
                'fecha': d[1].strftime('%d/%m/%Y') if d[1] else None,
                'historia_clinica': d[2],
                'paciente': d[3],
                'tipo': d[4],
                'gravedad': d[5]
            } for d in diagnosticos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener diagnósticos por código: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()