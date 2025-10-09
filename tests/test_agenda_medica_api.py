import unittest
from unittest.mock import Mock, patch
from flask import Flask
from app.rutas.modulos.agenda_medica.agenda_medica_api import agendaapi


class TestAgendaMedicaAPI(unittest.TestCase):
    
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(agendaapi, url_prefix='/api')
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    @patch('app.rutas.modulos.agenda_medica.agenda_medica_api.AgendaDao')
    def test_get_all_agendas_success(self, mock_dao):
        mock_instance = Mock()
        mock_instance.getAllAgendas.return_value = [{'id_agenda_horario': 1}]
        mock_dao.return_value = mock_instance
        
        response = self.client.get('/api/agenda')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
    
    @patch('app.rutas.modulos.agenda_medica.agenda_medica_api.AgendaDao')
    def test_get_agenda_by_id_not_found(self, mock_dao):
        mock_instance = Mock()
        mock_instance.getAgendaById.return_value = None
        mock_dao.return_value = mock_instance
        
        response = self.client.get('/api/agenda/999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data['success'])
    
    @patch('app.rutas.modulos.agenda_medica.agenda_medica_api.AgendaDao')
    def test_add_agenda_missing_fields(self, mock_dao):
        response = self.client.post('/api/agenda', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])


if __name__ == '__main__':
    unittest.main()
