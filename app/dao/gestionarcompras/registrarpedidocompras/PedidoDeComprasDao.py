from flask import current_app as app
from app.conexion.Conexion import Conexion
from app.dao.gestionarcompras.registrarpedidocompras.dto import PedidoDeComprasDto

class PedidoDeComprasDao:
    
    # agregar
    def agregar(self, pedidoDto: PedidoDeComprasDto):
        insertPedidoCompraCabecera = """
        INSERT INTO public.pedido_de_compra
        (id_empleado, id_sucursal, id_epc, fecha_pedido, id_deposito)
        VALUES(%s, %s, %s, %s, %s)
        RETURNING id_pedido_compra
        """

        insertDetalleCompra = """
        INSERT INTO public.pedido_de_compra_detalle
        (id_pedido_compra, id_producto, cantidad)
        VALUES(%s, %s, %s)
        """

        # objeto conexion
        conexion = Conexion()
        con = conexion.getConexion()
        cur = con.cursor()
        try:
            parametros = ()
            cur.execute(insertPedidoCompraCabecera, parametros)

        except Exception as e:
            app.logger.error(f"Error a agregar un nuevo pedido: {str(e)}")
            return False
        finally:
            cur.close()
            con.close()

    # modificar
    def modificar(self):
        pass

    # anular
    def anular(self):
        pass