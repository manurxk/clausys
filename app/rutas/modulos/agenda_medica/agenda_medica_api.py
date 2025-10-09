from flask import Blueprint, request, jsonify, current_app as app
from app.dao.modulos.agenda_medica.Agenda_MedicaDao import AgendaDao

agendaapi = Blueprint('agendaapi', __name__)


@agendaapi.route('/agenda', methods=['GET'])
def getAllAgendas():
    """Obtiene la lista completa de agendas configuradas"""
    agendadao = AgendaDao()
    
    try:
        agendas = agendadao.getAllAgendas()
        return jsonify({'success': True, 'data': agendas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener todas las agendas: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@agendaapi.route('/agenda/<int:id_agenda_horario>', methods=['GET'])
def getAgenda(id_agenda_horario):
    """Obtiene una configuración de agenda específica por su ID"""
    agendadao = AgendaDao()
    
    try:
        agenda = agendadao.getAgendaById(id_agenda_horario)
        
        if agenda:
            return jsonify({'success': True, 'data': agenda, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró la agenda con el ID proporcionado.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener la agenda: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@agendaapi.route('/agenda/<int:id_agenda_horario>/editar', methods=['GET'])
def getAgendaParaEditar(id_agenda_horario):
    """Obtiene agenda con IDs originales para formulario de edición"""
    agendadao = AgendaDao()

    try:
        agenda = agendadao.getAgendaParaEditar(id_agenda_horario)

        if agenda:
            return jsonify({'success': True, 'data': agenda, 'error': None}), 200
        else:
            return jsonify({'success': False, 'error': 'No se encontró la agenda.'}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener agenda para editar: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@agendaapi.route('/agenda', methods=['POST'])
def addAgenda():
    """Crea una nueva configuración de agenda"""
    data = request.get_json()
    agendadao = AgendaDao()

    campos_requeridos = [
        'id_especialista', 'id_especialidad', 'id_consultorio', 
        'id_dia_semana', 'hora_inicio', 'hora_fin', 'duracion_turno'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        agenda_id = agendadao.guardarAgenda(
            id_especialista=data['id_especialista'],
            id_especialidad=data['id_especialidad'],
            id_consultorio=data['id_consultorio'],
            id_dia_semana=data['id_dia_semana'],
            hora_inicio=data['hora_inicio'],
            hora_fin=data['hora_fin'],
            duracion_turno=data['duracion_turno'],
            turno=data.get('turno', 'Mañana'),
            cupos_totales=data.get('cupos_totales', 10),
            fecha_desde=data.get('fecha_desde'),
            fecha_hasta=data.get('fecha_hasta'),
            creacion_usuario=data.get('creacion_usuario', 1)
        )

        if agenda_id is not None:
            return jsonify({
                'success': True,
                'data': {'id_agenda_horario': agenda_id, 'mensaje': 'Agenda creada exitosamente'},
                'error': None
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo guardar la agenda. El consultorio puede estar ocupado en ese horario.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al agregar agenda: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


@agendaapi.route('/agenda/<int:id_agenda_horario>', methods=['PUT'])
def updateAgenda(id_agenda_horario):
    """Actualiza una configuración de agenda existente"""
    data = request.get_json()
    agendadao = AgendaDao()

    agenda_existente = agendadao.getAgendaById(id_agenda_horario)
    if not agenda_existente:
        return jsonify({'success': False, 'error': 'No se encontró la agenda con el ID proporcionado.'}), 404

    campos_requeridos = [
        'id_especialidad', 'id_consultorio', 'id_dia_semana',
        'hora_inicio', 'hora_fin', 'duracion_turno', 'turno', 'cupos_totales'
    ]

    for campo in campos_requeridos:
        if campo not in data or not data[campo]:
            return jsonify({'success': False, 'error': f'El campo {campo} es obligatorio y no puede estar vacío.'}), 400

    try:
        resultado = agendadao.updateAgenda(
            id_agenda_horario=id_agenda_horario,
            id_especialidad=data['id_especialidad'],
            id_consultorio=data['id_consultorio'],
            id_dia_semana=data['id_dia_semana'],
            hora_inicio=data['hora_inicio'],
            hora_fin=data['hora_fin'],
            duracion_turno=data['duracion_turno'],
            turno=data['turno'],
            cupos_totales=data['cupos_totales'],
            fecha_desde=data.get('fecha_desde'),
            fecha_hasta=data.get('fecha_hasta'),
            activo=data.get('activo', True),
            modificacion_usuario=data.get('modificacion_usuario', 1)
        )

        if resultado:
            return jsonify({
                'success': True,
                'data': {'id_agenda_horario': id_agenda_horario, 'mensaje': 'Agenda actualizada exitosamente'},
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo actualizar la agenda. El consultorio puede estar ocupado en ese horario.'
            }), 500
    except Exception as e:
        app.logger.error(f"Error al actualizar agenda: {str(e)}")
        return jsonify({'success': False, 'error': f'Ocurrió un error interno: {str(e)}'}), 500


@agendaapi.route('/agenda/<int:id_agenda_horario>', methods=['DELETE'])
def deleteAgenda(id_agenda_horario):
    """Elimina lógicamente una configuración de agenda"""
    agendadao = AgendaDao()

    try:
        if agendadao.deleteAgenda(id_agenda_horario):
            return jsonify({
                'success': True,
                'mensaje': f'Agenda con ID {id_agenda_horario} eliminada correctamente.',
                'error': None
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se encontró la agenda con el ID proporcionado o no se pudo eliminar.'
            }), 404
    except Exception as e:
        app.logger.error(f"Error al eliminar agenda: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno. Consulte con el administrador.'}), 500


@agendaapi.route('/especialistas', methods=['GET'])
def getEspecialistas():
    """Obtiene lista de especialistas para modales"""
    agendadao = AgendaDao()
    
    try:
        especialistas = agendadao.getEspecialistas()
        return jsonify({'success': True, 'data': especialistas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener especialistas: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@agendaapi.route('/especialistas/<int:id_especialista>/especialidades', methods=['GET'])
def getEspecialidadesByEspecialista(id_especialista):
    """Obtiene las especialidades de un especialista específico"""
    agendadao = AgendaDao()
    
    try:
        especialidades = agendadao.getEspecialidadesByEspecialista(id_especialista)
        return jsonify({'success': True, 'data': especialidades, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener especialidades del especialista: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@agendaapi.route('/dias-semana', methods=['GET'])
def getDiasSemana():
    """Obtiene lista de días de la semana"""
    agendadao = AgendaDao()
    
    try:
        dias = agendadao.getDiasSemana()
        return jsonify({'success': True, 'data': dias, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener días de la semana: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@agendaapi.route('/consultorios', methods=['GET'])
def getConsultorios():
    """Obtiene lista de consultorios"""
    agendadao = AgendaDao()
    
    try:
        consultorios = agendadao.getConsultorios()
        return jsonify({'success': True, 'data': consultorios, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener consultorios: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@agendaapi.route('/agenda/especialista/<int:id_especialista>', methods=['GET'])
def getAgendasByEspecialista(id_especialista):
    """Obtiene todas las agendas de un especialista específico"""
    agendadao = AgendaDao()
    
    try:
        agendas = agendadao.getAgendasByEspecialista(id_especialista)
        return jsonify({'success': True, 'data': agendas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener agendas del especialista: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@agendaapi.route('/agenda/matriz-consultorios', methods=['GET'])
def getAgendaSemanalConsultorio():
    """Obtiene matriz semanal de uso de consultorios"""
    agendadao = AgendaDao()
    id_consultorio = request.args.get('id_consultorio', type=int)
    
    try:
        matriz = agendadao.getAgendaSemanalConsultorio(id_consultorio)
        return jsonify({'success': True, 'data': matriz, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener matriz semanal: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500


@agendaapi.route('/especialistas/con-agenda', methods=['GET'])
def getEspecialistasConAgenda():
    """Obtiene lista de especialistas que tienen agenda configurada"""
    agendadao = AgendaDao()
    
    try:
        especialistas = agendadao.getEspecialistasConAgenda()
        return jsonify({'success': True, 'data': especialistas, 'error': None}), 200
    except Exception as e:
        app.logger.error(f"Error al obtener especialistas con agenda: {str(e)}")
        return jsonify({'success': False, 'error': 'Ocurrió un error interno.'}), 500
