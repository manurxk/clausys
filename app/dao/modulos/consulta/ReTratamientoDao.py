from flask import current_app as app
from app.conexion.Conexion import Conexion
from datetime import datetime, date

class TratamientoDao:
    
    def getTratamientos(self):
        """Obtiene todos los tratamientos con sus datos completos"""
        tratamientoSQL = """
            SELECT
                t.id_tratamiento,
                t.id_paciente,
                t.id_diagnostico,
                t.des_tratamiento,
                t.tratamiento_tipo,
                t.tratamiento_fecha_inicio,
                t.tratamiento_fecha_fin,
                t.tratamiento_estado,
                t.tratamiento_objetivos,
                t.tratamiento_observaciones,
                -- Datos del paciente
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                pp.per_cedula AS paciente_cedula,
                pp.per_telefono AS paciente_telefono,
                -- Datos del diagnóstico (si existe)
                d.des_diagnostico,
                d.diagnostico_codigo_cie10,
                t.fecha_creacion
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            LEFT JOIN diagnosticos d ON t.id_diagnostico = d.id_diagnostico
            WHERE t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC, t.id_tratamiento DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(tratamientoSQL)
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'id_paciente': t[1],
                'id_diagnostico': t[2],
                'des_tratamiento': t[3],
                'tratamiento_tipo': t[4],
                'tratamiento_fecha_inicio': t[5].strftime('%d/%m/%Y') if t[5] else None,
                'tratamiento_fecha_fin': t[6].strftime('%d/%m/%Y') if t[6] else None,
                'tratamiento_estado': t[7],
                'tratamiento_objetivos': t[8],
                'tratamiento_observaciones': t[9],
                'historia_clinica': t[10],
                'paciente_nombre': t[11],
                'paciente_cedula': t[12],
                'paciente_telefono': t[13],
                'diagnostico': t[14],
                'codigo_cie10': t[15],
                'fecha_registro': t[16].strftime('%d/%m/%Y') if t[16] else None
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener todos los tratamientos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()

    def getTratamientoById(self, id_tratamiento):
        """Obtiene un tratamiento específico por ID con todos sus datos"""
        tratamientoSQL = """
            SELECT
                t.id_tratamiento,
                t.id_paciente,
                t.id_diagnostico,
                t.des_tratamiento,
                t.tratamiento_tipo,
                t.tratamiento_fecha_inicio,
                t.tratamiento_fecha_fin,
                t.tratamiento_estado,
                t.tratamiento_objetivos,
                t.tratamiento_observaciones,
                t.est_tratamiento,
                -- Datos del paciente
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                pp.per_cedula AS paciente_cedula,
                pp.per_telefono AS paciente_telefono,
                pp.per_fecha_nacimiento,
                DATE_PART('year', AGE(pp.per_fecha_nacimiento)) AS edad,
                -- Datos del diagnóstico
                d.des_diagnostico,
                d.diagnostico_codigo_cie10,
                t.fecha_creacion,
                t.usuario_creacion
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            LEFT JOIN diagnosticos d ON t.id_diagnostico = d.id_diagnostico
            WHERE t.id_tratamiento = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(tratamientoSQL, (id_tratamiento,))
            t = cur.fetchone()
            
            if not t:
                return None
            
            return {
                'id_tratamiento': t[0],
                'id_paciente': t[1],
                'id_diagnostico': t[2],
                'des_tratamiento': t[3],
                'tratamiento_tipo': t[4],
                'tratamiento_fecha_inicio': t[5].strftime('%d/%m/%Y') if t[5] else None,
                'tratamiento_fecha_fin': t[6].strftime('%d/%m/%Y') if t[6] else None,
                'tratamiento_estado': t[7],
                'tratamiento_objetivos': t[8],
                'tratamiento_observaciones': t[9],
                'activo': t[10] == 'A',
                'historia_clinica': t[11],
                'paciente_nombre': t[12],
                'paciente_cedula': t[13],
                'paciente_telefono': t[14],
                'paciente_fecha_nacimiento': t[15].strftime('%d/%m/%Y') if t[15] else None,
                'paciente_edad': int(t[16]) if t[16] else None,
                'diagnostico': t[17],
                'codigo_cie10': t[18],
                'fecha_registro': t[19].strftime('%d/%m/%Y') if t[19] else None,
                'usuario_creacion': t[20]
            }
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamiento por ID: {str(e)}")
            return None
        finally:
            cur.close()
            con.close()

    def getTratamientoParaEditar(self, id_tratamiento):
        """Obtiene un tratamiento con IDs originales para formulario de edición"""
        tratamientoSQL = """
            SELECT
                t.id_tratamiento,
                t.id_paciente,
                t.id_diagnostico,
                t.des_tratamiento,
                t.tratamiento_tipo,
                t.tratamiento_fecha_inicio,
                t.tratamiento_fecha_fin,
                t.tratamiento_estado,
                t.tratamiento_objetivos,
                t.tratamiento_observaciones,
                t.est_tratamiento,
                -- Descripciones
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                d.des_diagnostico,
                d.diagnostico_codigo_cie10
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            LEFT JOIN diagnosticos d ON t.id_diagnostico = d.id_diagnostico
            WHERE t.id_tratamiento = %s
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(tratamientoSQL, (id_tratamiento,))
            t = cur.fetchone()
            
            if not t:
                return None
            
            tratamiento = {
                'id_tratamiento': t[0],
                'id_paciente': t[1],
                'id_diagnostico': t[2],
                'des_tratamiento': t[3],
                'tratamiento_tipo': t[4],
                'tratamiento_fecha_inicio': t[5].strftime('%Y-%m-%d') if t[5] else None,
                'tratamiento_fecha_fin': t[6].strftime('%Y-%m-%d') if t[6] else None,
                'tratamiento_estado': t[7],
                'tratamiento_objetivos': t[8],
                'tratamiento_observaciones': t[9],
                'activo': t[10] == 'A',
                # Descripciones
                'historia_clinica': t[11],
                'paciente_nombre': t[12],
                'diagnostico': t[13],
                'codigo_cie10': t[14]
            }
            
            app.logger.info(f"Tratamiento cargado para editar: ID {tratamiento['id_tratamiento']}")
            
            return tratamiento
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamiento para editar: {str(e)}", exc_info=True)
            return None
        finally:
            cur.close()
            con.close()

    def guardarTratamiento(self, id_paciente, des_tratamiento, tratamiento_fecha_inicio,
                          tratamiento_tipo=None, id_diagnostico=None, tratamiento_fecha_fin=None,
                          tratamiento_estado='ACTIVO', tratamiento_objetivos=None,
                          tratamiento_observaciones=None, usuario_creacion='ADMIN'):
        """
        Guarda un nuevo tratamiento
        
        Args:
            id_paciente: ID del paciente (obligatorio)
            des_tratamiento: Descripción del tratamiento (obligatorio)
            tratamiento_fecha_inicio: Fecha de inicio (obligatorio)
            tratamiento_tipo: FARMACOLÓGICO, PSICOTERAPÉUTICO, MIXTO (opcional)
            id_diagnostico: ID del diagnóstico relacionado (opcional)
            tratamiento_fecha_fin: Fecha de finalización (opcional)
            tratamiento_estado: ACTIVO, FINALIZADO, SUSPENDIDO (default: ACTIVO)
            tratamiento_objetivos: Objetivos del tratamiento (opcional)
            tratamiento_observaciones: Observaciones adicionales (opcional)
            usuario_creacion: Usuario que crea el registro
        """
        
        # Validaciones básicas
        if not all([id_paciente, des_tratamiento, tratamiento_fecha_inicio]):
            app.logger.error("Faltan campos obligatorios para guardar tratamiento")
            return None
        
        insertTratamientoSQL = """
            INSERT INTO tratamientos(
                id_paciente, id_diagnostico, des_tratamiento, est_tratamiento,
                tratamiento_tipo, tratamiento_fecha_inicio, tratamiento_fecha_fin,
                tratamiento_estado, tratamiento_objetivos, tratamiento_observaciones,
                usuario_creacion
            )
            VALUES(%s, %s, %s, 'A', %s, %s, %s, %s, %s, %s, %s) 
            RETURNING id_tratamiento
        """

        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()

        try:
            app.logger.info(f"Insertando tratamiento para paciente ID: {id_paciente}")
            
            cur.execute(insertTratamientoSQL, (
                id_paciente,
                id_diagnostico,
                des_tratamiento,
                tratamiento_tipo,
                tratamiento_fecha_inicio,
                tratamiento_fecha_fin,
                tratamiento_estado,
                tratamiento_objetivos,
                tratamiento_observaciones,
                usuario_creacion
            ))
            
            tratamiento_id = cur.fetchone()[0]
            con.commit()
            
            app.logger.info(f"Tratamiento guardado exitosamente con ID: {tratamiento_id}")
            return tratamiento_id

        except Exception as e:
            con.rollback()
            app.logger.error(f"Error al insertar tratamiento: {str(e)}", exc_info=True)
            return None

        finally:
            cur.close()
            con.close()

    def updateTratamiento(self, id_tratamiento, des_tratamiento, tratamiento_tipo,
                         tratamiento_fecha_inicio, tratamiento_fecha_fin, tratamiento_estado,
                         tratamiento_objetivos=None, tratamiento_observaciones=None,
                         usuario_modificacion='ADMIN'):
        """
        Actualiza un tratamiento existente
        Nota: No se permite cambiar el paciente ni el diagnóstico base
        """
        
        updateTratamientoSQL = """
            UPDATE tratamientos
            SET des_tratamiento = %s,
                tratamiento_tipo = %s,
                tratamiento_fecha_inicio = %s,
                tratamiento_fecha_fin = %s,
                tratamiento_estado = %s,
                tratamiento_objetivos = %s,
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
            
            cur.execute(updateTratamientoSQL, (
                des_tratamiento,
                tratamiento_tipo,
                tratamiento_fecha_inicio,
                tratamiento_fecha_fin,
                tratamiento_estado,
                tratamiento_objetivos,
                tratamiento_observaciones,
                usuario_modificacion,
                id_tratamiento
            ))

            con.commit()
            app.logger.info(f"Tratamiento {id_tratamiento} actualizado exitosamente")
            return True

        except Exception as e:
            app.logger.error(f"Error al actualizar tratamiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    def deleteTratamiento(self, id_tratamiento):
        """
        Elimina lógicamente un tratamiento (cambia est_tratamiento a 'I')
        """
        deleteTratamientoSQL = """
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
            
            cur.execute(deleteTratamientoSQL, (id_tratamiento,))
            
            if cur.rowcount == 0:
                app.logger.warning(f"No se encontró el tratamiento con ID: {id_tratamiento}")
                return False
            
            con.commit()
            app.logger.info(f"Tratamiento {id_tratamiento} eliminado exitosamente")
            return True

        except Exception as e:
            app.logger.error(f"Error al eliminar tratamiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()

    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    def getTratamientosPorPaciente(self, id_paciente):
        """Obtiene todos los tratamientos de un paciente específico"""
        tratamientoSQL = """
            SELECT
                t.id_tratamiento,
                t.des_tratamiento,
                t.tratamiento_tipo,
                t.tratamiento_fecha_inicio,
                t.tratamiento_fecha_fin,
                t.tratamiento_estado,
                d.des_diagnostico,
                d.diagnostico_codigo_cie10
            FROM tratamientos t
            LEFT JOIN diagnosticos d ON t.id_diagnostico = d.id_diagnostico
            WHERE t.id_paciente = %s AND t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(tratamientoSQL, (id_paciente,))
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'descripcion': t[1],
                'tipo': t[2],
                'fecha_inicio': t[3].strftime('%d/%m/%Y') if t[3] else None,
                'fecha_fin': t[4].strftime('%d/%m/%Y') if t[4] else None,
                'estado': t[5],
                'diagnostico': t[6],
                'codigo_cie10': t[7]
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos del paciente: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getTratamientosActivos(self):
        """Obtiene todos los tratamientos activos"""
        tratamientoSQL = """
            SELECT
                t.id_tratamiento,
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                t.des_tratamiento,
                t.tratamiento_tipo,
                t.tratamiento_fecha_inicio,
                d.des_diagnostico
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            LEFT JOIN diagnosticos d ON t.id_diagnostico = d.id_diagnostico
            WHERE t.tratamiento_estado = 'ACTIVO' AND t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(tratamientoSQL)
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'historia_clinica': t[1],
                'paciente': t[2],
                'descripcion': t[3],
                'tipo': t[4],
                'fecha_inicio': t[5].strftime('%d/%m/%Y') if t[5] else None,
                'diagnostico': t[6]
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos activos: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getTratamientosPorEstado(self, estado):
        """Obtiene tratamientos filtrados por estado"""
        tratamientoSQL = """
            SELECT
                t.id_tratamiento,
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                t.des_tratamiento,
                t.tratamiento_tipo,
                t.tratamiento_fecha_inicio,
                t.tratamiento_fecha_fin
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            WHERE t.tratamiento_estado = %s AND t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(tratamientoSQL, (estado,))
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'historia_clinica': t[1],
                'paciente': t[2],
                'descripcion': t[3],
                'tipo': t[4],
                'fecha_inicio': t[5].strftime('%d/%m/%Y') if t[5] else None,
                'fecha_fin': t[6].strftime('%d/%m/%Y') if t[6] else None
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos por estado: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getTratamientosPorDiagnostico(self, id_diagnostico):
        """Obtiene todos los tratamientos asociados a un diagnóstico específico"""
        tratamientoSQL = """
            SELECT
                t.id_tratamiento,
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                t.des_tratamiento,
                t.tratamiento_tipo,
                t.tratamiento_fecha_inicio,
                t.tratamiento_estado
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            WHERE t.id_diagnostico = %s AND t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(tratamientoSQL, (id_diagnostico,))
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'historia_clinica': t[1],
                'paciente': t[2],
                'descripcion': t[3],
                'tipo': t[4],
                'fecha_inicio': t[5].strftime('%d/%m/%Y') if t[5] else None,
                'estado': t[6]
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos por diagnóstico: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def getTratamientosPorTipo(self, tipo):
        """Obtiene tratamientos filtrados por tipo"""
        tratamientoSQL = """
            SELECT
                t.id_tratamiento,
                p.pac_historia_clinica,
                CONCAT(pp.per_nombre, ' ', pp.per_apellido) AS paciente_nombre,
                t.des_tratamiento,
                t.tratamiento_fecha_inicio,
                t.tratamiento_estado,
                d.des_diagnostico
            FROM tratamientos t
            JOIN pacientes p ON t.id_paciente = p.id_paciente
            JOIN personas pp ON p.id_persona = pp.id_persona
            LEFT JOIN diagnosticos d ON t.id_diagnostico = d.id_diagnostico
            WHERE t.tratamiento_tipo = %s AND t.est_tratamiento = 'A'
            ORDER BY t.tratamiento_fecha_inicio DESC
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(tratamientoSQL, (tipo,))
            tratamientos = cur.fetchall()
            
            return [{
                'id_tratamiento': t[0],
                'historia_clinica': t[1],
                'paciente': t[2],
                'descripcion': t[3],
                'fecha_inicio': t[4].strftime('%d/%m/%Y') if t[4] else None,
                'estado': t[5],
                'diagnostico': t[6]
            } for t in tratamientos]
            
        except Exception as e:
            app.logger.error(f"Error al obtener tratamientos por tipo: {str(e)}")
            return []
        finally:
            cur.close()
            con.close()
    
    def finalizarTratamiento(self, id_tratamiento, fecha_fin=None, observaciones=None):
        """
        Finaliza un tratamiento activo
        """
        if not fecha_fin:
            fecha_fin = date.today()
        
        finalizarSQL = """
            UPDATE tratamientos
            SET tratamiento_estado = 'FINALIZADO',
                tratamiento_fecha_fin = %s,
                tratamiento_observaciones = COALESCE(%s, tratamiento_observaciones),
                fecha_modificacion = CURRENT_TIMESTAMP
            WHERE id_tratamiento = %s AND tratamiento_estado = 'ACTIVO'
        """
        
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        
        try:
            cur.execute(finalizarSQL, (fecha_fin, observaciones, id_tratamiento))
            
            if cur.rowcount == 0:
                app.logger.warning(f"No se pudo finalizar el tratamiento ID: {id_tratamiento}")
                return False
            
            con.commit()
            app.logger.info(f"Tratamiento {id_tratamiento} finalizado exitosamente")
            return True
            
        except Exception as e:
            app.logger.error(f"Error al finalizar tratamiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
    
    def suspenderTratamiento(self, id_tratamiento, observaciones=None):
        """
        Suspende un tratamiento activo
        """
        suspenderSQL = """
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
            cur.execute(suspenderSQL, (observaciones, id_tratamiento))
            
            if cur.rowcount == 0:
                app.logger.warning(f"No se pudo suspender el tratamiento ID: {id_tratamiento}")
                return False
            
            con.commit()
            app.logger.info(f"Tratamiento {id_tratamiento} suspendido exitosamente")
            return True
            
        except Exception as e:
            app.logger.error(f"Error al suspender tratamiento: {str(e)}")
            con.rollback()
            return False
        finally:
            cur.close()
            con.close()
            