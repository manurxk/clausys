from flask import Blueprint, request, jsonify, current_app as app, make_response
import io
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from app.dao.gestionar_personas.persona.PersonaDao import PersonaDao

personaapi = Blueprint('personaapi', __name__)

# --- Funciones para exportar ---

def export_pdf(data, columns, filename='personas.pdf'):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    table_data = [columns] + data
    table = Table(table_data)
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.gray),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])
    table.setStyle(style)
    doc.build([table])
    pdf = buffer.getvalue()
    buffer.close()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

def export_excel(data, columns, filename='personas.xlsx'):
    df = pd.DataFrame(data, columns=columns)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Personas')
    excel_data = buffer.getvalue()
    buffer.close()

    response = make_response(excel_data)
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

# --- Rutas ---

@personaapi.route('/personas', methods=['GET'])
def getPersonas():
    personadao = PersonaDao()
    try:
        personas = personadao.getPersonas()
        return jsonify({'success': True, 'data': personas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todas las personas: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500

@personaapi.route('/personas/<int:persona_id>', methods=['GET'])
def getPersona(persona_id):
    personadao = PersonaDao()
    try:
        persona = personadao.getPersonasById(persona_id)
        if persona:
            return jsonify({'success': True, 'data': persona, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró la persona con el ID proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener la persona: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500
    










@personaapi.route('/personas/matriculados', methods=['GET'])
def getPersonasMatriculados():
    personadao = PersonaDao()
    try:
        personas = personadao.getPersonasConMatricula()
        return jsonify({'success': True, 'data': personas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener personas matriculadas: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno.'}), 500

@personaapi.route('/personas/fecha_ingreso', methods=['GET'])
def getPersonasPorFechaIngreso():
    personadao = PersonaDao()
    fecha_inicio = request.args.get('fecha_inicio')  # formato: 'YYYY-MM-DD'
    fecha_fin = request.args.get('fecha_fin')

    try:
        personas = personadao.getPersonasPorFechaIngreso(fecha_inicio, fecha_fin)
        return jsonify({'success': True, 'data': personas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener personas por fecha ingreso: {str(e)}")
        return jsonify({'success': False, 'error': 'Error interno.'}), 500













@personaapi.route('/personas', methods=['POST'])
def addPersona():
    data = request.get_json()
    personadao = PersonaDao()

    campos_requeridos = ['nombre', 'apellido', 'cedula', 'fecha_nacimiento', 'id_genero', 'id_estado_civil', 'telefono_emergencia', 'id_ciudad']

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or (isinstance(data[campo], str) and len(data[campo].strip()) == 0):
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        nombre = data['nombre'].upper()
        apellido = data['apellido'].upper()
        cedula = data['cedula'].strip()
        fecha_nacimiento = data['fecha_nacimiento']
        id_genero = data['id_genero']
        id_estado_civil = data['id_estado_civil']
        telefono_emergencia = data['telefono_emergencia'].strip()
        id_ciudad = data['id_ciudad']
        fecha_registro = data.get('fecha_registro')  # opcional
        matricula = data.get('matricula')  # opcional

        persona_id = personadao.guardarPersona(
            nombre, apellido, cedula, fecha_nacimiento,
            id_genero, id_estado_civil, telefono_emergencia,
            id_ciudad, fecha_registro, matricula
        )

        if persona_id:
            return jsonify({
                'success': True,
                'data': {
                    'id': persona_id, 'nombre': nombre, 'apellido': apellido, 'cedula': cedula,
                    'fecha_nacimiento': fecha_nacimiento, 'id_genero': id_genero,
                    'id_estado_civil': id_estado_civil, 'telefono_emergencia': telefono_emergencia,
                    'id_ciudad': id_ciudad, 'fecha_registro': fecha_registro, 'matricula': matricula
                }, 'error': None
            }), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar la persona. Consulte con el administrador.'}), 500
    except Exception as e:
        app.logger.error(f"Error al agregar persona: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500

@personaapi.route('/personas/<int:persona_id>', methods=['PUT'])
def updatePersona(persona_id):
    data = request.get_json()
    personadao = PersonaDao()

    campos_requeridos = ['nombre', 'apellido', 'cedula', 'fecha_nacimiento', 'id_genero', 'id_estado_civil', 'telefono_emergencia', 'id_ciudad']

    for campo in campos_requeridos:
        if campo not in data or data[campo] is None or (isinstance(data[campo], str) and len(data[campo].strip()) == 0):
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        nombre = data['nombre'].upper()
        apellido = data['apellido'].upper()
        cedula = data['cedula'].strip()
        fecha_nacimiento = data['fecha_nacimiento']
        id_genero = data['id_genero']
        id_estado_civil = data['id_estado_civil']
        telefono_emergencia = data['telefono_emergencia'].strip()
        id_ciudad = data['id_ciudad']
        matricula = data.get('matricula')  # Aquí ya traemos la matrícula opcionalmente

        # Ahora pasamos la matrícula directamente al método updatePersona
        persona_actualizada = personadao.updatePersona(
            persona_id, nombre, apellido, cedula, fecha_nacimiento,
            id_genero, id_estado_civil, telefono_emergencia, id_ciudad, matricula
        )

        # Fecha de registro (paciente)
        fecha_registro = data.get('fecha_registro')
        if fecha_registro:
            personadao.updateFechaRegistroPaciente(persona_id, fecha_registro)

        if persona_actualizada:
            return jsonify({
                'success': True,
                'data': {
                    'id': persona_id,
                    'nombre': nombre,
                    'apellido': apellido,
                    'cedula': cedula,
                    'fecha_nacimiento': fecha_nacimiento,
                    'id_genero': id_genero,
                    'id_estado_civil': id_estado_civil,
                    'telefono_emergencia': telefono_emergencia,
                    'id_ciudad': id_ciudad,
                    'fecha_registro': fecha_registro,
                    'matricula': matricula
                },
                'error': None
            }), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró la persona con el ID proporcionado o no se pudo actualizar.'}), 404
    except Exception as e:
        app.logger.error(f"Error al actualizar persona: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500

@personaapi.route('/personas/<int:persona_id>', methods=['DELETE'])
def deletePersona(persona_id):
    personadao = PersonaDao()
    try:
        if personadao.deletePersona(persona_id):
            return jsonify({'success': True, 'mensaje': f'Persona con ID {persona_id} eliminada correctamente.', 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró la persona con el ID proporcionado o no se pudo eliminar.'}), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar persona: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500

# Opcionalmente puedes agregar rutas para exportar Excel y PDF si quieres usar export_excel y export_pdf
