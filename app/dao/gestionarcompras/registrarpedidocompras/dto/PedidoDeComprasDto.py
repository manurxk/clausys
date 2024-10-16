from typing import List
from app.dao.gestionarcompras.registrarpedidocompras.dto.PedidoDeCompraDetalleDto import PedidoDeCompraDetalleDto

class PedidoDeComprasDto:
    
    def __init__(self, id_pedido_compra: int, id_empleado: int, id_sucursal: int, \
        id_epc: int, fecha_pedido, id_deposito: int, detallePedido: List[PedidoDeCompraDetalleDto]):
        self.id_pedido_compra = id_pedido_compra
        self.id_empleado = id_empleado
        self.id_sucursal = id_sucursal
        self.id_epc = id_epc
        self.fecha_pedido = fecha_pedido
        self.id_deposito = id_deposito
        self.detallePedido = detallePedido