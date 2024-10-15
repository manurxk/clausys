class PedidoDeCompraDetalleDto:
    
    def __init__(self, id_pedido_compra, id_producto, cantidad):
        self.__id_pedido_compra = id_pedido_compra
        self.__id_producto = id_producto
        self.__cantidad = cantidad

    #getters y setters de id_pedido_compra
    @property
    def id_pedido_compra(self):
        return self.__id_pedido_compra

    @id_pedido_compra.setter
    def id_pedido_compra(self, valor):
        if not valor:
            raise("El atributo id_pedido_compra no puede estar vacio")
        self.__id_pedido_compra = valor

    #getters y setters de id_producto
    @property
    def id_producto(self):
        return self.__id_producto

    @id_producto.setter
    def id_producto(self, valor):
        if not valor:
            raise("El atributo id_producto no puede estar vacio")
        self.__id_producto = valor

    #getters y setters de cantidad
    @property
    def cantidad(self):
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor):
        if not valor:
            raise("El atributo cantidad no puede estar vacio")
        self.__cantidad = valor