class PedidoDeComprasDto:
    
    def __init__(self, id, id_empleado, id_usuario, id_sucursal, \
        id_estado, fechapedido, id_deposito, pedidoDeCompraDetalleDto):
        self.id = id
        self.id_empleado = id_empleado
        self.id_usuario = id_usuario
        self.id_sucursal = id_sucursal
        self.id_estado = id_estado
        self.fechapedido = fechapedido
        self.id_deposito = id_deposito
        self.pedidoDeCompraDetalleDto = pedidoDeCompraDetalleDto