from flask import Blueprint, request, jsonify, current_app as app
from app.dao.gestionar_personas.paciente.PacienteDao import PacienteDao
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from openpyxl import Workbook
import io


pacienteapi = Blueprint('pacienteapi', __name__)


# ============================================
# GENERAR PDF DE PACIENTE
# ============================================
@pacienteapi.route('/pacientes/<int:pac_id>/pdf', methods=['GET'])
def generarPDF(pac_id):
    pacientedao = PacienteDao()
    
    try:
        paciente = pacientedao.getPacienteById(pac_id)
        
        if not paciente:
            return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
        
        # Crear PDF en memoria
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Título
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "Ficha de Paciente")
        
        # Datos del paciente
        p.setFont("Helvetica", 12)
        y = height - 100
        
        datos = [
            f"Historia Clínica: {paciente.get('historia_clinica', 'N/A')}",
            f"Nombre: {paciente.get('nombre', '')} {paciente.get('apellido', '')}",
            f"Cédula: {paciente.get('cedula', 'N/A')}",
            f"Fecha Nacimiento: {paciente.get('fecha_nacimiento', 'N/A')}",
            f"Edad: {paciente.get('edad', 'N/A')} años",
            f"Género: {paciente.get('genero', 'N/A')}",
            f"Estado Civil: {paciente.get('estado_civil', 'N/A')}",
            f"Teléfono: {paciente.get('telefono', 'N/A')}",
            f"Correo: {paciente.get('correo', 'N/A')}",
            f"Domicilio: {paciente.get('domicilio', 'N/A')}",
            f"Ciudad: {paciente.get('ciudad', 'N/A')}",
            f"Nivel Instrucción: {paciente.get('nivel_instruccion', 'N/A')}",
            f"Profesión: {paciente.get('profesion', 'N/A')}",
        ]
        
        for dato in datos:
            p.drawString(50, y, dato)
            y -= 20
        
        if paciente.get('es_menor') and (paciente.get('nom_madre') or paciente.get('nom_padre')):
            y -= 20
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "Datos del Tutor:")
            y -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, y, f"Madre: {paciente.get('nom_madre', 'N/A')} - Tel: {paciente.get('tel_madre', 'N/A')}")
            y -= 20
            p.drawString(50, y, f"Padre: {paciente.get('nom_padre', 'N/A')} - Tel: {paciente.get('tel_padre', 'N/A')}")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"paciente_{pac_id}.pdf", mimetype='application/pdf')
        
    except Exception as e:
        app.logger.error(f"Error al generar PDF: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al generar PDF'}), 500


# ============================================
# GENERAR EXCEL DE PACIENTE
# ============================================
@pacienteapi.route('/pacientes/<int:pac_id>/excel', methods=['GET'])
def generarExcel(pac_id):
    pacientedao = PacienteDao()
    
    try:
        paciente = pacientedao.getPacienteById(pac_id)
        
        if not paciente:
            return jsonify({'success': False, 'error': 'Paciente no encontrado'}), 404
        
        # Crear Excel en memoria
        wb = Workbook()
        ws = wb.active
        ws.title = "Datos del Paciente"
        
        # Encabezados
        ws['A1'] = "Campo"
        ws['B1'] = "Valor"
        
        # Datos
        datos = [
            ["Historia Clínica", paciente.get('historia_clinica', 'N/A')],
            ["Nombre", paciente.get('nombre', '')],
            ["Apellido", paciente.get('apellido', '')],
            ["Cédula", paciente.get('cedula', 'N/A')],
            ["Fecha Nacimiento", paciente.get('fecha_nacimiento', 'N/A')],
            ["Edad", f"{paciente.get('edad', 'N/A')} años"],
            ["Género", paciente.get('genero', 'N/A')],
            ["Estado Civil", paciente.get('estado_civil', 'N/A')],
            ["Teléfono", paciente.get('telefono', 'N/A')],
            ["Correo", paciente.get('correo', 'N/A')],
            ["Domicilio", paciente.get('domicilio', 'N/A')],
            ["Ciudad", paciente.get('ciudad', 'N/A')],
            ["Nivel Instrucción", paciente.get('nivel_instruccion', 'N/A')],
            ["Profesión", paciente.get('profesion', 'N/A')],
        ]
        
        for idx, (campo, valor) in enumerate(datos, start=2):
            ws[f'A{idx}'] = campo
            ws[f'B{idx}'] = valor
        
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        return send_file(buffer, as_attachment=True, download_name=f"paciente_{pac_id}.xlsx", 
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
    except Exception as e:
        app.logger.error(f"Error al generar Excel: {str(e)}")
        return jsonify({'success': False, 'error': 'Error al generar Excel'}), 500



# ============================================
# OBTENER TODOS LOS PACIENTES
# ============================================
@pacienteapi.route('/pacientes', methods=['GET'])
def getPacientes():
    """Obtiene la lista completa de pacientes"""
    pacientedao = PacienteDao()
    
    try:
        pacientes = pacientedao.getPacientes()
        
        return jsonify({
            'success': True,
            'data': pacientes,
            'error': None
        }), 200
    
    except Exception as e:
        app.logger.error(f"Error al obtener todos los pacientes: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ============================================
# OBTENER PACIENTE POR ID
# ============================================
@pacienteapi.route('/pacientes/<int:pac_id>', methods=['GET'])
def getPaciente(pac_id):
    """Obtiene un paciente específico por su ID"""
    pacientedao = PacienteDao()
    
    try:
        paciente = pacientedao.getPacienteById(pac_id)
        
        if paciente:
            return jsonify({
                'success': True,
                'data': paciente,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el paciente con el ID proporcionado.'
            }), 404
    
    except Exception as e:
        app.logger.error(f"Error al obtener el paciente: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ============================================
# CREAR NUEVO PACIENTE
# ============================================
@pacienteapi.route('/pacientes', methods=['POST'])
def addPaciente():
    """Crea un nuevo paciente con todos sus datos"""
    data = request.get_json()
    pacientedao = PacienteDao()

    # Campos obligatorios REALES
    campos_requeridos = [
        'nombre', 'apellido', 'cedula', 'telefono'
    ]

    # Validar campos obligatorios
    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    # Validar que si es_menor = true, tenga datos de tutores
    es_menor = data.get('es_menor', False)
    if es_menor and not (data.get('nom_madre') or data.get('nom_padre')):
        return jsonify({
            'success': False,
            'error': 'Si el paciente es menor, debe proporcionar al menos el nombre de la madre o el padre.'
        }), 400

    try:
        paciente_id = pacientedao.guardarPaciente(
            # Datos de persona (obligatorios)
            nombre=data['nombre'],
            apellido=data['apellido'],
            cedula=data['cedula'],
            telefono=data['telefono'],
            fecha_nacimiento=data['fecha_nacimiento'],
            
            # Datos de persona (opcionales)
            id_genero=data.get('id_genero'),  # <-- Cambiado
            estado_civil_id=data.get('id_estado_civil'),  # <-- Cambiado
            correo=data.get('correo'),
            domicilio=data.get('domicilio'),
            id_ciudad=data.get('id_ciudad'),  # <-- Cambiado
            ciudad_nacimiento_id=data.get('id_ciudad_nacimiento'),  # <-- Cambiado
            nivel_instruccion_id=data.get('id_nivel_instruccion'),  # <-- Cambiado
            profesion_ocupacion_id=data.get('id_profesion'),  # <-- Cambiado
            
            # Datos de paciente
            historia_clinica=data.get('historia_clinica'),  # <-- AHORA OPCIONAL
            es_menor=es_menor,
            observaciones=data.get('observaciones'),
            
            # Datos del menor
            nom_madre=data.get('nom_madre'),
            tel_madre=data.get('tel_madre'),
            nom_padre=data.get('nom_padre'),
            tel_padre=data.get('tel_padre'),
            educacion=data.get('educacion'),
            colegio=data.get('colegio'),
            tel_colegio=data.get('tel_colegio')
        )

        if paciente_id is not None:
            return jsonify({
                'success': True,
                'data': {
                    'id_paciente': paciente_id,  # <-- Cambiado
                    'mensaje': 'Paciente creado exitosamente'
                },
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar el paciente. Consulte con el administrador.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al agregar paciente: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Ocurrió un error interno: {str(e)}'
        }), 500
    

@pacienteapi.route('/pacientes/<int:pac_id>/editar', methods=['GET'])
def getPacienteParaEditar(pac_id):
    pacientedao = PacienteDao()

    try:
        paciente = pacientedao.getPacienteParaEditar(pac_id)

        if paciente:
            return jsonify({
                'success': True,
                'data': paciente,
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el paciente.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al obtener paciente para editar: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno.'
        }), 500
# ============================================
# ACTUALIZAR PACIENTE EXISTENTE
# ============================================
@pacienteapi.route('/pacientes/<int:pac_id>', methods=['PUT'])
def updatePaciente(pac_id):
    """Actualiza un paciente existente con todos sus datos"""
    data = request.get_json()
    pacientedao = PacienteDao()
    app.logger.info(f"Datos recibidos para actualizar: {data}")

    # Verificar que el paciente existe
    paciente_existente = pacientedao.getPacienteById(pac_id)
    if not paciente_existente:
        return jsonify({
            'success': False,
            'error': 'No se encontró el paciente con el ID proporcionado.'
        }), 404

    # Campos obligatorios
    campos_requeridos = [
        'nombre', 'apellido', 'cedula', 'cedula'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({
                'success': False,
                'error': f'El campo {campo} es obligatorio y no puede estar vacío.'
            }), 400

    try:
        resultado = pacientedao.updatePaciente(
            pac_id=pac_id,
            
            # Datos de persona
            nombre=data['nombre'],
            apellido=data['apellido'],
            cedula=data['cedula'],
            fecha_nacimiento=data['fecha_nacimiento'],
            id_genero=data.get('id_genero'),
            estado_civil_id=data.get('estado_civil_id'),
            telefono=data.get('telefono'),
            correo=data.get('correo'),
            domicilio=data.get('domicilio'),
            id_ciudad=data.get('id_ciudad'),
            ciudad_nacimiento_id=data.get('ciudad_nacimiento_id'),
            nivel_instruccion_id=data.get('nivel_instruccion_id'),
            profesion_ocupacion_id=data.get('profesion_ocupacion_id'),
            
            # Datos de paciente
            historia_clinica=data['historia_clinica'],
            es_menor=data['es_menor'],
            observaciones=data.get('observaciones'),
            
            # Datos del menor
            nom_madre=data.get('nom_madre'),
            tel_madre=data.get('tel_madre'),
            nom_padre=data.get('nom_padre'),
            tel_padre=data.get('tel_padre'),
            educacion=data.get('educacion'),
            colegio=data.get('colegio'),
            tel_colegio=data.get('tel_colegio')
        )

        if resultado:
            return jsonify({
                'success': True,
                'data': {
                    'pac_id': pac_id,
                    'mensaje': 'Paciente actualizado exitosamente'
                },
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo actualizar el paciente.'
            }), 500

    except Exception as e:
        app.logger.error(f"Error al actualizar paciente: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Ocurrió un error interno: {str(e)}'
        }), 500


# ============================================
# ELIMINAR PACIENTE
# ============================================
@pacienteapi.route('/pacientes/<int:pac_id>', methods=['DELETE'])
def deletePaciente(pac_id):
    """Elimina un paciente y todos sus datos asociados"""
    pacientedao = PacienteDao()

    try:
        if pacientedao.deletePaciente(pac_id):
            return jsonify({
                'success': True,
                'mensaje': f'Paciente con ID {pac_id} eliminado correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró el paciente con el ID proporcionado o no se pudo eliminar.'
            }), 404

    except Exception as e:
        app.logger.error(f"Error al eliminar paciente: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500


# ============================================
# FILTRAR PACIENTES POR FECHA DE REGISTRO
# ============================================
@pacienteapi.route('/pacientes/filtro/fecha', methods=['GET'])
def getPacientesPorFecha():
    """Filtra pacientes por rango de fechas de registro"""
    pacientedao = PacienteDao()
    
    # Obtener parámetros de query string
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    try:
        pacientes = pacientedao.getPacientesPorFechaRegistro(fecha_inicio, fecha_fin)

        return jsonify({
            'success': True,
            'data': pacientes,
            'error': None
        }), 200

    except Exception as e:
        app.logger.error(f"Error al filtrar pacientes por fecha: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador.'
        }), 500