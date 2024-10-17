from flask import Blueprint, request, jsonify, current_app as app
from app.dao.gestionar_compras.registrar_pedido_compras.pedido_de_compras_dao \
    import PedidoDeComprasDao

pdcapi = Blueprint('pdcapi', __name__)

@pdcapi.route('/pedidos', methods=['GET'])
def get_pedidos():
    dao = PedidoDeComprasDao()

    try:
        pedidos = dao.obtener_pedidos()
        return jsonify({
            'success': True,
            'data': pedidos,
            'error': False
        }), 200

    except Exception as e:
        app.logger.error(f"Error al obtener los pedidos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ocurrió un error interno. Consulte con el administrador'
        }), 500