from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime, date

class TratamientoDao:
    """DAO para gestionar tratamientos psicológicos"""
    
    def getTratamientos(self):
        """Obtiene todos los tratamientos activos"""
        query = """
            SELECT
                t.id_tratamiento,
                t.id_consulta,
                t.id_paciente,
                t.id_registro_diagnostico,
                t.id_tipo_tratamiento,
                t.des_tratamiento,
                t.tratamiento_objetivos,
                t.numero_sesiones,
                t.frecuencia_sesiones,
                t.duracion_sesion,
                t.tratamiento_fecha_inicio,
                t.tratamiento_fecha_fin,
                t.tratamiento_estado,
                t.tratamiento_observaciones,
                -- Datos paciente
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                -- Datos consulta
                c.consulta_fecha,
                -- Datos diagnóstico
                d.codigo_cie10,
                diag.des_diagnostico,
                -- Datos tipo tratamiento
                tt.des_tipo_tratamiento,
                t.fecha_creacion
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            LEFT JOIN consultas c ON t.id_consulta = c.id_consulta
            LEFT JOIN registro_diagnosticos rd ON t.id_registro_diagnostico = rd.id_registro_diagnostico
            LEFT JOIN diagnosticos d ON rd.id_diagnostico = d.id_diagnostico
            LEFT JOIN diagnosticos diag ON d.id_diagnostico = diag.id_diagnostico
            LEFT JOIN tipos_tratamientos tt ON t.id_tipo_tratamiento = tt.id_tipo_tratamiento
            WHERE t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC, t.id_tratamiento DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query)
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'id_consulta': t[1],
                'id_paciente': t[2],
                'id_registro_diagnostico': t[3],
                'id_tipo_tratamiento': t[4],
                'des_tratamiento': t[5],
                'tratamiento_objetivos': t[6],
                'numero_sesiones': t[7],
                'frecuencia_sesiones': t[8],
                'duracion_sesion': t[9],
                'tratamiento_fecha_inicio': t[10].strftime('%Y-%m-%d') if t[10] else None,
                'tratamiento_fecha_fin': t[11].strftime('%Y-%m-%d') if t[11] else None,
                'tratamiento_estado': t[12],
                'tratamiento_observaciones': t[13],
                'historia_clinica': t[14],
                'paciente_nombre': t[15],
                'consulta_fecha': t[16].strftime('%d/%m/%Y %H:%M') if t[16] else None,
                'codigo_cie10': t[17],
                'diagnostico': t[18],
                'tipo_tratamiento': t[19],
                'fecha_creacion': t[20].strftime('%d/%m/%Y') if t[20] else None
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTratamientoById(self, id_tratamiento):
        """Obtiene un tratamiento específico por ID"""
        query = """
            SELECT
                t.id_tratamiento,
                t.id_consulta,
                t.id_paciente,
                t.id_registro_diagnostico,
                t.id_tipo_tratamiento,
                t.des_tratamiento,
                t.tratamiento_objetivos,
                t.numero_sesiones,
                t.frecuencia_sesiones,
                t.duracion_sesion,
                t.tratamiento_fecha_inicio,
                t.tratamiento_fecha_fin,
                t.tratamiento_estado,
                t.tratamiento_observaciones,
                t.est_tratamiento,
                -- Datos completos
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                c.consulta_fecha,
                diag.codigo_cie10,
                diag.des_diagnostico,
                tt.des_tipo_tratamiento,
                t.usuario_creacion,
                t.fecha_creacion
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            LEFT JOIN consultas c ON t.id_consulta = c.id_consulta
            LEFT JOIN registro_diagnosticos rd ON t.id_registro_diagnostico = rd.id_registro_diagnostico
            LEFT JOIN diagnosticos diag ON rd.id_diagnostico = diag.id_diagnostico
            LEFT JOIN tipos_tratamientos tt ON t.id_tipo_tratamiento = tt.id_tipo_tratamiento
            WHERE t.id_tratamiento = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query, (id_tratamiento,))
            t = cur.fetchone()
            
            if not t:
                return None
            
            return {
                'id_tratamiento': t[0],
                'id_consulta': t[1],
                'id_paciente': t[2],
                'id_registro_diagnostico': t[3],
                'id_tipo_tratamiento': t[4],
                'des_tratamiento': t[5],
                'tratamiento_objetivos': t[6],
                'numero_sesiones': t[7],
                'frecuencia_sesiones': t[8],
                'duracion_sesion': t[9],
                'tratamiento_fecha_inicio': t[10].strftime('%Y-%m-%d') if t[10] else None,
                'tratamiento_fecha_fin': t[11].strftime('%Y-%m-%d') if t[11] else None,
                'tratamiento_estado': t[12],
                'tratamiento_observaciones': t[13],
                'activo': t[14] == 'A',
                'historia_clinica': t[15],
                'paciente_nombre': t[16],
                'consulta_fecha': t[17].strftime('%d/%m/%Y %H:%M') if t[17] else None,
                'codigo_cie10': t[18],
                'diagnostico': t[19],
                'tipo_tratamiento': t[20],
                'usuario_creacion': t[21],
                'fecha_creacion': t[22].strftime('%d/%m/%Y') if t[22] else None
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamiento por ID: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def getTratamientoParaEditar(self, id_tratamiento):
        """Obtiene tratamiento con IDs originales para formulario de edición"""
        query = """
            SELECT
                t.id_tratamiento,
                t.id_consulta,
                t.id_paciente,
                t.id_registro_diagnostico,
                t.id_tipo_tratamiento,
                t.des_tratamiento,
                t.tratamiento_objetivos,
                t.numero_sesiones,
                t.frecuencia_sesiones,
                t.duracion_sesion,
                t.tratamiento_fecha_inicio,
                t.tratamiento_fecha_fin,
                t.tratamiento_estado,
                t.tratamiento_observaciones,
                -- Datos para mostrar
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                diag.des_diagnostico,
                tt.des_tipo_tratamiento
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            LEFT JOIN registro_diagnosticos rd ON t.id_registro_diagnostico = rd.id_registro_diagnostico
            LEFT JOIN diagnosticos diag ON rd.id_diagnostico = diag.id_diagnostico
            LEFT JOIN tipos_tratamientos tt ON t.id_tipo_tratamiento = tt.id_tipo_tratamiento
            WHERE t.id_tratamiento = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query, (id_tratamiento,))
            t = cur.fetchone()
            
            if not t:
                return None
            
            return {
                'id_tratamiento': t[0],
                'id_consulta': t[1],
                'id_paciente': t[2],
                'id_registro_diagnostico': t[3],
                'id_tipo_tratamiento': t[4],
                'des_tratamiento': t[5],
                'tratamiento_objetivos': t[6],
                'numero_sesiones': t[7],
                'frecuencia_sesiones': t[8],
                'duracion_sesion': t[9],
                'tratamiento_fecha_inicio': t[10].strftime('%Y-%m-%d') if t[10] else None,
                'tratamiento_fecha_fin': t[11].strftime('%Y-%m-%d') if t[11] else None,
                'tratamiento_estado': t[12],
                'tratamiento_observaciones': t[13],
                'paciente_nombre': t[14],
                'diagnostico': t[15],
                'tipo_tratamiento': t[16]
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamiento para editar: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def guardarTratamiento(self, id_consulta, id_paciente, id_registro_diagnostico, 
                          id_tipo_tratamiento, des_tratamiento, tratamiento_fecha_inicio,
                          tratamiento_objetivos=None, numero_sesiones=None, 
                          frecuencia_sesiones=None, duracion_sesion=None, 
                          tratamiento_fecha_fin=None, tratamiento_estado='ACTIVO',
                          tratamiento_observaciones=None, usuario_creacion='ADMIN'):
        """Guarda un nuevo tratamiento"""
        
        if not all([id_consulta, id_paciente, id_registro_diagnostico, id_tipo_tratamiento, 
                   des_tratamiento, tratamiento_fecha_inicio]):
            app.logger.error("Faltan campos obligatorios para guardar tratamiento")
            return None
        
        query = """
            INSERT INTO tratamientos(
                id_consulta, id_paciente, id_registro_diagnostico, id_tipo_tratamiento,
                des_tratamiento, tratamiento_objetivos, numero_sesiones, 
                frecuencia_sesiones, duracion_sesion, tratamiento_fecha_inicio, 
                tratamiento_fecha_fin, tratamiento_estado, tratamiento_observaciones,
                usuario_creacion, est_tratamiento
            )
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'A')
            RETURNING id_tratamiento
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            app.logger.info(f"Guardando tratamiento para paciente ID: {id_paciente}")
            
            cur.execute(query, (
                id_consulta, id_paciente, id_registro_diagnostico, id_tipo_tratamiento,
                des_tratamiento, tratamiento_objetivos, numero_sesiones,
                frecuencia_sesiones, duracion_sesion, tratamiento_fecha_inicio,
                tratamiento_fecha_fin, tratamiento_estado, tratamiento_observaciones,
                usuario_creacion
            ))
            
            tratamiento_id = cur.fetchone()[0]
            con.commit()
            
            app.logger.info(f"Tratamiento guardado exitosamente con ID: {tratamiento_id}")
            return tratamiento_id
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al guardar tratamiento: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def updateTratamiento(self, id_tratamiento, id_tipo_tratamiento, des_tratamiento,
                         tratamiento_fecha_inicio, tratamiento_estado, 
                         tratamiento_objetivos=None, numero_sesiones=None,
                         frecuencia_sesiones=None, duracion_sesion=None,
                         tratamiento_fecha_fin=None, tratamiento_observaciones=None,
                         usuario_modificacion='ADMIN'):
        """Actualiza un tratamiento existente"""
        
        query = """
            UPDATE tratamientos
            SET id_tipo_tratamiento = %s,
                des_tratamiento = %s,
                tratamiento_objetivos = %s,
                numero_sesiones = %s,
                frecuencia_sesiones = %s,
                duracion_sesion = %s,
                tratamiento_fecha_inicio = %s,
                tratamiento_fecha_fin = %s,
                tratamiento_estado = %s,
                tratamiento_observaciones = %s,
                usuario_modificacion = %s,
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_tratamiento = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            app.logger.info(f"Actualizando tratamiento ID: {id_tratamiento}")
            
            cur.execute(query, (
                id_tipo_tratamiento, des_tratamiento, tratamiento_objetivos,
                numero_sesiones, frecuencia_sesiones, duracion_sesion,
                tratamiento_fecha_inicio, tratamiento_fecha_fin, tratamiento_estado,
                tratamiento_observaciones, usuario_modificacion, id_tratamiento
            ))
            
            con.commit()
            app.logger.info(f"Tratamiento {id_tratamiento} actualizado exitosamente")
            return True
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al actualizar tratamiento: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def deleteTratamiento(self, id_tratamiento):
        """Elimina lógicamente un tratamiento (cambia est_tratamiento a 'I')"""
        query = """
            UPDATE tratamientos
            SET est_tratamiento = 'I',
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_tratamiento = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            app.logger.info(f"Eliminando (lógicamente) tratamiento ID: {id_tratamiento}")
            
            cur.execute(query, (id_tratamiento,))
            
            if cur.rowcount == 0:
                app.logger.warning(f"No se encontró el tratamiento con ID: {id_tratamiento}")
                return False
            
            con.commit()
            app.logger.info(f"Tratamiento {id_tratamiento} eliminado exitosamente")
            return True
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al eliminar tratamiento: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    # ==========================================
    # MÉTODOS DE ESTADO DEL TRATAMIENTO
    # ==========================================
    
    def finalizarTratamiento(self, id_tratamiento, fecha_fin=None, observaciones=None):
        """Finaliza un tratamiento activo"""
        query = """
            UPDATE tratamientos
            SET tratamiento_estado = 'FINALIZADO',
                tratamiento_fecha_fin = COALESCE(%s, CURRENT_DATE),
                tratamiento_observaciones = COALESCE(%s, tratamiento_observaciones),
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_tratamiento = %s AND tratamiento_estado = 'ACTIVO'
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query, (fecha_fin, observaciones, id_tratamiento))
            con.commit()
            
            return cur.rowcount > 0
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al finalizar tratamiento: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def suspenderTratamiento(self, id_tratamiento, observaciones=None):
        """Suspende un tratamiento activo"""
        query = """
            UPDATE tratamientos
            SET tratamiento_estado = 'SUSPENDIDO',
                tratamiento_observaciones = COALESCE(%s, tratamiento_observaciones),
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_tratamiento = %s AND tratamiento_estado = 'ACTIVO'
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query, (observaciones, id_tratamiento))
            con.commit()
            
            return cur.rowcount > 0
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al suspender tratamiento: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    def reactivarTratamiento(self, id_tratamiento, observaciones=None):
        """Reactiva un tratamiento suspendido"""
        query = """
            UPDATE tratamientos
            SET tratamiento_estado = 'ACTIVO',
                tratamiento_observaciones = COALESCE(%s, tratamiento_observaciones),
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_tratamiento = %s AND tratamiento_estado IN ('SUSPENDIDO', 'EN_PAUSA')
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query, (observaciones, id_tratamiento))
            con.commit()
            
            return cur.rowcount > 0
            
        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al reactivar tratamiento: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    # ==========================================
    # MÉTODOS DE FILTRADO
    # ==========================================
    
    def getTratamientosPorPaciente(self, id_paciente):
        """Obtiene todos los tratamientos de un paciente"""
        query = """
            SELECT
                t.id_tratamiento, t.des_tratamiento, t.tratamiento_estado,
                t.tratamiento_fecha_inicio, t.tratamiento_fecha_fin,
                tt.des_tipo_tratamiento, d.codigo_cie10
            FROM tratamientos t
            LEFT JOIN tipos_tratamientos tt ON t.id_tipo_tratamiento = tt.id_tipo_tratamiento
            LEFT JOIN registro_diagnosticos rd ON t.id_registro_diagnostico = rd.id_registro_diagnostico
            LEFT JOIN diagnosticos d ON rd.id_diagnostico = d.id_diagnostico
            WHERE t.id_paciente = %s AND t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query, (id_paciente,))
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'des_tratamiento': t[1],
                'tratamiento_estado': t[2],
                'fecha_inicio': t[3].strftime('%Y-%m-%d') if t[3] else None,
                'fecha_fin': t[4].strftime('%Y-%m-%d') if t[4] else None,
                'tipo_tratamiento': t[5],
                'codigo_cie10': t[6]
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos del paciente: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTratamientosPorConsulta(self, id_consulta):
        """Obtiene todos los tratamientos de una consulta"""
        query = """
            SELECT
                t.id_tratamiento, t.des_tratamiento, t.tratamiento_estado,
                t.tratamiento_fecha_inicio, tt.des_tipo_tratamiento
            FROM tratamientos t
            LEFT JOIN tipos_tratamientos tt ON t.id_tipo_tratamiento = tt.id_tipo_tratamiento
            WHERE t.id_consulta = %s AND t.est_tratamiento = 'A'
            ORDER BY t.id_tratamiento DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query, (id_consulta,))
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'des_tratamiento': t[1],
                'tratamiento_estado': t[2],
                'fecha_inicio': t[3].strftime('%Y-%m-%d') if t[3] else None,
                'tipo_tratamiento': t[4]
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos de la consulta: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTratamientosPorEstado(self, estado):
        """Obtiene tratamientos filtrados por estado"""
        query = """
            SELECT
                t.id_tratamiento, t.des_tratamiento, t.tratamiento_estado,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                p.pac_historia_clinica, t.tratamiento_fecha_inicio, 
                tt.des_tipo_tratamiento
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            LEFT JOIN tipos_tratamientos tt ON t.id_tipo_tratamiento = tt.id_tipo_tratamiento
            WHERE t.tratamiento_estado = %s AND t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query, (estado,))
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'des_tratamiento': t[1],
                'tratamiento_estado': t[2],
                'paciente_nombre': t[3],
                'historia_clinica': t[4],
                'fecha_inicio': t[5].strftime('%Y-%m-%d') if t[5] else None,
                'tipo_tratamiento': t[6]
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos por estado: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTratamientosPorDiagnostico(self, id_registro_diagnostico):
        """Obtiene tratamientos para un diagnóstico específico"""
        query = """
            SELECT
                t.id_tratamiento, t.des_tratamiento, t.tratamiento_estado,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                t.tratamiento_fecha_inicio
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            WHERE t.id_registro_diagnostico = %s AND t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query, (id_registro_diagnostico,))
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'des_tratamiento': t[1],
                'tratamiento_estado': t[2],
                'paciente_nombre': t[3],
                'fecha_inicio': t[4].strftime('%Y-%m-%d') if t[4] else None
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos por diagnóstico: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTratamientosPorTipo(self, id_tipo_tratamiento):
        """Obtiene tratamientos filtrados por tipo"""
        query = """
            SELECT
                t.id_tratamiento, t.des_tratamiento, t.tratamiento_estado,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                t.numero_sesiones, t.frecuencia_sesiones
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            WHERE t.id_tipo_tratamiento = %s AND t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query, (id_tipo_tratamiento,))
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'des_tratamiento': t[1],
                'tratamiento_estado': t[2],
                'paciente_nombre': t[3],
                'numero_sesiones': t[4],
                'frecuencia_sesiones': t[5]
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos por tipo: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTratamientosActivos(self):
        """Obtiene todos los tratamientos activos del sistema"""
        query = """
            SELECT
                t.id_tratamiento, t.des_tratamiento, 
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                p.pac_historia_clinica, t.tratamiento_fecha_inicio,
                t.numero_sesiones, t.frecuencia_sesiones,
                tt.des_tipo_tratamiento
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            LEFT JOIN tipos_tratamientos tt ON t.id_tipo_tratamiento = tt.id_tipo_tratamiento
            WHERE t.tratamiento_estado = 'ACTIVO' AND t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(query)
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'des_tratamiento': t[1],
                'paciente_nombre': t[2],
                'historia_clinica': t[3],
                'fecha_inicio': t[4].strftime('%Y-%m-%d') if t[4] else None,
                'numero_sesiones': t[5],
                'frecuencia_sesiones': t[6],
                'tipo_tratamiento': t[7]
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos activos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()